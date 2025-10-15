import re
from pydantic import AfterValidator
from typing import Annotated


def validate_phone_number(phone_number: str) -> str:
    """Validates phone numbers without being strict on the formatting.
    This only checks that the country code is of the corrct length, if it is present
    and that the phone number has the correct number of digits.

    The original formatting will be preserved.

    Args:
        phone_number (str): The phone number to validate.

    Returns:
        str: The validated phone number.

    Raises:
        ValueError: If the input is not a string or if the phone number is too long or short.
    """

    if not isinstance(phone_number, str):
        raise ValueError("Phone number must be a string")

    digits = re.sub(
        r"[^\d+]", "", phone_number
    )  # Extract only digits and + for length validation

    if phone_number.startswith("+"):
        if not re.match(r"^\+\d{1,3}", phone_number):
            raise ValueError(
                "Invalid country code format. Must be + followed by 1-3 digits."
            )
        national_start = re.search(r"^\+\d{1,3}", digits).end()
        national_number = digits[national_start:]
    else:
        national_number = digits

    if not 7 <= len(national_number) <= 15:
        raise ValueError(
            "Phone number must be between 7 and 15 digits long (excluding the country code)."
        )

    return phone_number


PhoneNumber = Annotated[str, AfterValidator(validate_phone_number)]
