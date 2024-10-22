from sqlalchemy.orm import declared_attr
from sqlmodel import Field, SQLModel
from datetime import datetime, UTC
from uuid import UUID, uuid4
from pydantic import BaseModel


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

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    @declared_attr
    def __tablename__(self) -> str:
        """Defaults the table name to be the lowercase plural of the model name. I.e. Case -> cases.
        Submodels can override this by setting __tablename__ to their desired name."""
        return f"{self.__name__.lower()}s"

    class Config:
        """Ensures that Pydantic validates all subclasses ensuring all objects' attribute's datatypes consistently
        match their type annotations"""

        validate_assignment = True


class BaseRequest(BaseModel):
    class Meta:
        foreign_fields = {}
        model = None

    def get_model(self):
        if not self.Meta.model:
            raise NotImplementedError(
                "Either set the Meta.model property or override the get_model() method."
            )
        return self.Meta.model

    def get_foreign_fields(self):
        return self.Meta.foreign_fields

    def translate(self):
        data = self.dict()
        foreign_fields_names = self.get_foreign_fields()
        foreign_fields_data = {}
        self_fields = {}
        for field_name, field_value in data.items():
            if field_name in foreign_fields_names:
                foreign_fields_data[field_name] = field_value
            else:
                self_fields[field_name] = field_value
        return {**self_fields, **self._translate_foreign_fields(foreign_fields_data)}

    def _translate_foreign_fields(self, fields):
        instances = {}
        for field_name, field_value in fields.items():
            field = getattr(self, field_name)
            if not field:
                continue
            model = field[0].get_model()
            if isinstance(field_value, list):
                instances[field_name] = [model(**value) for value in field_value]
            else:
                instances[field_name] = model(**field_value)
        return instances
