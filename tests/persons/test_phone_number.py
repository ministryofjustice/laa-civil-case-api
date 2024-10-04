import pytest
from app.models.types.phone_number import validate_phone_number


def test_phone_number_validator():
    sample_phone_numbers = [
        # UK numbers (default, without country code)
        "020 7946 0958",
        "0161 496 0647",
        "0117 496 0723",
        "07700 900365",
        "07624 369258",
        "07911 123456",
        "0121 496 0738",
        "01632 960963",
        "0141 496 0763",
        "01534595834",
        # UK numbers (with country code +44)
        "+44 20 7946 0958",
        "+44 161 496 0647",
        "+44 7700 900365",
        "+443450539485",
        "+445495 345954",
        # North American numbers (country code +1)
        "+1 234 567 8901",
        "+1 (555) 123-4567",
        # Australian numbers (country code +61)
        "+61 2 9876 5432",
        "+61 4 1234 5678",
    ]

    for phone_number in sample_phone_numbers:
        assert validate_phone_number(phone_number) == phone_number


def test_invalid_phone_numbers():
    invalid_phone_numbers = [
        "a",
        "potato",
        1,
        12435544434232,
        3.1415926,
        b"0134333434353",
    ]
    for phone_number in invalid_phone_numbers:
        with pytest.raises(ValueError):
            validate_phone_number(phone_number)
