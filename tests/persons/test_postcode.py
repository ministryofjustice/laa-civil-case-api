import pytest
from app.models.person import Person
from app.models.types.postcode import validate_and_format_postcode


def test_postcode_validation():
    # Valid format
    assert validate_and_format_postcode("SW1A 1AA") == "SW1A 1AA"

    # Extra spaces should be removed
    assert validate_and_format_postcode("SW1A 1AA       ") == "SW1A 1AA"

    # Even if they're in strange places
    assert validate_and_format_postcode("  sw 1a     1a a  ") == "SW1A 1AA"

    malformed_postcodes = [
        1,  # Not a string
        "a.b1 1aa",  # Invalid character '.'
        "SW1A 1A",  # Missing last letter
        "SW1A1AAA",  # Extra letter at the end
        "SW1A 1AA1",  # Extra number at the end
        "SWIA 1AA",  # '1' replaced with 'I'
        "8W1A 1AA",  # Number instead of letter at the start
        "SWCA 1AA",  # Invalid character 'C' in first part
    ]
    for postcode in malformed_postcodes:
        with pytest.raises(ValueError):
            print(postcode)
            validate_and_format_postcode(postcode)


def test_postcode_formatting():
    person = Person(postcode="SW1A1AA", name="Bob")
    assert person.postcode == "SW1A 1AA"

    person.postcode = "sw1a1aa"
    assert person.postcode == "SW1A 1AA"

    person.postcode = " ab9 1bc  "
    assert person.postcode == "AB9 1BC"


def test_unusual_formatted_postcodes():
    person = Person(postcode="XM4 5HQ")
    assert person.postcode == "XM4 5HQ"

    person.postcode = "b1 1Hq"
    assert person.postcode == "B1 1HQ"


def test_british_forces_post_office():
    person = Person(postcode="BFPO 1234")
    assert person.postcode == "BFPO 1234"

    person.postcode = "bfpo5678"
    assert person.postcode == "BFPO 5678"

    person.postcode = "   bfp  o  56 7 8 "
    assert person.postcode == "BFPO 5678"
