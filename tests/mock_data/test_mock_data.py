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
