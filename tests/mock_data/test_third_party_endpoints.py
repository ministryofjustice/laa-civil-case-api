"""
Tests for third-party endpoints in mock_data.py.
"""

import pytest
from unittest.mock import patch

from app.models.mock_case import ThirdPartyCreate, ThirdPartyUpdate, PassphraseSetup


class TestThirdPartyEndpoints:
    """Test the third-party related API endpoints."""

    def test_add_third_party_success(self, client, mock_data):
        """Test POST /mock/cases/{case_reference}/third-party endpoint with valid data."""
        test_case = mock_data[2].copy()  # Maya Patel case with no third party
        test_case["thirdParty"] = {
            "fullName": "John Smith",
            "emailAddress": "john.smith@email.com",
            "contactNumber": "0123456789",
            "safeToCall": True,
            "address": "123 Main Street, London",
            "postcode": "SW1A 1AA",
            "relationshipToClient": {"selected": ["Other"]},
            "passphraseSetUp": {
                "selected": ["Yes"],
                "passphrase": "LetMeIn",
            },
        }

        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file") as mock_save:
                mock_find.return_value = (mock_data[2], 2, mock_data)

                response = client.post(
                    "/latest/mock/cases/PC-8765-4321/third-party",
                    json={
                        "fullName": "John Smith",
                        "emailAddress": "john.smith@email.com",
                        "contactNumber": "0123456789",
                        "safeToCall": True,
                        "address": "123 Main Street, London",
                        "postcode": "SW1A 1AA",
                        "relationshipToClient": {"selected": ["Other"]},
                        "passphraseSetUp": {
                            "selected": ["Yes"],
                            "passphrase": "LetMeIn",
                        },
                    },
                )

        assert response.status_code == 200
        data = response.json()
        assert data["caseReference"] == "PC-8765-4321"
        assert data["thirdParty"]["fullName"] == "John Smith"
        assert data["thirdParty"]["emailAddress"] == "john.smith@email.com"
        mock_save.assert_called_once()

    def test_add_third_party_minimal_data(self, client, mock_data):
        """Test adding third party with only required fullName field."""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file"):
                mock_find.return_value = (mock_data[2], 2, mock_data)

                response = client.post(
                    "/latest/mock/cases/PC-8765-4321/third-party",
                    json={"fullName": "Jane Doe"},
                )

        assert response.status_code == 200
        data = response.json()
        assert data["thirdParty"]["fullName"] == "Jane Doe"
        # Optional fields should have default values
        assert data["thirdParty"]["emailAddress"] is None
        assert data["thirdParty"]["safeToCall"] is False
        assert data["thirdParty"]["passphraseSetUp"] is None

    def test_add_third_party_missing_fullname(self, client, mock_data):
        """Test adding third party without required fullName field."""
        response = client.post(
            "/latest/mock/cases/PC-8765-4321/third-party",
            json={"emailAddress": "test@email.com"},
        )

        assert response.status_code == 422  # Validation error
        error_detail = response.json()["detail"]
        assert any(
            error.get("loc") and "fullName" in error["loc"] for error in error_detail
        )

    def test_add_third_party_empty_fullname(self, client, mock_data):
        """Test adding third party with empty fullName field."""
        response = client.post(
            "/latest/mock/cases/PC-8765-4321/third-party", json={"fullName": ""}
        )

        assert response.status_code == 422  # Validation error
        error_detail = response.json()["detail"]
        assert any(
            error.get("loc") and "fullName" in error["loc"] for error in error_detail
        )

    def test_add_third_party_whitespace_fullname(self, client, mock_data):
        """Test adding third party with whitespace-only fullName field."""
        response = client.post(
            "/latest/mock/cases/PC-8765-4321/third-party", json={"fullName": "   "}
        )

        assert response.status_code == 422  # Validation error
        error_detail = response.json()["detail"]
        assert any(
            error.get("loc") and "fullName" in error["loc"] for error in error_detail
        )

    def test_add_third_party_fullname_with_spaces(self, client, mock_data):
        """Test adding third party with fullName that has leading/trailing spaces."""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file"):
                mock_find.return_value = (mock_data[2], 2, mock_data)

                response = client.post(
                    "/latest/mock/cases/PC-8765-4321/third-party",
                    json={"fullName": "  John Smith  "},
                )

        assert response.status_code == 200
        data = response.json()
        # Should be trimmed
        assert data["thirdParty"]["fullName"] == "John Smith"

    def test_add_third_party_case_not_found(self, client):
        """Test adding third party to non-existent case."""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            from fastapi import HTTPException

            mock_find.side_effect = HTTPException(
                status_code=404, detail="Case with reference 'PC-9999-9999' not found"
            )

            response = client.post(
                "/latest/mock/cases/PC-9999-9999/third-party",
                json={"fullName": "John Smith"},
            )

        assert response.status_code == 404
        assert (
            "Case with reference 'PC-9999-9999' not found" in response.json()["detail"]
        )

    def test_update_third_party_success(self, client, mock_data):
        """Test PUT /mock/cases/{case_reference}/third-party endpoint with valid data."""
        # Use Ember Hamilton case which has existing third party
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file") as mock_save:
                mock_find.return_value = (mock_data[0], 0, mock_data)

                response = client.put(
                    "/latest/mock/cases/PC-3184-5962/third-party",
                    json={
                        "fullName": "Alex Rivers Updated",
                        "emailAddress": "alex.updated@email.com",
                        "safeToCall": False,
                    },
                )

        assert response.status_code == 200
        data = response.json()
        assert data["thirdParty"]["fullName"] == "Alex Rivers Updated"
        assert data["thirdParty"]["emailAddress"] == "alex.updated@email.com"
        assert data["thirdParty"]["safeToCall"] is False
        # Unchanged fields should remain the same
        assert data["thirdParty"]["postcode"] == "NW1 6XE"
        # passphraseSetUp should remain unchanged
        assert data["thirdParty"]["passphraseSetUp"]["passphrase"] == "Secret123"
        mock_save.assert_called_once()

    def test_update_third_party_partial_update(self, client, mock_data):
        """Test updating only some fields of third party."""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file"):
                mock_find.return_value = (mock_data[0], 0, mock_data)

                response = client.put(
                    "/latest/mock/cases/PC-3184-5962/third-party",
                    json={"fullName": "Alex Rivers Updated"},
                )

        assert response.status_code == 200
        data = response.json()
        assert data["thirdParty"]["fullName"] == "Alex Rivers Updated"
        # Other fields should remain unchanged
        assert data["thirdParty"]["emailAddress"] == "alex@rivers.com"
        # passphraseSetUp should remain unchanged
        assert data["thirdParty"]["passphraseSetUp"]["passphrase"] == "Secret123"

    def test_update_third_party_missing_fullname(self, client, mock_data):
        """Test updating third party without required fullName field."""
        response = client.put(
            "/latest/mock/cases/PC-3184-5962/third-party",
            json={"emailAddress": "test@email.com"},
        )

        assert response.status_code == 422  # Validation error
        error_detail = response.json()["detail"]
        assert any(
            error.get("loc") and "fullName" in error["loc"] for error in error_detail
        )

    def test_update_third_party_empty_fullname(self, client, mock_data):
        """Test updating third party with empty fullName field."""
        response = client.put(
            "/latest/mock/cases/PC-3184-5962/third-party", json={"fullName": ""}
        )

        assert response.status_code == 422  # Validation error
        error_detail = response.json()["detail"]
        assert any(
            error.get("loc") and "fullName" in error["loc"] for error in error_detail
        )

    def test_update_third_party_case_not_found(self, client):
        """Test updating third party for non-existent case."""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            from fastapi import HTTPException

            mock_find.side_effect = HTTPException(
                status_code=404, detail="Case with reference 'PC-9999-9999' not found"
            )

            response = client.put(
                "/latest/mock/cases/PC-9999-9999/third-party",
                json={"fullName": "John Smith"},
            )

        assert response.status_code == 404
        assert (
            "Case with reference 'PC-9999-9999' not found" in response.json()["detail"]
        )

    def test_update_third_party_no_existing_third_party(self, client, mock_data):
        """Test updating third party when case has no existing third party."""
        # Use Maya Patel case which has no third party
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            mock_find.return_value = (mock_data[2], 2, mock_data)

            response = client.put(
                "/latest/mock/cases/PC-8765-4321/third-party",
                json={"fullName": "John Smith"},
            )

        assert response.status_code == 404
        assert "No third party information found for case" in response.json()["detail"]

    def test_update_third_party_fullname_trimming(self, client, mock_data):
        """Test that fullName gets trimmed during update."""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file"):
                mock_find.return_value = (mock_data[0], 0, mock_data)

                response = client.put(
                    "/latest/mock/cases/PC-3184-5962/third-party",
                    json={"fullName": "  Alex Rivers Trimmed  "},
                )

        assert response.status_code == 200
        data = response.json()
        # Should be trimmed
        assert data["thirdParty"]["fullName"] == "Alex Rivers Trimmed"

    def test_delete_third_party_success(self, client, mock_data):
        """Test DELETE mock/cases/{case_reference}/third-party when thirdParty exists"""
        # Use Ember Hamilton case which has existing third party
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file") as mock_save:
                mock_find.return_value = (mock_data[0], 0, mock_data)
                response = client.delete(
                    "/latest/mock/cases/PC-3184-5962/third-party",
                )
        assert response.status_code == 200
        data = response.json()
        assert data["caseReference"] == "PC-3184-5962"
        assert data["thirdParty"] is None
        mock_save.assert_called_once()

    def test_delete_third_party_case_not_found(self, client):
        """Test DELETE mock/cases/{case_reference}/third-party when thirdParty not found"""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            from fastapi import HTTPException

            mock_find.side_effect = HTTPException(
                status_code=404, detail="Case with reference 'PC-9999-9999' not found"
            )
            response = client.delete(
                "/latest/mock/cases/PC-9999-9999/third-party",
            )
        assert response.status_code == 404
        assert (
            "Case with reference 'PC-9999-9999' not found" in response.json()["detail"]
        )

    def test_delete_third_party_no_existing_data(self, client, mock_data):
        """Test DELETE mock/cases/{case_reference}/third-party when no existing thirdParty data"""
        # Use Maya Patel case which has no third party
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            mock_find.return_value = (mock_data[2], 2, mock_data)
            response = client.delete("/latest/mock/cases/PC-8765-4321/third-party")
        assert response.status_code == 404
        assert "No third party information found for case" in response.json()["detail"]


