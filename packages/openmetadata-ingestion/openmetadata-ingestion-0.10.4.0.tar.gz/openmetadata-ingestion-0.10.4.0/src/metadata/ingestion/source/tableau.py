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
"""
Tableau source module
"""
import traceback
import uuid
from typing import Iterable, List

import dateutil.parser as dateparser
from tableau_api_lib import TableauServerConnection
from tableau_api_lib.utils.querying import (
    get_views_dataframe,
    get_workbook_connections_dataframe,
    get_workbooks_dataframe,
)

from metadata.config.common import FQDN_SEPARATOR
from metadata.generated.schema.api.lineage.addLineage import AddLineageRequest
from metadata.generated.schema.entity.data.dashboard import (
    Dashboard as Dashboard_Entity,
)
from metadata.generated.schema.entity.data.table import Table
from metadata.generated.schema.entity.services.connections.dashboard.tableauConnection import (
    TableauConnection,
)
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
)
from metadata.generated.schema.entity.services.dashboardService import DashboardService
from metadata.generated.schema.metadataIngestion.dashboardServiceMetadataPipeline import (
    DashboardServiceMetadataPipeline,
)
from metadata.generated.schema.metadataIngestion.workflow import (
    Source as WorkflowSource,
)
from metadata.generated.schema.type.entityLineage import EntitiesEdge
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.ingestion.api.common import Entity
from metadata.ingestion.api.source import InvalidSourceException, Source, SourceStatus
from metadata.ingestion.models.table_metadata import Chart, Dashboard, DashboardOwner
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.utils.connections import get_connection, test_connection
from metadata.utils.filters import filter_by_chart, filter_by_dashboard
from metadata.utils.logger import ingestion_logger

logger = ingestion_logger()


