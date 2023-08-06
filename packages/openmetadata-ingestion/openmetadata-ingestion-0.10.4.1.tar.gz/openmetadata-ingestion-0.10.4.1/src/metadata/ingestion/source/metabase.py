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
"""Metabase source module"""

import traceback
import uuid
from typing import Iterable
from urllib.parse import quote

import requests

from metadata.generated.schema.api.lineage.addLineage import AddLineageRequest
from metadata.generated.schema.entity.data.dashboard import Dashboard as Model_Dashboard
from metadata.generated.schema.entity.data.table import Table
from metadata.generated.schema.entity.services.connections.dashboard.metabaseConnection import (
    MetabaseConnection,
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
from metadata.ingestion.models.table_metadata import Chart, Dashboard
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.ingestion.source.sql_source import SQLSourceStatus
from metadata.utils.connections import get_connection, test_connection
from metadata.utils.filters import filter_by_chart, filter_by_dashboard
from metadata.utils.logger import ingestion_logger

HEADERS = {"Content-Type": "application/json", "Accept": "*/*"}

logger = ingestion_logger()


class MetabaseSource(Source[Entity]):
    """Metabase entity class

    Args:
        config:
        metadata_config:
    Attributes:
        config:
        metadata_config:
        status:
        metabase_session:
        dashboard_service:
        charts:
        metric_charts:
    """

    config: WorkflowSource
    metadata_config: OpenMetadataConnection
    status: SQLSourceStatus

    def __init__(
        self,
        config: WorkflowSource,
        metadata_config: OpenMetadataConnection,
    ):
        super().__init__()
        self.config = config
        self.service_connection = self.config.serviceConnection.__root__.config
        self.source_config: DashboardServiceMetadataPipeline = (
            self.config.sourceConfig.config
        )
        self.metadata_config = metadata_config
        self.metadata = OpenMetadata(metadata_config)

        self.status = SQLSourceStatus()
        params = dict()
        params["username"] = self.service_connection.username
        params["password"] = self.service_connection.password.get_secret_value()

        self.connection = get_connection(self.service_connection)
        self.metabase_session = self.connection.client["metabase_session"]

        self.dashboard_service = self.metadata.get_service_or_create(
            entity=DashboardService, config=config
        )
        self.charts = []
        self.metric_charts = []

    @classmethod
    def create(cls, config_dict, metadata_config: OpenMetadataConnection):
        """Instantiate object

        Args:
            config_dict:
            metadata_config:
        Returns:
            MetabaseSource
        """
        config = WorkflowSource.parse_obj(config_dict)
        connection: MetabaseConnection = config.serviceConnection.__root__.config
        if not isinstance(connection, MetabaseConnection):
            raise InvalidSourceException(
                f"Expected MetabaseConnection, but got {connection}"
            )
        return cls(config, metadata_config)

    def next_record(self) -> Iterable[Entity]:
        yield from self.get_dashboards()
        self.get_cards()

    def get_charts(self, charts) -> Iterable[Chart]:
        """Get chart method

        Args:
            charts:
        Returns:
            Iterable[Chart]
        """
        for chart in charts:
            try:
                chart_details = chart["card"]
                if not ("name" in chart_details):
                    continue
                if filter_by_chart(
                    self.source_config.chartFilterPattern, chart_details["name"]
                ):
                    self.status.filter(
                        chart_details["name"], "Chart Pattern not allowed"
                    )
                    continue
                yield Chart(
                    id=uuid.uuid4(),
                    name=chart_details["name"],
                    displayName=chart_details["name"],
                    description=chart_details["description"]
                    if chart_details["description"] is not None
                    else "",
                    chart_type=str(chart_details["display"]),
                    url=self.service_connection.hostPort,
                    service=EntityReference(
                        id=self.dashboard_service.id, type="dashboardService"
                    ),
                )
                self.charts.append(chart_details["name"])
                self.status.scanned(chart_details["name"])
            except Exception as err:  # pylint: disable=broad-except
                logger.error(repr(err))
                logger.debug(traceback.format_exc())
                continue

    def get_dashboards(self):
        """Get dashboard method"""
        resp_dashboards = self.req_get("/api/dashboard")
        if resp_dashboards.status_code == 200:
            for dashboard in resp_dashboards.json():
                resp_dashboard = self.req_get(f"/api/dashboard/{dashboard['id']}")
                dashboard_details = resp_dashboard.json()
                self.charts = []
                if filter_by_dashboard(
                    self.source_config.dashboardFilterPattern, dashboard_details["name"]
                ):
                    self.status.filter(
                        dashboard_details["name"], "Dashboard Pattern not Allowed"
                    )
                    continue
                yield from self.get_charts(dashboard_details["ordered_cards"])
                yield Dashboard(
                    id=uuid.uuid4(),
                    name=dashboard_details["name"],
                    url=self.service_connection.hostPort,
                    displayName=dashboard_details["name"],
                    description=dashboard_details["description"]
                    if dashboard_details["description"] is not None
                    else "",
                    charts=self.charts,
                    service=EntityReference(
                        id=self.dashboard_service.id, type="dashboardService"
                    ),
                )
                if self.service_connection.dbServiceName:
                    yield from self.get_lineage(
                        dashboard_details["ordered_cards"], dashboard_details["name"]
                    )

    def get_lineage(self, chart_list, dashboard_name):
        """Get lineage method

        Args:
            chart_list:
            dashboard_name
        """
        metadata = OpenMetadata(self.metadata_config)
        for chart in chart_list:
            try:
                chart_details = chart["card"]
                if not chart_details.get("table_id"):
                    continue
                resp_tables = self.req_get(f"/api/table/{chart_details['table_id']}")
                if resp_tables.status_code == 200:
                    table = resp_tables.json()
                    table_fqdn = f"{self.service_connection.dbServiceName}.{table['schema']}.{table['name']}"
                    dashboard_fqdn = (
                        f"{self.dashboard_service.name}.{quote(dashboard_name)}"
                    )
                    table_entity = metadata.get_by_name(entity=Table, fqdn=table_fqdn)
                    chart_entity = metadata.get_by_name(
                        entity=Model_Dashboard, fqdn=dashboard_fqdn
                    )
                    logger.debug("from entity %s", table_entity)
                    if table_entity and chart_entity:
                        lineage = AddLineageRequest(
                            edge=EntitiesEdge(
                                fromEntity=EntityReference(
                                    id=table_entity.id.__root__, type="table"
                                ),
                                toEntity=EntityReference(
                                    id=chart_entity.id.__root__, type="dashboard"
                                ),
                            )
                        )
                        yield lineage
            except Exception as err:  # pylint: disable=broad-except,unused-variable
                logger.error(traceback.format_exc())

    def req_get(self, path):
        """Send get request method

        Args:
            path:
        """
        return requests.get(
            self.service_connection.hostPort + path, headers=self.metabase_session
        )

    def get_status(self) -> SourceStatus:
        return self.status

    def close(self):
        pass

    def prepare(self):
        pass

    def test_connection(self) -> None:
        pass

    def get_card_detail(self, card_list):
        metadata = OpenMetadata(self.metadata_config)
        for card in card_list:
            try:
                card_details = card["card"]
                if not card_details.get("id"):
                    continue
                card_detail_resp = self.req_get(f"/api/card/{card_details['id']}")
                if card_detail_resp.status_code == 200:
                    raw_query = (
                        card_details.get("dataset_query", {})
                        .get("native", {})
                        .get("query", "")
                    )
            except Exception as e:
                logger.error(repr(e))

    def get_cards(self):
        """Get cards method"""
        resp_dashboards = self.req_get("/api/dashboard")
        if resp_dashboards.status_code == 200:
            for dashboard in resp_dashboards.json():
                resp_dashboard = self.req_get(f"/api/dashboard/{dashboard['id']}")
                dashboard_details = resp_dashboard.json()
                card_list = dashboard_details["ordered_cards"]
                self.get_card_detail(card_list)
