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
import pathlib

from metadata.generated.schema.entity.data.table import SqlQuery
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
)
from metadata.ingestion.api.stage import Stage, StageStatus
from metadata.ingestion.models.table_queries import QueryParserData, TableUsageCount
from metadata.ingestion.stage.file import FileStageConfig
from metadata.utils.logger import ingestion_logger

logger = ingestion_logger()


class TableUsageStage(Stage[QueryParserData]):
    config: FileStageConfig
    status: StageStatus

    def __init__(
        self,
        config: FileStageConfig,
        metadata_config: OpenMetadataConnection,
    ):

        self.config = config
        self.metadata_config = metadata_config
        self.status = StageStatus()
        self.table_usage = {}
        self.table_queries = {}
        fpath = pathlib.Path(self.config.filename)
        self.file = fpath.open("w")
        self.wrote_something = False

    @classmethod
    def create(cls, config_dict: dict, metadata_config: OpenMetadataConnection):
        config = FileStageConfig.parse_obj(config_dict)
        return cls(config, metadata_config)

    def _add_sql_query(self, record, table):
        if self.table_queries.get(table):
            self.table_queries[table].append(SqlQuery(query=record.sql))
        else:
            self.table_queries[table] = [SqlQuery(query=record.sql)]

    def stage_record(self, record: QueryParserData) -> None:
        if record is None:
            return None
        for table in record.tables:
            table_joins = record.joins.get(table)
            try:
                self._add_sql_query(record=record, table=table)
                table_usage_count = self.table_usage.get(table)
                if table_usage_count is not None:
                    table_usage_count.count = table_usage_count.count + 1
                    if table_joins:
                        table_usage_count.joins.extend(table_joins)
                else:
                    joins = []
                    if table_joins:
                        joins.extend(table_joins)

                    table_usage_count = TableUsageCount(
                        table=table,
                        database=record.database,
                        schema_name=record.schema_name,
                        date=record.date,
                        joins=joins,
                        service_name=record.service_name,
                        sql_queries=[],
                    )

            except Exception as exc:
                logger.error("Error in staging record {}".format(exc))
            self.table_usage[table] = table_usage_count
            logger.info(f"Successfully record staged for {table}")

    def get_status(self):
        return self.status

    def close(self):
        for key, value in self.table_usage.items():
            value.sql_queries = self.table_queries.get(key, [])
            data = value.json()
            self.file.write(json.dumps(data))
            self.file.write("\n")
        self.file.close()
