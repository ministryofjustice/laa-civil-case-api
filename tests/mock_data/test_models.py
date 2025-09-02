"""
Tests for models in mock_case.py.
"""

import pytest
from pydantic import ValidationError

from app.models.mock_case import (
    MockCase,
    ThirdParty,
    ThirdPartyCreate,
    ThirdPartyUpdate,
    ReasonableAdjustments,
)


class TestMockCaseModel:
    """Test the MockCase model."""

    def test_mock_case_creation_valid(self):
        """Test creating a MockCase with valid data."""
        case_data = {
            "fullName": "John Smith",
            "caseReference": "PC-1234-5678",
            "dateReceived": "2025-01-01T10:00:00-05:00",
            "caseStatus": "New",
            "dateOfBirth": "1990-01-01T00:00:00-05:00",
        }

        case = MockCase(**case_data)
        assert case.fullName == "John Smith"
        assert case.caseReference == "PC-1234-5678"
        assert case.caseStatus == "New"

    def test_mock_case_with_third_party(self):
        """Test creating a MockCase with third party information."""
        case_data = {
            "fullName": "John Smith",
            "caseReference": "PC-1234-5678",
            "dateReceived": "2025-01-01T10:00:00-05:00",
            "caseStatus": "New",
            "dateOfBirth": "1990-01-01T00:00:00-05:00",
            "thirdParty": {
                "fullName": "Jane Doe",
                "emailAddress": "jane@email.com",
                "safeToCall": True,
            },
        }

        case = MockCase(**case_data)
        assert case.thirdParty.fullName == "Jane Doe"
        assert case.thirdParty.emailAddress == "jane@email.com"
        assert case.thirdParty.safeToCall is True

    def test_mock_case_optional_fields(self):
        """Test MockCase with optional fields having default values."""
        case_data = {
            "fullName": "John Smith",
            "caseReference": "PC-1234-5678",
            "dateReceived": "2025-01-01T10:00:00-05:00",
            "caseStatus": "New",
            "dateOfBirth": "1990-01-01T00:00:00-05:00",
        }

        case = MockCase(**case_data)
        assert case.refCode == ""
        assert case.clientIsVulnerable is False
        assert case.language == "English"
        assert case.phoneNumber == ""
        assert case.thirdParty is None

    def test_mock_case_with_reasonable_adjustments(self):
        """Test MockCase with reasonable adjustments."""
        case_data = {
            "fullName": "John Smith",
            "caseReference": "PC-1234-5678",
            "dateReceived": "2025-01-01T10:00:00-05:00",
            "caseStatus": "New",
            "dateOfBirth": "1990-01-01T00:00:00-05:00",
            "reasonableAdjustments": {
                "selected": ["BSL - Webcam"],
                "available": ["BSL - Webcam", "Callback preference"],
                "additionalInfo": "Client needs extra time",
            },
        }

        case = MockCase(**case_data)
        assert case.reasonableAdjustments.selected == ["BSL - Webcam"]
        assert "BSL - Webcam" in case.reasonableAdjustments.available
        assert case.reasonableAdjustments.additionalInfo == "Client needs extra time"


class TestThirdPartyModel:
    """Test the ThirdParty model."""

    def test_third_party_creation_valid(self):
        """Test creating a ThirdParty with valid data."""
        third_party_data = {
            "fullName": "Jane Doe",
            "emailAddress": "jane@email.com",
            "contactNumber": "0123456789",
            "safeToCall": True,
            "address": "123 Main Street",
            "postcode": "SW1A 1AA",
        }

        third_party = ThirdParty(**third_party_data)
        assert third_party.fullName == "Jane Doe"
        assert third_party.emailAddress == "jane@email.com"
        assert third_party.safeToCall is True

    def test_third_party_minimal_data(self):
        """Test creating a ThirdParty with minimal data."""
        third_party = ThirdParty(fullName="Jane Doe")
        assert third_party.fullName == "Jane Doe"
        assert third_party.emailAddress is None
        assert third_party.safeToCall is False
        assert third_party.passphraseSetUp is False

    def test_third_party_optional_fields_defaults(self):
        """Test ThirdParty optional fields have correct defaults."""
        third_party = ThirdParty(fullName="Jane Doe")
        assert third_party.contactNumber is None
        assert third_party.address is None
        assert third_party.postcode is None
        assert third_party.relationshipToClient is None
        assert third_party.passphraseNotSetUpReason == ""
        assert third_party.passphrase == ""