class TestThirdPartyModels:
    """Test ThirdParty model validation."""

    def test_passphrase_setup_yes_scenario(self):
        """Test PassphraseSetup model with Yes scenario."""
        passphrase = PassphraseSetup(selected=["Yes"], passphrase="LetMeIn")
        assert passphrase.selected == ["Yes"]
        assert passphrase.passphrase == "LetMeIn"

    def test_passphrase_setup_no_scenario(self):
        """Test PassphraseSetup model with No scenario."""
        passphrase = PassphraseSetup(selected=["No, client is a child or patient"])
        assert passphrase.selected == ["No, client is a child or patient"]
        assert passphrase.passphrase is None  # No passphrase for No scenario

    def test_third_party_create_valid(self):
        """Test creating ThirdPartyCreate with valid data."""
        passphrase = PassphraseSetup(selected=["Yes"], passphrase="Secret123")
        data = ThirdPartyCreate(
            fullName="John Smith",
            emailAddress="john@email.com",
            safeToCall=True,
            passphraseSetUp=passphrase,
        )
        assert data.fullName == "John Smith"
        assert data.emailAddress == "john@email.com"
        assert data.safeToCall is True
        assert data.passphraseSetUp.passphrase == "Secret123"

    def test_third_party_create_minimal(self):
        """Test creating ThirdPartyCreate with minimal data."""
        data = ThirdPartyCreate(fullName="Jane Doe")
        assert data.fullName == "Jane Doe"
        assert data.emailAddress is None
        assert data.safeToCall is False  # Default value
        assert data.passphraseSetUp is None

    def test_third_party_create_fullname_trimming(self):
        """Test that fullName gets trimmed in ThirdPartyCreate."""
        data = ThirdPartyCreate(fullName="  John Smith  ")
        assert data.fullName == "John Smith"

    def test_third_party_create_empty_fullname(self):
        """Test ThirdPartyCreate with empty fullName."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ThirdPartyCreate(fullName="")

        assert "fullName is required and cannot be empty" in str(exc_info.value)

    def test_third_party_create_whitespace_fullname(self):
        """Test ThirdPartyCreate with whitespace-only fullName."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ThirdPartyCreate(fullName="   ")

        assert "fullName is required and cannot be empty" in str(exc_info.value)

    def test_third_party_update_valid(self):
        """Test creating ThirdPartyUpdate with valid data."""
        passphrase = PassphraseSetup(selected=["No, client is a child or patient"])
        data = ThirdPartyUpdate(
            fullName="John Smith Updated",
            emailAddress="john.updated@email.com",
            passphraseSetUp=passphrase,
        )
        assert data.fullName == "John Smith Updated"
        assert data.emailAddress == "john.updated@email.com"
        assert data.passphraseSetUp.selected == ["No, client is a child or patient"]

    def test_third_party_update_fullname_validation(self):
        """Test ThirdPartyUpdate fullName validation."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ThirdPartyUpdate(fullName="")

        assert "fullName is required and cannot be empty" in str(exc_info.value)

    def test_third_party_update_fullname_trimming(self):
        """Test that fullName gets trimmed in ThirdPartyUpdate."""
        data = ThirdPartyUpdate(fullName="  Updated Name  ")
        assert data.fullName == "Updated Name"

    def test_third_party_create_safe_to_call_empty_string(self):
        """Test that empty string safeToCall is converted to True."""
        data = ThirdPartyCreate(fullName="John Smith", safeToCall="")
        assert data.safeToCall is True

    def test_third_party_create_safe_to_call_string_values(self):
        """Test that string values for safeToCall are properly converted."""
        # Test truthy string values
        for value in ["true", "True", "TRUE", "1", "yes", "Yes"]:
            data = ThirdPartyCreate(fullName="John Smith", safeToCall=value)
            assert data.safeToCall is True, f"Expected True for '{value}'"

        # Test falsy string values
        for value in ["false", "False", "FALSE", "0", "no", "No"]:
            data = ThirdPartyCreate(fullName="John Smith", safeToCall=value)
            assert data.safeToCall is False, f"Expected False for '{value}'"

        # Test invalid string values (should default to True)
        for value in ["invalid", "random", "maybe"]:
            data = ThirdPartyCreate(fullName="John Smith", safeToCall=value)
            assert data.safeToCall is True, (
                f"Expected True (default) for invalid value '{value}'"
            )

    def test_third_party_update_safe_to_call_empty_string(self):
        """Test that empty string safeToCall is converted to None in updates."""
        data = ThirdPartyUpdate(fullName="John Smith", safeToCall="")
        assert data.safeToCall is None

    def test_third_party_update_safe_to_call_string_values(self):
        """Test that string values for safeToCall are properly converted in updates."""
        # Test truthy string values
        for value in ["true", "True", "TRUE", "1", "yes", "Yes"]:
            data = ThirdPartyUpdate(fullName="John Smith", safeToCall=value)
            assert data.safeToCall is True, f"Expected True for '{value}'"

        # Test falsy string values
        for value in ["false", "False", "FALSE", "0", "no", "No"]:
            data = ThirdPartyUpdate(fullName="John Smith", safeToCall=value)
            assert data.safeToCall is False, f"Expected False for '{value}'"

        # Test invalid string values (should default to True)
        for value in ["invalid", "random", "maybe"]:
            data = ThirdPartyUpdate(fullName="John Smith", safeToCall=value)
            assert data.safeToCall is True, (
                f"Expected True (default) for invalid value '{value}'"
            )
