#  Copyright (c) ZenML GmbH 2022. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.
"""SQL Model Implementations for Stack Components."""

import base64
import json
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from zenml.enums import StackComponentType
from zenml.models import ComponentModel
from zenml.zen_stores.schemas.stack_schemas import (
    StackCompositionSchema,
    StackSchema,
)


class StackComponentSchema(SQLModel, table=True):
    """SQL Model for stack components."""

    id: UUID = Field(primary_key=True, default_factory=uuid4)

    name: str
    is_shared: bool

    type: StackComponentType
    flavor_name: str
    # flavor_id: UUID = Field(foreign_key="flavorschema.id", nullable=True)
    # TODO: Prefill flavors
    user: UUID = Field(foreign_key="userschema.id")
    project: UUID = Field(foreign_key="projectschema.id")

    configuration: bytes

    creation_date: datetime = Field(default_factory=datetime.now)

    stacks: List["StackSchema"] = Relationship(
        back_populates="components", link_model=StackCompositionSchema
    )

    @classmethod
    def from_create_model(
        cls, user_id: UUID, project_id: UUID, component: ComponentModel
    ) -> "StackComponentSchema":
        """Create a `StackComponentSchema` with `id` and `created_at` missing.

        Args:
            user_id: The ID of the user creating the component.
            project_id: The ID of the project the component belongs to.
            component: The component model from which to create the schema.

        Returns:
            The created `StackComponentSchema`.
        """
        return cls(
            name=component.name,
            project=project_id,
            user=user_id,
            is_shared=component.is_shared,
            type=component.type,
            flavor_name=component.flavor,
            configuration=base64.b64encode(
                json.dumps(component.configuration).encode("utf-8")
            ),
        )

    def from_update_model(
        self,
        component: ComponentModel,
    ) -> "StackComponentSchema":
        """Update the updatable fields on an existing `StackSchema`.

        Args:
            component: The component model from which to update the schema.

        Returns:
            A `StackSchema`
        """
        self.name = component.name
        self.is_shared = component.is_shared
        self.configuration = base64.b64encode(
            json.dumps(component.configuration).encode("utf-8")
        )
        return self

    def to_model(self) -> "ComponentModel":
        """Creates a `ComponentModel` from an instance of a `StackSchema`.

        Returns:
            A `ComponentModel`
        """
        return ComponentModel(
            id=self.id,
            name=self.name,
            type=self.type,
            flavor=self.flavor_name,
            user=self.user,
            project=self.project,
            is_shared=self.is_shared,
            configuration=json.loads(
                base64.b64decode(self.configuration).decode()
            ),
            creation_date=self.creation_date,
        )
