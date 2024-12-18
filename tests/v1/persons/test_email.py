import pytest
from app.models.person import Person
from uuid import uuid4


def test_valid_email_addresses():
    valid_email_addresses = [
        "test@test.com",
        "name@justice.gov.uk",
        "john.doe1234@gmail.com",
    ]

    for email_address in valid_email_addresses:
        Person(name="Name", case_id=uuid4(), email=email_address)


def test_invalid_email_addresses():
    invalid_email_addresses = [
        "a",
        "potato",
        "name@domain",
        1,
        12435544434232,
        3.1415926,
        b"0134333434353",
    ]
    for email_address in invalid_email_addresses:
        with pytest.raises(ValueError):
            Person(name="Name", case_id=uuid4(), email=email_address)
