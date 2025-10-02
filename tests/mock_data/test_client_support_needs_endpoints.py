"""
Tests for client support needs endpoints in mock_data.py.
"""

from unittest.mock import patch

from app.models.mock_case import ClientSupportNeedsCreate


class TestClientSupportNeedsEndpoints:
    """Test the client support needs related API endpoints."""

    def test_add_client_support_needs_success(self, client, mock_data):
        """Test POST /mock/cases/{case_reference}/client-support-needs endpoint with valid data."""
        test_case = mock_data[2].copy()  # Maya Patel case with no client support needs
        test_case["clientSupportNeeds"] = {
            "bslWebcam": "No",
            "textRelay": "No",
            "callbackPreference": "No",
            "languageSupportNeeds": "English",
            "notes": "Here are some notes from the operator",
        }

        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file") as mock_save:
                mock_find.return_value = (mock_data[2], 2, mock_data)

                response = client.post(
                    "/latest/mock/cases/PC-8765-4321/client-support-needs",
                    json={
                        "bslWebcam": "No",
                        "textRelay": "No",
                        "callbackPreference": "No",
                        "languageSupportNeeds": "English",
                        "notes": "Here are some notes from the operator",
                    },
                )

        assert response.status_code == 200
        data = response.json()
        assert data["caseReference"] == "PC-8765-4321"
        assert data["clientSupportNeeds"]["bslWebcam"] == "No"
        assert data["clientSupportNeeds"]["textRelay"] == "No"
        assert data["clientSupportNeeds"]["callbackPreference"] == "No"
        assert data["clientSupportNeeds"]["languageSupportNeeds"] == "English"
        assert (
            data["clientSupportNeeds"]["notes"]
            == "Here are some notes from the operator"
        )
        mock_save.assert_called_once()

    def test_add_client_support_needs_minimal_data(self, client, mock_data):
        """Test adding client support needs with only one field."""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file"):
                mock_find.return_value = (mock_data[2], 2, mock_data)

                response = client.post(
                    "/latest/mock/cases/PC-8765-4321/client-support-needs",
                    json={"languageSupportNeeds": "British Sign Language"},
                )

        assert response.status_code == 200
        data = response.json()
        assert (
            data["clientSupportNeeds"]["languageSupportNeeds"]
            == "British Sign Language"
        )
        # Other fields should have None values since they weren't provided
        assert data["clientSupportNeeds"]["bslWebcam"] is None
        assert data["clientSupportNeeds"]["textRelay"] is None
        assert data["clientSupportNeeds"]["callbackPreference"] is None
        assert data["clientSupportNeeds"]["notes"] is None

    def test_add_client_support_needs_all_fields(self, client, mock_data):
        """Test adding client support needs with all possible fields."""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file"):
                mock_find.return_value = (mock_data[2], 2, mock_data)

                response = client.post(
                    "/latest/mock/cases/PC-8765-4321/client-support-needs",
                    json={
                        "bslWebcam": "Yes",
                        "textRelay": "Yes",
                        "callbackPreference": "Yes",
                        "languageSupportNeeds": "British Sign Language",
                        "notes": "Client requires BSL interpreter and text relay services",
                    },
                )

        assert response.status_code == 200
        data = response.json()
        assert data["clientSupportNeeds"]["bslWebcam"] == "Yes"
        assert data["clientSupportNeeds"]["textRelay"] == "Yes"
        assert data["clientSupportNeeds"]["callbackPreference"] == "Yes"
        assert (
            data["clientSupportNeeds"]["languageSupportNeeds"]
            == "British Sign Language"
        )
        assert (
            data["clientSupportNeeds"]["notes"]
            == "Client requires BSL interpreter and text relay services"
        )

    def test_add_client_support_needs_empty_body(self, client, mock_data):
        """Test adding client support needs with empty request body."""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file"):
                mock_find.return_value = (mock_data[2], 2, mock_data)

                response = client.post(
                    "/latest/mock/cases/PC-8765-4321/client-support-needs",
                    json={},
                )

        assert response.status_code == 200
        data = response.json()
        # Should have clientSupportNeeds object with all None values
        assert data["clientSupportNeeds"]["bslWebcam"] is None
        assert data["clientSupportNeeds"]["textRelay"] is None
        assert data["clientSupportNeeds"]["callbackPreference"] is None
        assert data["clientSupportNeeds"]["languageSupportNeeds"] is None
        assert data["clientSupportNeeds"]["notes"] is None

    def test_add_client_support_needs_case_not_found(self, client):
        """Test adding client support needs to non-existent case."""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            from fastapi import HTTPException

            mock_find.side_effect = HTTPException(
                status_code=404, detail="Case with reference 'PC-9999-9999' not found"
            )

            response = client.post(
                "/latest/mock/cases/PC-9999-9999/client-support-needs",
                json={"languageSupportNeeds": "Welsh"},
            )

        assert response.status_code == 404
        assert (
            "Case with reference 'PC-9999-9999' not found" in response.json()["detail"]
        )

    def test_update_client_support_needs_success(self, client, mock_data):
        """Test PUT /mock/cases/{case_reference}/client-support-needs endpoint with valid data."""
        # Set up a case with existing client support needs
        test_case = mock_data[0].copy()
        test_case["clientSupportNeeds"] = {
            "bslWebcam": "No",
            "textRelay": "No",
            "callbackPreference": "No",
            "languageSupportNeeds": "English",
            "notes": "Original notes",
        }

        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file") as mock_save:
                mock_find.return_value = (test_case, 0, mock_data)

                response = client.put(
                    "/latest/mock/cases/PC-3184-5962/client-support-needs",
                    json={
                        "bslWebcam": "Yes",
                        "languageSupportNeeds": "British Sign Language",
                        "notes": "Updated notes - BSL interpreter required",
                    },
                )

        assert response.status_code == 200
        data = response.json()
        assert data["clientSupportNeeds"]["bslWebcam"] == "Yes"
        assert (
            data["clientSupportNeeds"]["languageSupportNeeds"]
            == "British Sign Language"
        )
        assert (
            data["clientSupportNeeds"]["notes"]
            == "Updated notes - BSL interpreter required"
        )
        # Unchanged fields should remain the same
        assert data["clientSupportNeeds"]["textRelay"] == "No"
        assert data["clientSupportNeeds"]["callbackPreference"] == "No"
        mock_save.assert_called_once()

    def test_update_client_support_needs_partial_update(self, client, mock_data):
        """Test updating only some fields of client support needs."""
        test_case = mock_data[0].copy()
        test_case["clientSupportNeeds"] = {
            "bslWebcam": "No",
            "textRelay": "No",
            "callbackPreference": "No",
            "languageSupportNeeds": "English",
            "notes": "Original notes",
        }

        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file"):
                mock_find.return_value = (test_case, 0, mock_data)

                response = client.put(
                    "/latest/mock/cases/PC-3184-5962/client-support-needs",
                    json={"languageSupportNeeds": "Welsh"},
                )

        assert response.status_code == 200
        data = response.json()
        assert data["clientSupportNeeds"]["languageSupportNeeds"] == "Welsh"
        # Other fields should remain unchanged
        assert data["clientSupportNeeds"]["bslWebcam"] == "No"
        assert data["clientSupportNeeds"]["textRelay"] == "No"
        assert data["clientSupportNeeds"]["notes"] == "Original notes"

    def test_update_client_support_needs_case_not_found(self, client):
        """Test updating client support needs for non-existent case."""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            from fastapi import HTTPException

            mock_find.side_effect = HTTPException(
                status_code=404, detail="Case with reference 'PC-9999-9999' not found"
            )

            response = client.put(
                "/latest/mock/cases/PC-9999-9999/client-support-needs",
                json={"languageSupportNeeds": "Welsh"},
            )

        assert response.status_code == 404
        assert (
            "Case with reference 'PC-9999-9999' not found" in response.json()["detail"]
        )

    def test_update_client_support_needs_no_existing_data(self, client, mock_data):
        """Test updating client support needs when case has no existing data."""
        # Use Maya Patel case which has no client support needs
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            mock_find.return_value = (mock_data[2], 2, mock_data)

            response = client.put(
                "/latest/mock/cases/PC-8765-4321/client-support-needs",
                json={"languageSupportNeeds": "Welsh"},
            )

        assert response.status_code == 404
        assert (
            "No client support needs information found for case"
            in response.json()["detail"]
        )

    def test_update_client_support_needs_empty_body(self, client, mock_data):
        """Test updating client support needs with empty request body."""
        test_case = mock_data[0].copy()
        test_case["clientSupportNeeds"] = {
            "bslWebcam": "No",
            "languageSupportNeeds": "English",
        }

        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file"):
                mock_find.return_value = (test_case, 0, mock_data)

                response = client.put(
                    "/latest/mock/cases/PC-3184-5962/client-support-needs",
                    json={},
                )

        assert response.status_code == 200
        data = response.json()
        # No fields should be updated
        assert data["clientSupportNeeds"]["bslWebcam"] == "No"
        assert data["clientSupportNeeds"]["languageSupportNeeds"] == "English"

    def test_delete_client_support_needs_success(self, client, mock_data):
        """Test DELETE /mock/cases/{case_reference}/client-support-needs when client support needs exists"""
        # Set up a case with existing client support needs
        test_case = mock_data[0].copy()
        test_case["clientSupportNeeds"] = {
            "bslWebcam": "Yes",
            "textRelay": "Yes",
            "languageSupportNeeds": "British Sign Language",
            "notes": "BSL interpreter required",
        }

        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file") as mock_save:
                mock_find.return_value = (test_case, 0, mock_data)

                response = client.delete(
                    "/latest/mock/cases/PC-3184-5962/client-support-needs",
                )

        assert response.status_code == 200
        data = response.json()
        assert data["caseReference"] == "PC-3184-5962"
        assert data["clientSupportNeeds"] is None
        mock_save.assert_called_once()

    def test_delete_client_support_needs_case_not_found(self, client):
        """Test DELETE /mock/cases/{case_reference}/client-support-needs when case not found"""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            from fastapi import HTTPException

            mock_find.side_effect = HTTPException(
                status_code=404, detail="Case with reference 'PC-9999-9999' not found"
            )
            response = client.delete(
                "/latest/mock/cases/PC-9999-9999/client-support-needs",
            )
        assert response.status_code == 404
        assert (
            "Case with reference 'PC-9999-9999' not found" in response.json()["detail"]
        )

    def test_delete_client_support_needs_no_existing_data(self, client, mock_data):
        """Test DELETE /mock/cases/{case_reference}/client-support-needs when no existing data"""
        # Use Maya Patel case which has no client support needs
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            mock_find.return_value = (mock_data[2], 2, mock_data)
            response = client.delete(
                "/latest/mock/cases/PC-8765-4321/client-support-needs"
            )
        assert response.status_code == 404
        assert (
            "No client support needs information found for case"
            in response.json()["detail"]
        )


