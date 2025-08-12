import pytest
import json
from unittest.mock import patch, mock_open, MagicMock
from fastapi import HTTPException, Response

from app.routers.mock_data import (
    load_mock_data,
    filter_cases_by_status,
    sort_cases,
    paginate_cases,
    set_pagination_headers,
    get_cases_by_status,
    search_cases,
)
from app.models.mock_case import MockCase


@pytest.fixture
def mock_data():
    """Sample mock data for testing."""
    return [
        {
            "fullName": "Ember Hamilton",
            "caseReference": "PC-3184-5962",
            "refCode": "",
            "dateReceived": "2025-01-08T19:00:00-05:00",
            "lastModified": "2025-01-09T14:30:00-05:00",
            "caseStatus": "Accepted",
            "dateOfBirth": "1987-02-19T00:00:00-05:00",
            "clientIsVulnerable": True,
            "reasonableAdjustments": {
                "selected": ["BSL - Webcam"],
                "available": [
                    "BSL - Webcam",
                    "Callback preference",
                    "Minicom",
                    "Skype",
                    "Text relay",
                    "No accommodations required",
                ],
                "additionalInfo": "Client prefers morning appointments",
            },
            "language": "English",
            "phoneNumber": "0776744581",
            "safeToCall": False,
            "announceCall": True,
            "emailAddress": "ember.hamilton@email.com",
            "address": "80 Pythagoras Place, Birmingham",
            "postcode": "B1 1DW",
            "laaReference": "3103560",
        },
        {
            "fullName": "John Doe",
            "caseReference": "PC-9999-1111",
            "refCode": "Test refCode",
            "dateReceived": "2025-01-20T19:00:00-05:00",
            "caseStatus": "New",
            "dateOfBirth": "1985-03-10T00:00:00-05:00",
            "clientIsVulnerable": False,
            "reasonableAdjustments": {
                "selected": [],
                "available": [
                    "BSL - Webcam",
                    "Callback preference",
                    "Minicom",
                    "Skype",
                    "Text relay",
                    "No accommodations required",
                ],
                "additionalInfo": "",
            },
            "language": "English",
            "phoneNumber": "0777123456",
            "safeToCall": True,
            "announceCall": False,
            "emailAddress": "john.doe@email.com",
            "address": "123 Test Street, London",
            "postcode": "SW1 1AA",
            "laaReference": "1234567",
        },
        {
            "fullName": "Jane Smith",
            "caseReference": "PC-1234-5678",
            "refCode": "",
            "dateReceived": "2025-01-15T19:00:00-05:00",
            "lastModified": "2025-01-16T14:30:00-05:00",
            "caseStatus": "Opened",
            "dateOfBirth": "1990-04-20T00:00:00-05:00",
            "clientIsVulnerable": True,
            "reasonableAdjustments": {
                "selected": ["Skype"],
                "available": [
                    "BSL - Webcam",
                    "Callback preference",
                    "Minicom",
                    "Skype",
                    "Text relay",
                    "No accommodations required",
                ],
                "additionalInfo": "Requires written confirmation",
            },
            "language": "Welsh",
            "phoneNumber": "0778987654",
            "safeToCall": False,
            "announceCall": True,
            "emailAddress": "jane.smith@email.com",
            "address": "456 Test Avenue, Cardiff",
            "postcode": "CF1 2BB",
            "laaReference": "2345678",
        },
        {
            "fullName": "Bob Wilson",
            "caseReference": "PC-5678-9012",
            "refCode": "",
            "dateReceived": "2025-01-10T19:00:00-05:00",
            "lastModified": "2025-01-11T14:30:00-05:00",
            "dateClosed": "2025-01-12T14:30:00-05:00",
            "caseStatus": "Closed",
            "dateOfBirth": "1988-05-25T00:00:00-05:00",
            "clientIsVulnerable": False,
            "reasonableAdjustments": {
                "selected": ["Text relay"],
                "available": [
                    "BSL - Webcam",
                    "Callback preference",
                    "Minicom",
                    "Skype",
                    "Text relay",
                    "No accommodations required",
                ],
                "additionalInfo": "Needs extra time for responses",
            },
            "language": "English",
            "phoneNumber": "0779876543",
            "safeToCall": True,
            "announceCall": False,
            "emailAddress": "bob.wilson@email.com",
            "address": "789 Test Road, Manchester",
            "postcode": "M1 3CC",
            "laaReference": "3456789",
        },
    ]