class TableauSource(Source[Entity]):
    """Tableau source entity class

    Args:
        config:
        metadata_config:

    Attributes:
        config:
        metadata_config:
        status:
        service:
        dashboard:
        all_dashboard_details:
    """

    config: WorkflowSource
    metadata_config: OpenMetadataConnection
    status: SourceStatus

    def __init__(
        self,
        config: WorkflowSource,
        metadata_config: OpenMetadataConnection,
    ):
        super().__init__()
        self.config = config
        self.metadata_config = metadata_config
        self.metadata = OpenMetadata(metadata_config)
        self.connection_config = self.config.serviceConnection.__root__.config
        self.source_config: DashboardServiceMetadataPipeline = (
            self.config.sourceConfig.config
        )

        self.connection = get_connection(self.connection_config)
        self.client = self.connection.client
        self.service = self.metadata.get_service_or_create(
            entity=DashboardService, config=config
        )
        self.status = SourceStatus()
        self.metadata_client = OpenMetadata(self.metadata_config)
        self.dashboards = get_workbooks_dataframe(self.client).to_dict()
        self.all_dashboard_details = get_views_dataframe(self.client).to_dict()

    @classmethod
    def create(cls, config_dict: dict, metadata_config: OpenMetadataConnection):
        config: WorkflowSource = WorkflowSource.parse_obj(config_dict)
        connection: TableauConnection = config.serviceConnection.__root__.config
        if not isinstance(connection, TableauConnection):
            raise InvalidSourceException(
                f"Expected TableauConnection, but got {connection}"
            )
        return cls(config, metadata_config)

    def prepare(self):
        pass

    def next_record(self) -> Iterable[Entity]:
        yield from self._get_tableau_charts()
        yield from self._get_tableau_dashboard()

    @staticmethod
    def get_owner(owner) -> List[DashboardOwner]:
        """Get dashboard owner

        Args:
            owner:
        Returns:
            List[DashboardOwner]
        """
        parts = owner["fullName"].split(" ")
        first_name = " ".join(parts[: len(owner) // 2])
        last_name = " ".join(parts[len(owner) // 2 :])
        return [
            DashboardOwner(
                first_name=first_name,
                last_name=last_name,
                username=owner["name"],
            )
        ]

    def get_lineage(self, datasource_list, dashboard_name) -> AddLineageRequest:
        for datasource in datasource_list:
            try:
                table_fqdn = datasource.split("(")[1].split(")")[0]
                dashboard_fqdn = f"{self.config.serviceName}.{dashboard_name}"
                table_fqdn = f"{self.connection_config.dbServiceName}.{table_fqdn}"
                table_entity = self.metadata_client.get_by_name(
                    entity=Table, fqdn=table_fqdn
                )
                dashboard_entity = self.metadata_client.get_by_name(
                    entity=Dashboard_Entity, fqdn=dashboard_fqdn
                )
                if table_entity and dashboard_entity:
                    lineage = AddLineageRequest(
                        edge=EntitiesEdge(
                            fromEntity=EntityReference(
                                id=table_entity.id.__root__, type="table"
                            ),
                            toEntity=EntityReference(
                                id=dashboard_entity.id.__root__, type="dashboard"
                            ),
                        )
                    )
                    yield lineage
            except (Exception, IndexError) as err:
                logger.debug(traceback.format_exc())
                logger.error(err)

    def _get_tableau_dashboard(self) -> Dashboard:
        for index in range(len(self.dashboards["id"])):
            try:
                dashboard_id = self.dashboards["id"][index]
                dashboard_name = self.dashboards["name"][index]
                if filter_by_dashboard(
                    self.source_config.dashboardFilterPattern, dashboard_name
                ):
                    self.status.failure(dashboard_name, "Dashboard Pattern not allowed")
                    continue
                dashboard_tag = self.dashboards["tags"][index]
                dashboard_url = self.dashboards["webpageUrl"][index]
                datasource_list = (
                    get_workbook_connections_dataframe(self.client, dashboard_id)
                    .get("datasource_name")
                    .tolist()
                )
                tag_labels = []
                if hasattr(dashboard_tag, "tag"):
                    for tag in dashboard_tag["tag"]:
                        tag_labels.append(tag["label"])
                dashboard_chart = []
                for chart_index in self.all_dashboard_details["workbook"]:
                    dashboard_owner = self.all_dashboard_details["owner"][chart_index]
                    chart = self.all_dashboard_details["workbook"][chart_index]
                    if chart["id"] == dashboard_id:
                        dashboard_chart.append(
                            self.all_dashboard_details["id"][chart_index]
                        )
                yield Dashboard(
                    id=uuid.uuid4(),
                    name=dashboard_id,
                    displayName=dashboard_name,
                    description="",
                    owner=self.get_owner(dashboard_owner),
                    charts=dashboard_chart,
                    tags=list(tag_labels),
                    url=dashboard_url,
                    service=EntityReference(
                        id=self.service.id, type="dashboardService"
                    ),
                    last_modified=dateparser.parse(chart["updatedAt"]).timestamp()
                    * 1000,
                )
                if self.connection_config.dbServiceName:
                    yield from self.get_lineage(datasource_list, dashboard_id)
            except Exception as err:
                logger.debug(traceback.format_exc())
                logger.error(err)

    def _get_tableau_charts(self):
        for index in range(len(self.all_dashboard_details["id"])):
            try:
                chart_name = self.all_dashboard_details["name"][index]
                if filter_by_chart(self.source_config.chartFilterPattern, chart_name):
                    self.status.failure(chart_name, "Chart Pattern not allowed")
                    continue
                chart_id = self.all_dashboard_details["id"][index]
                chart_tags = self.all_dashboard_details["tags"][index]
                chart_type = self.all_dashboard_details["sheetType"][index]
                chart_url = (
                    f"{self.connection_config.hostPort}/#/site/{self.connection_config.siteName}"
                    f"{self.all_dashboard_details['contentUrl'][index]}"
                )
                chart_owner = self.all_dashboard_details["owner"][index]
                chart_datasource_fqn = chart_url.replace("/", FQDN_SEPARATOR)
                chart_last_modified = self.all_dashboard_details["updatedAt"][index]
                tag_labels = []
                if hasattr(chart_tags, "tag"):
                    for tag in chart_tags["tag"]:
                        tag_labels.append(tag["label"])
                yield Chart(
                    name=chart_id,
                    displayName=chart_name,
                    description="",
                    chart_type=chart_type,
                    url=chart_url,
                    owners=self.get_owner(chart_owner),
                    datasource_fqn=chart_datasource_fqn,
                    last_modified=dateparser.parse(chart_last_modified).timestamp()
                    * 1000,
                    service=EntityReference(
                        id=self.service.id, type="dashboardService"
                    ),
                )
            except Exception as err:
                logger.debug(traceback.format_exc())
                logger.error(err)

    def get_status(self) -> SourceStatus:
        return self.status

    def close(self):
        pass

    def test_connection(self) -> None:
        pass