class TestThirdPartyCreateModel:
    """Test the ThirdPartyCreate model."""

    def test_third_party_create_valid(self):
        """Test creating ThirdPartyCreate with valid data."""
        data = {
            "fullName": "John Smith",
            "emailAddress": "john@email.com",
            "contactNumber": "0123456789",
            "safeToCall": True,
        }

        third_party = ThirdPartyCreate(**data)
        assert third_party.fullName == "John Smith"
        assert third_party.emailAddress == "john@email.com"
        assert third_party.safeToCall is True

    def test_third_party_create_minimal(self):
        """Test creating ThirdPartyCreate with only required field."""
        third_party = ThirdPartyCreate(fullName="Jane Doe")
        assert third_party.fullName == "Jane Doe"
        assert third_party.emailAddress is None
        assert third_party.safeToCall is False

    def test_third_party_create_fullname_required(self):
        """Test that fullName is required in ThirdPartyCreate."""
        with pytest.raises(ValidationError) as exc_info:
            ThirdPartyCreate()

        error_messages = str(exc_info.value)
        assert "fullName" in error_messages
        assert "Field required" in error_messages

    def test_third_party_create_fullname_empty(self):
        """Test ThirdPartyCreate rejects empty fullName."""
        with pytest.raises(ValidationError) as exc_info:
            ThirdPartyCreate(fullName="")

        assert "fullName is required and cannot be empty" in str(exc_info.value)

    def test_third_party_create_fullname_whitespace(self):
        """Test ThirdPartyCreate rejects whitespace-only fullName."""
        with pytest.raises(ValidationError) as exc_info:
            ThirdPartyCreate(fullName="   ")

        assert "fullName is required and cannot be empty" in str(exc_info.value)

    def test_third_party_create_fullname_trimming(self):
        """Test ThirdPartyCreate trims fullName."""
        third_party = ThirdPartyCreate(fullName="  John Smith  ")
        assert third_party.fullName == "John Smith"

    def test_third_party_create_with_all_fields(self):
        """Test ThirdPartyCreate with all possible fields."""
        data = {
            "fullName": "Complete Person",
            "emailAddress": "complete@email.com",
            "contactNumber": "0123456789",
            "safeToCall": True,
            "address": "123 Complete Street",
            "postcode": "CO1 1MP",
            "relationshipToClient": {"type": "family"},
            "passphraseSetUp": True,
            "passphraseNotSetUpReason": "",
            "passphrase": "secret123",
        }

        third_party = ThirdPartyCreate(**data)
        assert third_party.fullName == "Complete Person"
        assert third_party.relationshipToClient == {"type": "family"}
        assert third_party.passphraseSetUp is True


class TestThirdPartyUpdateModel:
    """Test the ThirdPartyUpdate model."""

    def test_third_party_update_valid(self):
        """Test creating ThirdPartyUpdate with valid data."""
        data = {"fullName": "Updated Name", "emailAddress": "updated@email.com"}

        update = ThirdPartyUpdate(**data)
        assert update.fullName == "Updated Name"
        assert update.emailAddress == "updated@email.com"

    def test_third_party_update_fullname_required(self):
        """Test that fullName is required in ThirdPartyUpdate."""
        with pytest.raises(ValidationError) as exc_info:
            ThirdPartyUpdate()

        error_messages = str(exc_info.value)
        assert "fullName" in error_messages
        assert "Field required" in error_messages

    def test_third_party_update_fullname_validation(self):
        """Test ThirdPartyUpdate fullName validation."""
        # Empty fullName
        with pytest.raises(ValidationError) as exc_info:
            ThirdPartyUpdate(fullName="")
        assert "fullName is required and cannot be empty" in str(exc_info.value)

        # Whitespace-only fullName
        with pytest.raises(ValidationError) as exc_info:
            ThirdPartyUpdate(fullName="   ")
        assert "fullName is required and cannot be empty" in str(exc_info.value)

    def test_third_party_update_fullname_trimming(self):
        """Test ThirdPartyUpdate trims fullName."""
        update = ThirdPartyUpdate(fullName="  Updated Name  ")
        assert update.fullName == "Updated Name"

    def test_third_party_update_optional_fields(self):
        """Test ThirdPartyUpdate optional fields."""
        update = ThirdPartyUpdate(fullName="Name Only")
        assert update.fullName == "Name Only"
        assert update.emailAddress is None
        assert update.contactNumber is None
        assert update.safeToCall is None  # Note: Optional bool can be None

    def test_third_party_update_partial_data(self):
        """Test ThirdPartyUpdate with partial data for updates."""
        data = {"fullName": "Partial Update", "safeToCall": False}

        update = ThirdPartyUpdate(**data)
        assert update.fullName == "Partial Update"
        assert update.safeToCall is False
        assert update.emailAddress is None
        assert update.address is None


