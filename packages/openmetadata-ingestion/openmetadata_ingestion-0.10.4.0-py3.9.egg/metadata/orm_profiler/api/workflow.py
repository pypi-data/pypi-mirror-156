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
Workflow definition for the ORM Profiler.

- How to specify the source
- How to specify the entities to run
- How to define metrics & tests
"""
import itertools
from typing import Iterable, List

import click
from pydantic import ValidationError

from metadata.config.common import WorkflowExecutionError
from metadata.config.workflow import get_processor, get_sink
from metadata.generated.schema.entity.data.database import Database
from metadata.generated.schema.entity.data.table import Table
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
)
from metadata.generated.schema.metadataIngestion.databaseServiceProfilerPipeline import (
    DatabaseServiceProfilerPipeline,
)
from metadata.generated.schema.metadataIngestion.workflow import (
    OpenMetadataWorkflowConfig,
)
from metadata.ingestion.api.processor import Processor
from metadata.ingestion.api.sink import Sink
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.ingestion.source.sql_source import SQLSourceStatus
from metadata.orm_profiler.api.models import ProfilerProcessorConfig, ProfilerResponse
from metadata.utils.connections import (
    create_and_bind_session,
    get_connection,
    test_connection,
)
from metadata.utils.filters import filter_by_fqn
from metadata.utils.logger import profiler_logger

logger = profiler_logger()


class ProfilerWorkflow:
    """
    Configure and run the ORM profiler
    """

    config: OpenMetadataWorkflowConfig
    processor: Processor
    sink: Sink
    metadata: OpenMetadata

    def __init__(self, config: OpenMetadataWorkflowConfig):
        self.config = config
        self.metadata_config: OpenMetadataConnection = (
            self.config.workflowConfig.openMetadataServerConfig
        )

        # Prepare the connection to the source service
        # We don't need the whole Source class, as it is the OM Server
        engine = get_connection(self.config.source.serviceConnection.__root__.config)
        test_connection(engine)

        # Init and type the source config
        self.source_config: DatabaseServiceProfilerPipeline = (
            self.config.source.sourceConfig.config
        )
        self.source_status = SQLSourceStatus()

        self.processor = get_processor(
            processor_type=self.config.processor.type,  # orm-profiler
            processor_config=self.config.processor or ProfilerProcessorConfig(),
            metadata_config=self.metadata_config,
            _from="orm_profiler",
            # Pass the session as kwargs for the profiler
            session=create_and_bind_session(engine),
        )

        if self.config.sink:
            self.sink = get_sink(
                sink_type=self.config.sink.type,
                sink_config=self.config.sink,
                metadata_config=self.metadata_config,
                _from="orm_profiler",
            )

        # OpenMetadata client to fetch tables
        self.metadata = OpenMetadata(self.metadata_config)

    @classmethod
    def create(cls, config_dict: dict) -> "ProfilerWorkflow":
        """
        Parse a JSON (dict) and create the workflow
        """
        try:
            config = OpenMetadataWorkflowConfig.parse_obj(config_dict)
            return cls(config)
        except ValidationError as err:
            logger.error("Error trying to parse the Profiler Workflow configuration")
            raise err

    def filter_entities(self, tables: List[Table]) -> Iterable[Table]:
        """
        From a list of tables, apply the SQLSourceConfig
        filter patterns.

        We will update the status on the SQLSource Status.
        """
        for table in tables:

            if filter_by_fqn(
                fqn_filter_pattern=self.source_config.fqnFilterPattern,
                fqn=table.fullyQualifiedName.__root__,
            ):
                self.source_status.filter(
                    table.fullyQualifiedName.__root__, "Schema pattern not allowed"
                )
                continue

            self.source_status.scanned(table.fullyQualifiedName.__root__)
            yield table

    def list_entities(self) -> Iterable[Table]:
        """
        List and filter OpenMetadata tables based on the
        source configuration.

        The listing will be based on the entities from the
        informed service name in the source configuration.

        Note that users can specify `table_filter_pattern` to
        either be `includes` or `excludes`. This means
        that we will either what is specified in `includes`
        or we will use everything but the tables excluded.

        Same with `schema_filter_pattern`.
        """

        # First, get all the databases for the service:
        all_dbs = self.metadata.list_entities(
            entity=Database,
            params={"service": self.config.source.serviceName},
        )

        # Then list all tables from each db.
        # This returns a nested structure [[db1 tables], [db2 tables]...]
        all_tables = [
            self.metadata.list_entities(
                entity=Table,
                fields=[
                    "tableProfile",
                    "tests",
                ],  # We will need it for window metrics to check past data
                params={
                    "database": f"{self.config.source.serviceName}.{database.name.__root__}"
                },
            ).entities
            for database in all_dbs.entities
        ]

        # Flatten the structure into a List[Table]
        flat_tables = list(itertools.chain.from_iterable(all_tables))

        yield from self.filter_entities(flat_tables)

    def execute(self):
        """
        Run the profiling and tests
        """
        for entity in self.list_entities():
            profile_and_tests: ProfilerResponse = self.processor.process(entity)

            if hasattr(self, "sink"):
                self.sink.write_record(profile_and_tests)

    def print_status(self) -> int:
        click.echo()
        click.secho("Source Status:", bold=True)
        click.echo(self.source_status.as_string())
        click.secho("Processor Status:", bold=True)
        click.echo(self.processor.get_status().as_string())
        if hasattr(self, "sink"):
            click.secho("Sink Status:", bold=True)
            click.echo(self.sink.get_status().as_string())
            click.echo()

        if (
            self.source_status.failures
            or self.processor.get_status().failures
            or (hasattr(self, "sink") and self.sink.get_status().failures)
        ):
            click.secho("Workflow finished with failures", fg="bright_red", bold=True)
            return 1
        elif (
            self.source_status.warnings
            or self.processor.get_status().failures
            or (hasattr(self, "sink") and self.sink.get_status().warnings)
        ):
            click.secho("Workflow finished with warnings", fg="yellow", bold=True)
            return 0
        else:
            click.secho("Workflow finished successfully", fg="green", bold=True)
            return 0

    def raise_from_status(self, raise_warnings=False):
        """
        Check source, processor and sink status and raise if needed

        Our profiler source will never log any failure, only filters,
        as we are just picking up data from OM.
        """

        if self.processor.get_status().failures:
            raise WorkflowExecutionError(
                "Processor reported errors", self.processor.get_status()
            )
        if hasattr(self, "sink") and self.sink.get_status().failures:
            raise WorkflowExecutionError("Sink reported errors", self.sink.get_status())

        if raise_warnings:
            if self.source_status.warnings:
                raise WorkflowExecutionError(
                    "Source reported warnings", self.source_status
                )
            if self.processor.get_status().warnings:
                raise WorkflowExecutionError(
                    "Processor reported warnings", self.processor.get_status()
                )
            if hasattr(self, "sink") and self.sink.get_status().warnings:
                raise WorkflowExecutionError(
                    "Sink reported warnings", self.sink.get_status()
                )

    def stop(self):
        """
        Close all connections
        """
        self.metadata.close()
