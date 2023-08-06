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
Mixin class containing Glossary Term specific methods

To be used be OpenMetadata
"""
from typing import Type, TypeVar

from pydantic import BaseModel

from metadata.ingestion.ometa.utils import ometa_logger

T = TypeVar("T", bound=BaseModel)  # pylint: disable=invalid-name
logger = ometa_logger()


class GlossaryTermMixin:
    def create_glossary_term(self, entity: Type[T], glossary_term_body):
        """Method to create new Glossary Term
        Args:
            glossary_term_body (Glossary): body of the request
        """
        resp = self.client.put(
            path=self.get_suffix(entity), data=glossary_term_body.json()
        )
        logger.info(f"Created a Glossary Term: {resp}")