class TestLoadMockData:
    """Test the load_mock_data function."""

    def test_load_mock_data_success(self, mock_data):
        """Test successful loading of mock data."""
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            with patch("pathlib.Path.exists", return_value=True):
                result = load_mock_data()
                assert result == mock_data

    def test_load_mock_data_file_not_found(self):
        """Test when mock data file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                load_mock_data()
            assert exc_info.value.status_code == 404

    def test_load_mock_data_invalid_json(self):
        """Test when mock data file contains invalid JSON."""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(HTTPException) as exc_info:
                    load_mock_data()
                assert exc_info.value.status_code == 500

    def test_load_mock_data_general_exception(self):
        """Test when a general exception occurs while loading data."""
        with patch("builtins.open", side_effect=Exception("File read error")):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(HTTPException) as exc_info:
                    load_mock_data()
                assert exc_info.value.status_code == 500


class TestHelperFunctions:
    """Test the helper functions in mock_data.py."""

    def test_filter_cases_by_status(self, mock_data):
        """Test filtering cases by status."""
        # Test filtering for 'New' status
        new_cases = filter_cases_by_status(mock_data, "New")
        assert len(new_cases) == 1
        assert new_cases[0]["caseStatus"] == "New"
        assert new_cases[0]["fullName"] == "John Doe"

        # Test filtering for 'Opened' status
        opened_cases = filter_cases_by_status(mock_data, "Opened")
        assert len(opened_cases) == 1
        assert opened_cases[0]["caseStatus"] == "Opened"
        assert opened_cases[0]["fullName"] == "Jane Smith"

        # Test filtering for 'Accepted' status
        accepted_cases = filter_cases_by_status(mock_data, "Accepted")
        assert len(accepted_cases) == 1
        assert accepted_cases[0]["caseStatus"] == "Accepted"
        assert accepted_cases[0]["fullName"] == "Ember Hamilton"

        # Test filtering for 'Closed' status
        closed_cases = filter_cases_by_status(mock_data, "Closed")
        assert len(closed_cases) == 1
        assert closed_cases[0]["caseStatus"] == "Closed"
        assert closed_cases[0]["fullName"] == "Bob Wilson"

        # Test case-insensitive filtering
        new_cases_lower = filter_cases_by_status(mock_data, "new")
        assert len(new_cases_lower) == 1
        assert new_cases_lower[0]["caseStatus"] == "New"

        # Test filtering with 'all' status (should return all cases)
        all_cases = filter_cases_by_status(mock_data, "all")
        assert len(all_cases) == len(mock_data)

        # Test filtering for non-existent status
        unknown_cases = filter_cases_by_status(mock_data, "Unknown")
        assert len(unknown_cases) == 0

    def test_sort_cases_new_status(self, mock_data):
        """Test sorting cases for 'New' status uses dateReceived."""
        # Create multiple new cases with different dateReceived
        test_cases = [
            {
                "caseStatus": "New",
                "dateReceived": "2025-01-10T19:00:00-05:00",
                "fullName": "First",
            },
            {
                "caseStatus": "New",
                "dateReceived": "2025-01-20T19:00:00-05:00",
                "fullName": "Second",
            },
            {
                "caseStatus": "New",
                "dateReceived": "2025-01-15T19:00:00-05:00",
                "fullName": "Third",
            },
        ]

        # Test descending order (default)
        sorted_desc = sort_cases(test_cases, "desc", "New")
        assert sorted_desc[0]["fullName"] == "Second"  # Latest date
        assert sorted_desc[1]["fullName"] == "Third"  # Middle date
        assert sorted_desc[2]["fullName"] == "First"  # Earliest date

        # Test ascending order
        sorted_asc = sort_cases(test_cases, "asc", "New")
        assert sorted_asc[0]["fullName"] == "First"  # Earliest date
        assert sorted_asc[1]["fullName"] == "Third"  # Middle date
        assert sorted_asc[2]["fullName"] == "Second"  # Latest date

    def test_sort_cases_opened_accepted_status(self, mock_data):
        """Test sorting cases for 'Opened' and 'Accepted' status uses lastModified."""
        test_cases = [
            {
                "caseStatus": "Opened",
                "lastModified": "2025-01-10T14:30:00-05:00",
                "fullName": "First",
            },
            {
                "caseStatus": "Opened",
                "lastModified": "2025-01-20T14:30:00-05:00",
                "fullName": "Second",
            },
            {
                "caseStatus": "Opened",
                "lastModified": "2025-01-15T14:30:00-05:00",
                "fullName": "Third",
            },
        ]

        # Test descending order for Opened
        sorted_desc = sort_cases(test_cases, "desc", "Opened")
        assert sorted_desc[0]["fullName"] == "Second"  # Latest lastModified

        # Test ascending order for Accepted
        test_cases_accepted = [
            {
                "caseStatus": "Accepted",
                "lastModified": "2025-01-10T14:30:00-05:00",
                "fullName": "First",
            },
            {
                "caseStatus": "Accepted",
                "lastModified": "2025-01-20T14:30:00-05:00",
                "fullName": "Second",
            },
        ]
        sorted_asc = sort_cases(test_cases_accepted, "asc", "Accepted")
        assert sorted_asc[0]["fullName"] == "First"  # Earliest lastModified

    def test_sort_cases_closed_status(self, mock_data):
        """Test sorting cases for 'Closed' status uses dateClosed."""
        test_cases = [
            {
                "caseStatus": "Closed",
                "dateClosed": "2025-01-10T14:30:00-05:00",
                "fullName": "First",
            },
            {
                "caseStatus": "Closed",
                "dateClosed": "2025-01-20T14:30:00-05:00",
                "fullName": "Second",
            },
            {
                "caseStatus": "Closed",
                "dateClosed": "2025-01-15T14:30:00-05:00",
                "fullName": "Third",
            },
        ]

        # Test descending order
        sorted_desc = sort_cases(test_cases, "desc", "Closed")
        assert sorted_desc[0]["fullName"] == "Second"  # Latest dateClosed

        # Test ascending order
        sorted_asc = sort_cases(test_cases, "asc", "Closed")
        assert sorted_asc[0]["fullName"] == "First"  # Earliest dateClosed

    def test_sort_cases_unknown_status(self, mock_data):
        """Test sorting cases for unknown status defaults to dateReceived."""
        test_cases = [
            {
                "caseStatus": "Unknown",
                "dateReceived": "2025-01-10T19:00:00-05:00",
                "fullName": "First",
            },
            {
                "caseStatus": "Unknown",
                "dateReceived": "2025-01-20T19:00:00-05:00",
                "fullName": "Second",
            },
        ]

        sorted_desc = sort_cases(test_cases, "desc", "Unknown")
        assert sorted_desc[0]["fullName"] == "Second"  # Latest dateReceived

    def test_paginate_cases(self, mock_data):
        """Test pagination functionality."""
        # Test first page
        page1, total_count = paginate_cases(mock_data, page=1, limit=2)
        assert len(page1) == 2
        assert total_count == 4

        # Test second page
        page2, total_count = paginate_cases(mock_data, page=2, limit=2)
        assert len(page2) == 2
        assert total_count == 4

        # Test third page (partial)
        page3, total_count = paginate_cases(mock_data, page=3, limit=2)
        assert len(page3) == 0
        assert total_count == 4

        # Test large limit
        all_cases, total_count = paginate_cases(mock_data, page=1, limit=10)
        assert len(all_cases) == 4
        assert total_count == 4

    def test_set_pagination_headers(self):
        """Test pagination headers are set correctly."""
        response = MagicMock(spec=Response)
        response.headers = {}

        set_pagination_headers(response, total_count=25, page=2, limit=10)

        assert (
            response.headers["Access-Control-Expose-Headers"]
            == "X-Total-Count, X-Page, X-Per-Page, X-Total-Pages"
        )
        assert response.headers["X-Total-Count"] == "25"
        assert response.headers["X-Page"] == "2"
        assert response.headers["X-Per-Page"] == "10"
        assert response.headers["X-Total-Pages"] == "3"  # ceil(25/10) = 3

    def test_get_cases_by_status(self, mock_data):
        """Test the generic get_cases_by_status function."""
        response = MagicMock(spec=Response)
        response.headers = {}

        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            # Test getting new cases
            new_cases = get_cases_by_status("New", response, "desc", 1, 10)
            assert len(new_cases) == 1
            assert isinstance(new_cases[0], MockCase)
            assert new_cases[0].fullName == "John Doe"

            # Test getting opened cases
            opened_cases = get_cases_by_status("Opened", response, "desc", 1, 10)
            assert len(opened_cases) == 1
            assert isinstance(opened_cases[0], MockCase)
            assert opened_cases[0].fullName == "Jane Smith"

            # Test pagination is set
            assert "X-Total-Count" in response.headers

    def test_update_case_by_reference_success(self, mock_data):
        """Test updating a case by reference only changes provided fields."""
        from app.routers.mock_data import update_case_by_reference

        # Patch load_mock_data to return mock_data, patch open for writing
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            m = mock_open()
            with patch("builtins.open", m):
                update_data = {"fullName": "Updated Name", "language": "Spanish"}
                updated = update_case_by_reference("PC-3184-5962", update_data)
                assert updated["fullName"] == "Updated Name"
                assert updated["language"] == "Spanish"
                # Unchanged fields remain
                assert updated["caseReference"] == "PC-3184-5962"
                # Check file write
                m.assert_called_once()

    def test_update_case_by_reference_not_found(self, mock_data):
        """Test updating a case by reference raises 404 if not found."""
        from app.routers.mock_data import update_case_by_reference

        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            with pytest.raises(HTTPException) as exc_info:
                update_case_by_reference("NON-EXISTENT-REF", {"fullName": "Nope"})
            assert exc_info.value.status_code == 404

    def test_search_cases_case_reference_exact_match(self, mock_data):
        """Test search by case reference (exact match, case-insensitive)."""
        # Test exact match
        results = search_cases(mock_data, "PC-3184-5962")
        assert len(results) == 1
        assert results[0]["fullName"] == "Ember Hamilton"

        # Test case-insensitive
        results = search_cases(mock_data, "pc-3184-5962")
        assert len(results) == 1
        assert results[0]["fullName"] == "Ember Hamilton"

        # Test partial match should not work for case reference
        results = search_cases(mock_data, "PC-3184")
        assert len(results) == 0

    def test_search_cases_phone_number_exact_match(self, mock_data):
        """Test search by phone number (exact match, ignore whitespace)."""
        # Test exact match
        results = search_cases(mock_data, "0776744581")
        assert len(results) == 1
        assert results[0]["fullName"] == "Ember Hamilton"

        # Test with spaces (should still match by ignoring spaces)
        results = search_cases(mock_data, "0776 744 581")
        assert len(results) == 1
        assert results[0]["fullName"] == "Ember Hamilton"

        # Test with different spacing format
        results = search_cases(mock_data, "07767 44581")
        assert len(results) == 1
        assert results[0]["fullName"] == "Ember Hamilton"

        # Test partial match should not work for phone number
        results = search_cases(mock_data, "0776")
        assert len(results) == 0

    def test_search_cases_full_name_partial_match(self, mock_data):
        """Test search by full name (partial match, case-insensitive)."""
        # Test partial match
        results = search_cases(mock_data, "John")
        assert len(results) == 1
        assert results[0]["fullName"] == "John Doe"

        # Test case-insensitive
        results = search_cases(mock_data, "jane")
        assert len(results) == 1
        assert results[0]["fullName"] == "Jane Smith"

        # Test full name match
        results = search_cases(mock_data, "Bob Wilson")
        assert len(results) == 1
        assert results[0]["fullName"] == "Bob Wilson"

    def test_search_cases_postcode_exact_match(self, mock_data):
        """Test search by postcode (exact match, case-insensitive, ignore whitespace)."""
        # Test exact match
        results = search_cases(mock_data, "B1 1DW")
        assert len(results) == 1
        assert results[0]["fullName"] == "Ember Hamilton"

        # Test case-insensitive
        results = search_cases(mock_data, "b1 1dw")
        assert len(results) == 1
        assert results[0]["fullName"] == "Ember Hamilton"

        # Test without space
        results = search_cases(mock_data, "B11DW")
        assert len(results) == 1
        assert results[0]["fullName"] == "Ember Hamilton"

        # Test partial match should not work for postcode
        results = search_cases(mock_data, "B1")
        assert len(results) == 0

    def test_search_cases_address_partial_match(self, mock_data):
        """Test search by address (partial match, case-insensitive)."""
        # Test partial match
        results = search_cases(mock_data, "Test Street")
        assert len(results) == 1
        assert results[0]["fullName"] == "John Doe"

        # Test case-insensitive
        results = search_cases(mock_data, "test avenue")
        assert len(results) == 1
        assert results[0]["fullName"] == "Jane Smith"

        # Test single word
        results = search_cases(mock_data, "Birmingham")
        assert len(results) == 1
        assert results[0]["fullName"] == "Ember Hamilton"

    def test_search_cases_no_matches(self, mock_data):
        """Test search with no matches."""
        results = search_cases(mock_data, "NonExistent")
        assert len(results) == 0

        results = search_cases(mock_data, "99999999")
        assert len(results) == 0

    def test_search_cases_multiple_matches(self):
        """Test search that could return multiple matches."""
        test_data = [
            {
                "fullName": "John Smith",
                "caseReference": "PC-1111-1111",
                "phoneNumber": "0777111111",
                "address": "123 Main Street, London",
                "postcode": "SW1 1AA",
            },
            {
                "fullName": "John Doe",
                "caseReference": "PC-2222-2222",
                "phoneNumber": "0777222222",
                "address": "456 High Street, London",
                "postcode": "SW1 2BB",
            },
        ]

        # Search by partial name should return both
        results = search_cases(test_data, "John")
        assert len(results) == 2

        # Search by city should return both
        results = search_cases(test_data, "London")
        assert len(results) == 2

    def test_search_cases_invalid_data(self):
        """Test search with invalid or empty data."""
        # Test with empty list
        results = search_cases([], "test")
        assert len(results) == 0

        # Test with invalid case data (missing caseReference)
        invalid_data = [
            {"fullName": "Test User"},  # Missing caseReference
            None,  # Null case
            "invalid",  # Not a dict
        ]
        results = search_cases(invalid_data, "Test")
        assert len(results) == 0

    def test_search_cases_empty_fields(self):
        """Test search with cases that have empty fields."""
        test_data = [
            {
                "fullName": "",
                "caseReference": "PC-1111-1111",
                "phoneNumber": "",
                "address": "",
                "postcode": "",
            },
        ]

        # Should not match empty fields
        results = search_cases(test_data, "")
        assert len(results) == 0

        # Should not match empty phone number with spaced search
        results = search_cases(test_data, "0777 123 456")
        assert len(results) == 0

        # Should match case reference
        results = search_cases(test_data, "PC-1111-1111")
        assert len(results) == 1


class TestMockDataEndpoints:
    """Test the mock data API endpoints."""

    def test_get_new_cases(self, client, mock_data):
        """Test get new cases endpoint."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.get("/latest/mock/cases/new")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

            # Check pagination headers
            assert "X-Total-Count" in response.headers
            assert "X-Page" in response.headers
            assert "X-Per-Page" in response.headers
            assert "X-Total-Pages" in response.headers

    def test_get_opened_cases(self, client, mock_data):
        """Test get opened cases endpoint."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.get("/latest/mock/cases/opened")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_get_accepted_cases(self, client, mock_data):
        """Test get accepted cases endpoint."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.get("/latest/mock/cases/accepted")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_get_closed_cases(self, client, mock_data):
        """Test get closed cases endpoint."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.get("/latest/mock/cases/closed")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_pagination_parameters(self, client, mock_data):
        """Test pagination parameters."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.get("/latest/mock/cases/accepted?page=1&limit=5")
            assert response.status_code == 200
            data = response.json()
            assert len(data) <= 5
            assert response.headers["X-Page"] == "1"
            assert response.headers["X-Per-Page"] == "5"

    def test_sorting_parameters(self, client, mock_data):
        """Test sorting parameters."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.get("/latest/mock/cases/accepted?sortOrder=desc")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_get_mock_case_by_reference(self, client, mock_data):
        """Test get mock case by reference endpoint."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            # Test success case
            response = client.get("/latest/mock/cases/PC-3184-5962")
            assert response.status_code == 200
            data = response.json()
            assert data["fullName"] == "Ember Hamilton"

            # Test not found case
            response = client.get("/latest/mock/cases/PC-0000-0000")
            assert response.status_code == 404

    def test_put_case_by_reference(self, client, mock_data):
        """Test updating a mock case by reference using PUT endpoint."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            m = mock_open()
            with patch("builtins.open", m):
                update_data = {"fullName": "Updated Name", "language": "Spanish"}
                response = client.put(
                    "/latest/mock/cases/PC-3184-5962", json=update_data
                )
                assert response.status_code == 200
                data = response.json()
                assert data["fullName"] == "Updated Name"
                assert data["language"] == "Spanish"
                assert data["caseReference"] == "PC-3184-5962"
                m.assert_called_once()

        # Test not found case
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.put(
                "/latest/mock/cases/NON-EXISTENT-REF", json={"fullName": "Nope"}
            )
            assert response.status_code == 404

    def test_search_mock_cases_endpoint(self, client, mock_data):
        """Test search mock cases endpoint.

        Note: Search endpoint sorts by lastModified date only, not by status-based date fields
        like the individual status endpoints (new, opened, accepted, closed).ƒ
        """
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            # Test basic search
            response = client.get("/latest/mock/cases/search?keyword=John")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["fullName"] == "John Doe"

            # Check pagination headers
            assert "X-Total-Count" in response.headers
            assert "X-Page" in response.headers
            assert "X-Per-Page" in response.headers
            assert "X-Total-Pages" in response.headers

    def test_search_mock_cases_with_status_filter(self, client, mock_data):
        """Test search with status filter."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            # Search for cases with specific status filter
            response = client.get("/latest/mock/cases/search?keyword=Test&status=New")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

            # Test 'all' status parameter returns results from all statuses
            test_data = [
                {
                    "fullName": "Test User New",
                    "caseReference": "PC-1111-1111",
                    "refCode": "",
                    "dateReceived": "2025-01-10T19:00:00-05:00",
                    "caseStatus": "New",
                    "dateOfBirth": "1990-01-01T00:00:00-05:00",
                    "clientIsVulnerable": False,
                    "reasonableAdjustments": {
                        "selected": [],
                        "available": [
                            "BSL - Webcam",
                            "Callback preference",
                            "Minicom",
                            "Skype",
                            "Text relay",
                            "No accommodations required",
                        ],
                        "additionalInfo": "",
                    },
                    "language": "English",
                    "phoneNumber": "0777111111",
                    "safeToCall": True,
                    "announceCall": False,
                    "emailAddress": "test1@email.com",
                    "address": "123 Test Street, London",
                    "postcode": "SW1 1AA",
                    "laaReference": "1111111",
                },
                {
                    "fullName": "Test User Opened",
                    "caseReference": "PC-2222-2222",
                    "refCode": "",
                    "dateReceived": "2025-01-10T19:00:00-05:00",
                    "lastModified": "2025-01-11T14:30:00-05:00",
                    "caseStatus": "Opened",
                    "dateOfBirth": "1990-01-01T00:00:00-05:00",
                    "clientIsVulnerable": False,
                    "reasonableAdjustments": {
                        "selected": [],
                        "available": [
                            "BSL - Webcam",
                            "Callback preference",
                            "Minicom",
                            "Skype",
                            "Text relay",
                            "No accommodations required",
                        ],
                        "additionalInfo": "",
                    },
                    "language": "English",
                    "phoneNumber": "0777222222",
                    "safeToCall": True,
                    "announceCall": False,
                    "emailAddress": "test2@email.com",
                    "address": "456 Test Avenue, London",
                    "postcode": "SW1 2BB",
                    "laaReference": "2222222",
                },
                {
                    "fullName": "Test User Accepted",
                    "caseReference": "PC-3333-3333",
                    "refCode": "",
                    "dateReceived": "2025-01-10T19:00:00-05:00",
                    "lastModified": "2025-01-11T14:30:00-05:00",
                    "caseStatus": "Accepted",
                    "dateOfBirth": "1990-01-01T00:00:00-05:00",
                    "clientIsVulnerable": False,
                    "reasonableAdjustments": {
                        "selected": [],
                        "available": [
                            "BSL - Webcam",
                            "Callback preference",
                            "Minicom",
                            "Skype",
                            "Text relay",
                            "No accommodations required",
                        ],
                        "additionalInfo": "",
                    },
                    "language": "English",
                    "phoneNumber": "0777333333",
                    "safeToCall": True,
                    "announceCall": False,
                    "emailAddress": "test3@email.com",
                    "address": "789 Test Road, London",
                    "postcode": "SW1 3CC",
                    "laaReference": "3333333",
                },
                {
                    "fullName": "Test User Closed",
                    "caseReference": "PC-4444-4444",
                    "refCode": "",
                    "dateReceived": "2025-01-10T19:00:00-05:00",
                    "lastModified": "2025-01-11T14:30:00-05:00",
                    "dateClosed": "2025-01-12T14:30:00-05:00",
                    "caseStatus": "Closed",
                    "dateOfBirth": "1990-01-01T00:00:00-05:00",
                    "clientIsVulnerable": False,
                    "reasonableAdjustments": {
                        "selected": [],
                        "available": [
                            "BSL - Webcam",
                            "Callback preference",
                            "Minicom",
                            "Skype",
                            "Text relay",
                            "No accommodations required",
                        ],
                        "additionalInfo": "",
                    },
                    "language": "English",
                    "phoneNumber": "0777444444",
                    "safeToCall": True,
                    "announceCall": False,
                    "emailAddress": "test4@email.com",
                    "address": "101 Test Boulevard, London",
                    "postcode": "SW1 4DD",
                    "laaReference": "4444444",
                },
            ]

            with patch("app.routers.mock_data.load_mock_data", return_value=test_data):
                # Should return all cases with 'all' status filter
                response = client.get(
                    "/latest/mock/cases/search?keyword=Test&status=all"
                )
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 4

                # Should return only New status cases with 'new' filter
                response = client.get(
                    "/latest/mock/cases/search?keyword=Test&status=new"
                )
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["fullName"] == "Test User New"

    def test_search_mock_cases_with_pagination(self, client, mock_data):
        """Test search with pagination parameters."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.get(
                "/latest/mock/cases/search?keyword=Test&page=1&limit=2"
            )
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) <= 2
            assert response.headers["X-Page"] == "1"
            assert response.headers["X-Per-Page"] == "2"

    def test_search_mock_cases_sorting_by_last_modified(self, client):
        """Test search endpoint sorts by lastModified date (not status-based sorting)."""
        # Create test data with different lastModified dates and all required fields
        test_data = [
            {
                "fullName": "Test User 1",
                "caseReference": "PC-1111-1111",
                "refCode": "",
                "phoneNumber": "0777111111",
                "address": "123 Test Street, London",
                "postcode": "SW1 1AA",
                "caseStatus": "New",
                "dateReceived": "2025-01-10T19:00:00-05:00",
                "lastModified": "2025-01-15T14:30:00-05:00",  # Middle date
                "dateOfBirth": "1990-01-01T00:00:00-05:00",
                "clientIsVulnerable": False,
                "reasonableAdjustments": {
                    "selected": [],
                    "available": [
                        "BSL - Webcam",
                        "Callback preference",
                        "Minicom",
                        "Skype",
                        "Text relay",
                        "No accommodations required",
                    ],
                    "additionalInfo": "",
                },
                "language": "English",
                "safeToCall": True,
                "announceCall": False,
                "emailAddress": "test1@email.com",
                "laaReference": "1111111",
            },
            {
                "fullName": "Test User 2",
                "caseReference": "PC-2222-2222",
                "refCode": "",
                "phoneNumber": "0777222222",
                "address": "456 Test Avenue, London",
                "postcode": "SW1 2BB",
                "caseStatus": "Opened",
                "dateReceived": "2025-01-05T19:00:00-05:00",
                "lastModified": "2025-01-20T14:30:00-05:00",  # Latest date
                "dateOfBirth": "1990-01-01T00:00:00-05:00",
                "clientIsVulnerable": False,
                "reasonableAdjustments": {
                    "selected": [],
                    "available": [
                        "BSL - Webcam",
                        "Callback preference",
                        "Minicom",
                        "Skype",
                        "Text relay",
                        "No accommodations required",
                    ],
                    "additionalInfo": "",
                },
                "language": "English",
                "safeToCall": True,
                "announceCall": False,
                "emailAddress": "test2@email.com",
                "laaReference": "2222222",
            },
            {
                "fullName": "Test User 3",
                "caseReference": "PC-3333-3333",
                "refCode": "",
                "phoneNumber": "0777333333",
                "address": "789 Test Road, London",
                "postcode": "SW1 3CC",
                "caseStatus": "Closed",
                "dateReceived": "2025-01-01T19:00:00-05:00",
                "lastModified": "2025-01-10T14:30:00-05:00",  # Earliest date
                "dateClosed": "2025-01-12T14:30:00-05:00",
                "dateOfBirth": "1990-01-01T00:00:00-05:00",
                "clientIsVulnerable": False,
                "reasonableAdjustments": {
                    "selected": [],
                    "available": [
                        "BSL - Webcam",
                        "Callback preference",
                        "Minicom",
                        "Skype",
                        "Text relay",
                        "No accommodations required",
                    ],
                    "additionalInfo": "",
                },
                "language": "English",
                "safeToCall": True,
                "announceCall": False,
                "emailAddress": "test3@email.com",
                "laaReference": "3333333",
            },
        ]

        with patch("app.routers.mock_data.load_mock_data", return_value=test_data):
            # Test descending order (default) - should sort by lastModified regardless of status
            response = client.get(
                "/latest/mock/cases/search?keyword=Test&sortOrder=desc"
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 3
            # Should be sorted by lastModified desc: User 2 (latest), User 1 (middle), User 3 (earliest)
            assert data[0]["fullName"] == "Test User 2"  # Latest lastModified
            assert data[1]["fullName"] == "Test User 1"  # Middle lastModified
            assert data[2]["fullName"] == "Test User 3"  # Earliest lastModified

            # Test ascending order
            response = client.get(
                "/latest/mock/cases/search?keyword=Test&sortOrder=asc"
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 3
            # Should be sorted by lastModified asc: User 3 (earliest), User 1 (middle), User 2 (latest)
            assert data[0]["fullName"] == "Test User 3"  # Earliest lastModified
            assert data[1]["fullName"] == "Test User 1"  # Middle lastModified
            assert data[2]["fullName"] == "Test User 2"  # Latest lastModified

    def test_search_mock_cases_no_results(self, client, mock_data):
        """Test search with no matching results."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.get("/latest/mock/cases/search?keyword=NonExistent")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 0
            assert response.headers["X-Total-Count"] == "0"

    def test_search_mock_cases_missing_keyword(self, client):
        """Test search endpoint without keyword parameter."""
        response = client.get("/latest/mock/cases/search")
        assert response.status_code == 422  # Validation error

    def test_search_mock_cases_by_case_reference(self, client, mock_data):
        """Test search by case reference."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.get("/latest/mock/cases/search?keyword=PC-3184-5962")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["caseReference"] == "PC-3184-5962"
            assert data[0]["fullName"] == "Ember Hamilton"

    def test_search_mock_cases_by_phone_number(self, client, mock_data):
        """Test search by phone number."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            # Test exact match without spaces
            response = client.get("/latest/mock/cases/search?keyword=0777123456")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["phoneNumber"] == "0777123456"
            assert data[0]["fullName"] == "John Doe"

            # Test match with spaces (should ignore spaces in phone number)
            response = client.get("/latest/mock/cases/search?keyword=0777%20123%20456")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["phoneNumber"] == "0777123456"
            assert data[0]["fullName"] == "John Doe"

    def test_search_mock_cases_by_postcode(self, client, mock_data):
        """Test search by postcode."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.get("/latest/mock/cases/search?keyword=SW1%201AA")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["postcode"] == "SW1 1AA"
            assert data[0]["fullName"] == "John Doe"

    def test_search_mock_cases_by_address(self, client, mock_data):
        """Test search by address."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.get("/latest/mock/cases/search?keyword=Birmingham")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert "Birmingham" in data[0]["address"]
            assert data[0]["fullName"] == "Ember Hamilton"