class TestClientSupportNeedsModels:
    """Test ClientSupportNeeds model validation."""

    def test_client_support_needs_create_valid(self):
        """Test creating ClientSupportNeedsCreate with valid data."""
        data = ClientSupportNeedsCreate(
            bslWebcam="Yes",
            textRelay="No",
            callbackPreference="Yes",
            languageSupportNeeds="British Sign Language",
            notes="Client requires BSL interpreter",
        )
        assert data.bslWebcam == "Yes"
        assert data.textRelay == "No"
        assert data.callbackPreference == "Yes"
        assert data.languageSupportNeeds == "British Sign Language"
        assert data.notes == "Client requires BSL interpreter"

    def test_client_support_needs_create_minimal(self):
        """Test creating ClientSupportNeedsCreate with minimal data."""
        data = ClientSupportNeedsCreate(languageSupportNeeds="English")
        assert data.languageSupportNeeds == "English"
        assert data.bslWebcam is None
        assert data.textRelay is None
        assert data.callbackPreference is None
        assert data.notes is None

    def test_client_support_needs_create_empty(self):
        """Test creating ClientSupportNeedsCreate with no data."""
        data = ClientSupportNeedsCreate()
        assert data.bslWebcam is None
        assert data.textRelay is None
        assert data.callbackPreference is None
        assert data.languageSupportNeeds is None
        assert data.notes is None

    def test_client_support_needs_create_all_none(self):
        """Test creating ClientSupportNeedsCreate with all None values."""
        data = ClientSupportNeedsCreate(
            bslWebcam=None,
            textRelay=None,
            callbackPreference=None,
            languageSupportNeeds=None,
            notes=None,
        )
        assert data.bslWebcam is None
        assert data.textRelay is None
        assert data.callbackPreference is None
        assert data.languageSupportNeeds is None
        assert data.notes is None

    def test_client_support_needs_create_string_values(self):
        """Test creating ClientSupportNeedsCreate with various string values."""
        # Test typical "Yes/No" values
        data = ClientSupportNeedsCreate(
            bslWebcam="Yes",
            textRelay="No",
            callbackPreference="Yes",
            languageSupportNeeds="Welsh",
            notes="",
        )
        assert data.bslWebcam == "Yes"
        assert data.textRelay == "No"
        assert data.callbackPreference == "Yes"
        assert data.languageSupportNeeds == "Welsh"
        assert data.notes == ""

    def test_client_support_needs_create_long_strings(self):
        """Test creating ClientSupportNeedsCreate with longer string values."""
        long_notes = "This is a very long note about the client's support needs including specific requirements for BSL interpretation and text relay services during all communications."
        data = ClientSupportNeedsCreate(
            languageSupportNeeds="British Sign Language with certified interpreter",
            notes=long_notes,
        )
        assert (
            data.languageSupportNeeds
            == "British Sign Language with certified interpreter"
        )
        assert data.notes == long_notes

    def test_client_support_needs_create_edge_cases(self):
        """Test creating ClientSupportNeedsCreate with edge case values."""
        data = ClientSupportNeedsCreate(
            bslWebcam="",  # Empty string
            textRelay="Maybe",  # Non-standard value
            callbackPreference="0",  # Number as string
            languageSupportNeeds="Multiple: English, Welsh, BSL",  # Complex value
            notes="   ",  # Whitespace only
        )
        assert data.bslWebcam == ""
        assert data.textRelay == "Maybe"
        assert data.callbackPreference == "0"
        assert data.languageSupportNeeds == "Multiple: English, Welsh, BSL"
        assert data.notes == "   "