class TestReasonableAdjustmentsModel:
    """Test the ReasonableAdjustments model."""

    def test_reasonable_adjustments_creation(self):
        """Test creating ReasonableAdjustments with data."""
        data = {
            "selected": ["BSL - Webcam", "Callback preference"],
            "available": ["BSL - Webcam", "Callback preference", "Minicom"],
            "additionalInfo": "Client needs extra time",
        }

        adjustments = ReasonableAdjustments(**data)
        assert adjustments.selected == ["BSL - Webcam", "Callback preference"]
        assert len(adjustments.available) == 3
        assert adjustments.additionalInfo == "Client needs extra time"

    def test_reasonable_adjustments_defaults(self):
        """Test ReasonableAdjustments default values."""
        adjustments = ReasonableAdjustments()
        assert adjustments.selected == []
        assert adjustments.available == []
        assert adjustments.additionalInfo == ""

    def test_reasonable_adjustments_partial(self):
        """Test ReasonableAdjustments with partial data."""
        data = {"additionalInfo": "Special requirements"}

        adjustments = ReasonableAdjustments(**data)
        assert adjustments.selected == []
        assert adjustments.available == []
        assert adjustments.additionalInfo == "Special requirements"


class TestModelInteractions:
    """Test interactions between models."""

    def test_mock_case_with_validated_third_party(self):
        """Test MockCase using validated ThirdParty data."""
        # Create third party data that would be validated
        third_party_data = {
            "fullName": "  Validated Person  ",  # Should be trimmed
            "emailAddress": "validated@email.com",
            "safeToCall": True,
        }

        # Create the ThirdParty to validate
        third_party = ThirdParty(**third_party_data)

        case_data = {
            "fullName": "Case Owner",
            "caseReference": "PC-1234-5678",
            "dateReceived": "2025-01-01T10:00:00-05:00",
            "caseStatus": "New",
            "dateOfBirth": "1990-01-01T00:00:00-05:00",
            "thirdParty": third_party,
        }

        case = MockCase(**case_data)
        assert (
            case.thirdParty.fullName == "  Validated Person  "
        )  # ThirdParty doesn't trim
        assert case.thirdParty.emailAddress == "validated@email.com"

    def test_third_party_create_to_dict(self):
        """Test converting ThirdPartyCreate to dict for storage."""
        create_data = ThirdPartyCreate(
            fullName="  John Smith  ", emailAddress="john@email.com", safeToCall=True
        )

        # This simulates what happens in the endpoint
        dict_data = create_data.dict(exclude_unset=True)

        assert dict_data["fullName"] == "John Smith"  # Should be trimmed
        assert dict_data["emailAddress"] == "john@email.com"
        assert dict_data["safeToCall"] is True
        # Fields not provided should not be in the dict
        assert "contactNumber" not in dict_data

    def test_third_party_update_exclude_unset(self):
        """Test ThirdPartyUpdate exclude_unset behavior."""
        update_data = ThirdPartyUpdate(
            fullName="Updated Name", emailAddress="updated@email.com"
        )

        # Only provided fields should be included
        dict_data = update_data.dict(exclude_unset=True)

        assert dict_data["fullName"] == "Updated Name"
        assert dict_data["emailAddress"] == "updated@email.com"
        # Fields not provided should not be in the dict
        assert "contactNumber" not in dict_data
        assert "safeToCall" not in dict_data
