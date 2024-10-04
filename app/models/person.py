from sqlmodel import Field, SQLModel, String, Relationship
from app.models.base import TableModelMixin
from app.models.types.postcode import Postcode
from app.models.types.phone_number import PhoneNumber
from pydantic import EmailStr
from uuid import UUID


class BasePersonModel(SQLModel):
    case_id: UUID = Field(foreign_key="cases.id", index=True)
    name: str
    address: str | None
    phone_number: PhoneNumber | None = Field(default=None, sa_type=String)
    postcode: Postcode | None = Field(default=None, sa_type=String)
    email: EmailStr | None = Field(sa_type=String)


class Person(BasePersonModel, TableModelMixin, table=True):
    # This allows for linking the person back to the case, this allows us to address persons directly by using
    # the `Case.person` syntax, rather than searching for each note using its ID.
    case: "Case" = Relationship(back_populates="people")  # noqa: F821