class TestMockCaseModel:
    """Test the MockCase Pydantic model."""

    def test_mock_case_valid_data(self):
        """Test creating MockCase with valid data."""
        case_data = {
            "fullName": "Test User",
            "caseReference": "PC-1234-5678",
            "refCode": "",
            "dateReceived": "2025-01-08T19:00:00-05:00",
            "lastModified": "2025-01-09T14:30:00-05:00",
            "caseStatus": "Accepted",
            "dateOfBirth": "1990-01-15T00:00:00-05:00",
            "clientIsVulnerable": False,
            "reasonableAdjustments": {
                "selected": [],
                "available": [
                    "BSL - Webcam",
                    "Callback preference",
                    "Minicom",
                    "Skype",
                    "Text relay",
                    "No accommodations required",
                ],
                "additionalInfo": "",
            },
            "language": "English",
            "phoneNumber": "0777123456",
            "safeToCall": True,
            "announceCall": False,
            "emailAddress": "test.user@email.com",
            "address": "123 Test Street, London",
            "postcode": "SW1 1AA",
            "laaReference": "1234567",
        }

        mock_case = MockCase(**case_data)
        assert mock_case.fullName == "Test User"
        assert mock_case.caseReference == "PC-1234-5678"
        assert mock_case.dateOfBirth == "1990-01-15T00:00:00-05:00"

    def test_mock_case_with_ref_code(self):
        """Test creating MockCase with ref code."""
        case_data = {
            "fullName": "Test User",
            "caseReference": "PC-1234-5678",
            "refCode": "Operator recommends second opinion",
            "dateReceived": "2025-01-08T19:00:00-05:00",
            "lastModified": "2025-01-09T14:30:00-05:00",
            "caseStatus": "Accepted",
            "dateOfBirth": "1990-01-15T00:00:00-05:00",
            "clientIsVulnerable": False,
            "reasonableAdjustments": {
                "selected": [],
                "available": [
                    "BSL - Webcam",
                    "Callback preference",
                    "Minicom",
                    "Skype",
                    "Text relay",
                    "No accommodations required",
                ],
                "additionalInfo": "",
            },
            "language": "English",
            "phoneNumber": "0777123456",
            "safeToCall": True,
            "announceCall": False,
            "emailAddress": "test.user@email.com",
            "address": "123 Test Street, London",
            "postcode": "SW1 1AA",
            "laaReference": "1234567",
        }

        mock_case = MockCase(**case_data)
        assert mock_case.refCode == "Operator recommends second opinion"

    def test_mock_case_with_date_closed(self):
        """Test creating MockCase with dateClosed field."""
        case_data = {
            "fullName": "Test User",
            "caseReference": "PC-1234-5678",
            "refCode": "",
            "dateReceived": "2025-01-08T19:00:00-05:00",
            "lastModified": "2025-01-09T14:30:00-05:00",
            "dateClosed": "2025-01-10T14:30:00-05:00",
            "caseStatus": "Closed",
            "dateOfBirth": "1990-01-15T00:00:00-05:00",
            "clientIsVulnerable": False,
            "reasonableAdjustments": {
                "selected": [],
                "available": [
                    "BSL - Webcam",
                    "Callback preference",
                    "Minicom",
                    "Skype",
                    "Text relay",
                    "No accommodations required",
                ],
                "additionalInfo": "",
            },
            "language": "English",
            "phoneNumber": "0777123456",
            "safeToCall": True,
            "announceCall": False,
            "emailAddress": "test.user@email.com",
            "address": "123 Test Street, London",
            "postcode": "SW1 1AA",
            "laaReference": "1234567",
        }

        mock_case = MockCase(**case_data)
        assert mock_case.dateClosed == "2025-01-10T14:30:00-05:00"

    def test_mock_case_new_status(self):
        """Test creating MockCase with New status (no lastModified)."""
        case_data = {
            "fullName": "Test User",
            "caseReference": "PC-1234-5678",
            "refCode": "",
            "dateReceived": "2025-01-08T19:00:00-05:00",
            "caseStatus": "New",
            "dateOfBirth": "1990-01-15T00:00:00-05:00",
            "clientIsVulnerable": False,
            "reasonableAdjustments": {
                "selected": [],
                "available": [
                    "BSL - Webcam",
                    "Callback preference",
                    "Minicom",
                    "Skype",
                    "Text relay",
                    "No accommodations required",
                ],
                "additionalInfo": "",
            },
            "language": "English",
            "phoneNumber": "0777123456",
            "safeToCall": True,
            "announceCall": False,
            "emailAddress": "test.user@email.com",
            "address": "123 Test Street, London",
            "postcode": "SW1 1AA",
            "laaReference": "1234567",
        }

        mock_case = MockCase(**case_data)
        assert mock_case.caseStatus == "New"
        assert mock_case.lastModified is None
