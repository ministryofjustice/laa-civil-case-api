import uuid
from functools import cached_property
from typing import List, Tuple, Any
from sqlalchemy.orm import declared_attr
from sqlalchemy.inspection import inspect
from sqlmodel import Field, SQLModel, Session
from datetime import datetime, UTC
from pydantic import BaseModel


def generate_id() -> uuid.UUID:
    return uuid.uuid4()


class TimestampMixin(SQLModel):
    """Mixin handing adding timestamp fields to models.

    created_at, is set once when the object is first instantiated.
    updated_at, is set when the object is first instantiated and
                updated every time the object is commited to the database.

    Note: As SQLite doesn't support timezone aware timezones you need to add TZInfo when writing tests.
    TODO: Use Postgres as the testing database to fix the above.
    """

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column_kwargs={"onupdate": lambda: datetime.now(UTC)},
    )


class TableModelMixin(TimestampMixin):
    """Mixin adding a UUID4 ID and Timestamps to child models.
    All models which exist in the database should inherit from this mixin"""

    id: uuid.UUID = Field(default_factory=generate_id, primary_key=True)

    @declared_attr
    def __tablename__(self) -> str:
        """Defaults the table name to be the lowercase plural of the model name. I.e. Case -> cases.
        Submodels can override this by setting __tablename__ to their desired name."""
        return f"{self.__name__.lower()}s"

    class Config:
        """Ensures that Pydantic validates all subclasses ensuring all objects' attribute's datatypes consistently
        match their type annotations"""

        validate_assignment = True


class BaseResponse(TableModelMixin):
    pass


class BaseRequest(BaseModel):
    class Meta:
        model: SQLModel

    @property
    def model(self) -> SQLModel:
        if not self.Meta.model:
            raise NotImplementedError(
                "Either set the Meta.model property or override the get_model() method."
            )
        return self.Meta.model

    @cached_property
    def related_fields(self) -> List[str]:
        related_fields = []
        model = self.Meta.model
        if not model:
            return related_fields
        relationship_list: Tuple[str, Any] = inspect(model).relationships.items()
        for relationship in relationship_list:
            field_name = relationship[0]
            if field_name in self.model_fields:
                related_fields.append(field_name)
        return related_fields

    def retrieve(self, session, instance_id: uuid.UUID) -> SQLModel | None:
        model = self.model
        return session.get(model, instance_id)

    def create(self, session: Session) -> SQLModel:
        data = self.translate()
        instance = self.model(**data)
        session.add(instance)
        session.commit()
        session.refresh(instance)
        return instance

    def update(self, instance: SQLModel, session: Session):
        data = self.translate()
        for field_name, field_value in data.items():
            setattr(instance, field_name, field_value)

        session.add(instance)
        session.commit()
        session.refresh(instance)
        return instance

    def translate(self) -> dict:
        """
        Convert a dump of request to a dict that can easily be used to create an instance of a model

        This method currently only translates relationships that are two levels deep i.e Case.person
        and not Case.person.income

        Todo: Allow deeper level of nested fields to be translated
        """
        data = self.model_dump(exclude_unset=True)
        related_fields_names = self.related_fields
        related_fields_data = {}
        fields = {}
        for field_name, field_value in data.items():
            if field_name in related_fields_names and field_value:
                related_fields_data[field_name] = field_value
            else:
                fields[field_name] = field_value
        return {**fields, **self._translate_related_fields(related_fields_data)}

    def _translate_related_fields(self, fields) -> dict:
        """Convert related fields from a dict to an instance of their declared model"""
        instances = {}
        for field_name, field_value in fields.items():
            if not hasattr(self, field_name):
                continue

            field = getattr(self, field_name)
            if not field:
                continue

            if isinstance(field, list):
                model = field[0].model
            else:
                model = field.model

            if isinstance(field_value, list):
                instances[field_name] = [model(**value) for value in field_value]
            else:
                instances[field_name] = model(**field_value)
        return instances
