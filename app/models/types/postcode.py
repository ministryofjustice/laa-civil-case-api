import re
from pydantic import AfterValidator
from typing import Any, Annotated

# Regular expression for UK postcodes, derived from British Standard BS7666.
uk_postcode_pattern = r"^([A-Z]{1,2}[0-9][A-Z0-9]?)([0-9][A-Z]{2})$"

# Regular expression for BFPO (British Forces Post Office) postcodes
bfpo_pattern = r"^(BFPO?)([0-9]{1,4})$"


def validate_and_format_postcode(postcode: Any) -> str:
    """
    Validates and formats a UK postcode or BFPO (British Forces Post Office) postcode.

    Any correctly formatted UK Postcode or British Forces Post Office is considered to be valid at this stage,
    regardless of if it exists.

    As Legal Aid is different in Scotland, Northern Ireland and British Overseas territories these postcodes could
    be deemed as invalid, however, this is not the purpose of this validator.

    Args:
        postcode (str): The postcode to validate and format.

    Returns:
        str: The validated and formatted postcode.

    Raises:
        ValueError: If the input is not a string or if the postcode format is invalid.
    """

    if not isinstance(postcode, str):
        raise ValueError("Postcode must be a string")

    postcode = "".join(postcode.split())  # Remove all whitespace for consistency

    postcode = postcode.upper()  # Convert to uppercase for consistency

    match = re.match(uk_postcode_pattern, postcode) or re.match(bfpo_pattern, postcode)
    if not match:
        raise ValueError(
            "Invalid UK Postcode format. Please enter a valid UK Postcode."
        )

    # Format the persons with a space for consistency
    formatted_postcode = f"{match.group(1)} {match.group(2)}"

    return formatted_postcode


Postcode = Annotated[str, AfterValidator(validate_and_format_postcode)]
