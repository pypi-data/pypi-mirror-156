#  Copyright 2021 Collate
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import json
from datetime import datetime

from metadata.config.common import ConfigModel
from metadata.generated.schema.entity.data.database import Database
from metadata.generated.schema.entity.data.table import ColumnJoins, Table, TableJoins
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
)
from metadata.ingestion.api.bulk_sink import BulkSink, BulkSinkStatus
from metadata.ingestion.models.table_queries import (
    ColumnJoinedWith,
    TableColumn,
    TableUsageCount,
    TableUsageRequest,
)
from metadata.ingestion.ometa.client import APIError
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.utils.fqdn_generator import get_fqdn
from metadata.utils.helpers import _get_formmated_table_name
from metadata.utils.logger import ingestion_logger

logger = ingestion_logger()


class MetadataUsageSinkConfig(ConfigModel):
    filename: str


class MetadataUsageBulkSink(BulkSink):
    config: MetadataUsageSinkConfig

    def __init__(
        self,
        config: MetadataUsageSinkConfig,
        metadata_config: OpenMetadataConnection,
    ):

        self.config = config
        self.metadata_config = metadata_config
        self.service_name = None
        self.wrote_something = False
        self.file_handler = open(self.config.filename, "r")
        self.metadata = OpenMetadata(self.metadata_config)
        self.status = BulkSinkStatus()
        self.table_join_dict = {}
        self.today = datetime.today().strftime("%Y-%m-%d")

    @classmethod
    def create(cls, config_dict: dict, metadata_config: OpenMetadataConnection):
        config = MetadataUsageSinkConfig.parse_obj(config_dict)
        return cls(config, metadata_config)

    def handle_work_unit_start(self, wu):
        pass

    def handle_work_unit_end(self, wu):
        pass

    def ingest_sql_queries_lineage(self, queries, database, schema_name):
        for query in queries:
            self.metadata.ingest_lineage_by_query(
                query=query.query,
                service_name=self.service_name,
                database_name=database,
                schema_name=schema_name,
            )

    def write_records(self) -> None:
        usage_records = [json.loads(l) for l in self.file_handler.readlines()]
        table_usage_map = {}
        for record in usage_records:
            table_usage = TableUsageCount(**json.loads(record))

            self.service_name = table_usage.service_name

            table_entities = self.metadata.get_table_entities_from_query(
                self.service_name,
                table_usage.database,
                table_usage.schema_name,
                table_usage.table,
            )

            if not table_entities:
                logger.warning(
                    f"Could not fetch table from {table_usage.database}.{table_usage.schema_name}.{table_usage.table}"
                )
                continue

            for table_entity in table_entities:
                if table_entity is not None:
                    if not table_usage_map.get(table_entity.id.__root__):
                        table_usage_map[table_entity.id.__root__] = {
                            "table_entity": table_entity,
                            "usage_count": table_usage.count,
                            "sql_queries": table_usage.sql_queries,
                            "usage_date": table_usage.date,
                            "database": table_usage.database,
                            "schema_name": table_usage.schema_name,
                        }
                    else:
                        table_usage_map[table_entity.id.__root__][
                            "usage_count"
                        ] += table_usage.count
                        table_usage_map[table_entity.id.__root__]["sql_queries"].extend(
                            table_usage.sql_queries
                        )
                    table_join_request = self.__get_table_joins(
                        table_entity, table_usage
                    )

                    logger.debug("table join request {}".format(table_join_request))
                    try:
                        if (
                            table_join_request is not None
                            and len(table_join_request.columnJoins) > 0
                        ):
                            self.metadata.publish_frequently_joined_with(
                                table_entity, table_join_request
                            )
                    except APIError as err:
                        self.status.failures.append(table_join_request)
                        logger.error(
                            "Failed to update query join for {}, {}".format(
                                table_usage.table, err
                            )
                        )

                else:
                    logger.warning(
                        "Table does not exist, skipping usage publish {}, {}".format(
                            table_usage.table, table_usage.database
                        )
                    )
                    self.status.warnings.append(f"Table: {table_usage.table}")

        for table_id, value_dict in table_usage_map.items():
            self.metadata.ingest_table_queries_data(
                table=value_dict["table_entity"],
                table_queries=value_dict["sql_queries"],
            )
            self.ingest_sql_queries_lineage(
                value_dict["sql_queries"],
                value_dict["database"],
                value_dict["schema_name"],
            )
            table_usage_request = TableUsageRequest(
                date=value_dict["usage_date"], count=value_dict["usage_count"]
            )
            try:
                self.metadata.publish_table_usage(
                    value_dict["table_entity"], table_usage_request
                )
                logger.info(
                    "Successfully table usage published for {}".format(
                        value_dict["table_entity"].name.__root__
                    )
                )
                self.status.records_written(
                    "Table: {}".format(value_dict["table_entity"].name.__root__)
                )
            except Exception as err:
                self.status.failures.append(table_usage_request)
                logger.error(
                    "Failed to update usage for {} {}".format(
                        value_dict["table_entity"].name.__root__, err
                    )
                )
                self.status.failures.append(
                    "Table: {}".format(value_dict["table_entity"].name.__root__)
                )
        try:
            self.metadata.compute_percentile(Table, self.today)
            self.metadata.compute_percentile(Database, self.today)
        except APIError:
            logger.error("Failed to publish compute.percentile")

    def __get_table_joins(self, table_entity: Table, table_usage: TableUsageCount):
        table_joins: TableJoins = TableJoins(columnJoins=[], startDate=table_usage.date)
        column_joins_dict = {}
        for column_join in table_usage.joins:
            joined_with = {}
            if column_join.table_column is None or len(column_join.joined_with) == 0:
                continue
            if column_join.table_column.column in column_joins_dict.keys():
                joined_with = column_joins_dict[column_join.table_column.column]
            else:
                column_joins_dict[column_join.table_column.column] = {}
            for column in column_join.joined_with:
                joined_column_fqdn = self.__get_column_fqdn(
                    table_usage.database, table_usage.schema_name, column
                )

                if str(joined_column_fqdn) in joined_with.keys():
                    column_joined_with = joined_with[str(joined_column_fqdn)]
                    column_joined_with.joinCount += 1
                    joined_with[str(joined_column_fqdn)] = column_joined_with
                elif joined_column_fqdn is not None:
                    joined_with[str(joined_column_fqdn)] = ColumnJoinedWith(
                        fullyQualifiedName=str(joined_column_fqdn), joinCount=1
                    )
                else:
                    logger.info(
                        f"Skipping join columns for {column} {joined_column_fqdn}"
                    )
            column_joins_dict[column_join.table_column.column] = joined_with

        for key, value in column_joins_dict.items():
            # Fetch real key (column) name from the Entity
            key_name = self.__fetch_column_in_entity(key, table_entity).split(".")[-1]
            table_joins.columnJoins.append(
                ColumnJoins(columnName=key_name, joinedWith=list(value.values()))
            )

        return table_joins

    def __get_column_fqdn(
        self, database: str, database_schema: str, table_column: TableColumn
    ):
        table_entities = self.metadata.get_table_entities_from_query(
            self.service_name, database, database_schema, table_column.table
        )
        if not table_entities:
            return None
        for table_entity in table_entities:
            return self.__fetch_column_in_entity(table_column.column, table_entity)

    @staticmethod
    def __fetch_column_in_entity(column: str, table: Table) -> str:
        """
        Find the column in the table that matches the incoming name
        """
        for tbl_column in table.columns:
            if column.lower() == tbl_column.name.__root__.lower():
                return tbl_column.fullyQualifiedName.__root__.__root__

    def get_status(self):
        return self.status

    def close(self):
        self.file_handler.close()
        self.metadata.close()
