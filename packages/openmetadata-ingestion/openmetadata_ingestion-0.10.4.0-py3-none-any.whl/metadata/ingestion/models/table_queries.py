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

from typing import Dict, List, Optional

from pydantic import BaseModel

from metadata.generated.schema.entity.data.table import ColumnJoins, SqlQuery
from metadata.ingestion.models.json_serializable import JsonSerializable


class TableQuery(JsonSerializable):
    """ """

    def __init__(
        self,
        query: str,
        user_name: str,
        starttime: str,
        endtime: str,
        analysis_date: str,
        database: Optional[str],
        aborted: bool,
        sql: str,
        service_name: str,
        schema_name: Optional[str] = None,
    ) -> None:
        """ """
        self.query = query
        self.user_name = user_name
        self.starttime = starttime
        self.endtime = endtime
        self.analysis_date = analysis_date
        self.database = database
        self.schema_name = schema_name
        self.aborted = aborted
        self.sql = sql
        self.service_name = service_name


class TableColumn(BaseModel):
    table: str
    column: str


class TableColumnJoin(BaseModel):
    table_column: Optional[TableColumn] = None
    joined_with: Optional[List[TableColumn]] = None


TableColumnJoins = List[TableColumnJoin]


class TableUsageCount(BaseModel):
    table: str
    date: str
    database: str
    schema_name: Optional[str] = None
    sql_queries: List[SqlQuery]
    count: int = 1
    joins: TableColumnJoins
    service_name: str


class QueryParserData(BaseModel):
    tables: List[str]
    joins: Dict[str, List[TableColumnJoin]]
    date: str
    database: str
    schema_name: Optional[str] = None
    sql: str
    service_name: str

    class Config:
        arbitrary_types_allowed = True


class TableUsageRequest(BaseModel):
    date: str
    count: int


class ColumnJoinsList(BaseModel):
    __root__: List[ColumnJoins]


class ColumnJoinedWith(BaseModel):
    fullyQualifiedName: str
    joinCount: int


TablesUsage = List[TableUsageCount]
