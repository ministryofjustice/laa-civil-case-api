"""
Tests for helper functions in mock_data.py.
"""

import pytest
import json
from unittest.mock import patch, mock_open, MagicMock
from fastapi import HTTPException

from app.routers.mock_data import (
    load_mock_data,
    filter_cases_by_status,
    sort_cases,
    paginate_cases,
    set_pagination_headers,
    search_cases,
    find_case_by_reference,
    save_cases_to_file,
    update_case_by_reference,
)


class TestLoadMockData:
    """Test the load_mock_data function."""

    def test_load_mock_data_success(self, mock_data):
        """Test successful loading of mock data."""
        mock_json_data = json.dumps(mock_data)
        mock_file = mock_open(read_data=mock_json_data)

        with patch("builtins.open", mock_file):
            with patch("pathlib.Path.exists", return_value=True):
                result = load_mock_data()

        assert result == mock_data
        mock_file.assert_called_once()

    def test_load_mock_data_file_not_found(self):
        """Test loading when file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                load_mock_data()

        assert exc_info.value.status_code == 404
        assert "Mock data file not found" in str(exc_info.value.detail)

    def test_load_mock_data_invalid_json(self):
        """Test loading with invalid JSON."""
        mock_file = mock_open(read_data="invalid json")

        with patch("builtins.open", mock_file):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(HTTPException) as exc_info:
                    load_mock_data()

        assert exc_info.value.status_code == 500
        assert "Invalid JSON in mock data file" in str(exc_info.value.detail)

    def test_load_mock_data_general_exception(self):
        """Test loading with general exception."""
        with patch("builtins.open", side_effect=Exception("File read error")):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(HTTPException) as exc_info:
                    load_mock_data()

        assert exc_info.value.status_code == 500
        assert "Error loading mock data" in str(exc_info.value.detail)


class TestHelperFunctions:
    """Test the helper functions in mock_data.py."""

    def test_filter_cases_by_status(self, mock_data):
        """Test filtering cases by status."""
        # Test filtering by "New" status
        new_cases = filter_cases_by_status(mock_data, "New")
        assert len(new_cases) == 1
        assert new_cases[0]["caseStatus"] == "New"

        # Test filtering by "all" status
        all_cases = filter_cases_by_status(mock_data, "all")
        assert len(all_cases) == len(mock_data)

        # Test case insensitive filtering
        accepted_cases = filter_cases_by_status(mock_data, "ACCEPTED")
        assert len(accepted_cases) == 1
        assert accepted_cases[0]["caseStatus"] == "Accepted"

    def test_sort_cases_new_status(self, mock_data):
        """Test sorting cases with 'New' status (by dateReceived)."""
        sorted_cases = sort_cases(mock_data, "asc", "New")
        dates = [case["dateReceived"] for case in sorted_cases]
        assert dates == sorted(dates)

        sorted_cases_desc = sort_cases(mock_data, "desc", "New")
        dates_desc = [case["dateReceived"] for case in sorted_cases_desc]
        assert dates_desc == sorted(dates_desc, reverse=True)

    def test_sort_cases_opened_accepted_status(self, mock_data):
        """Test sorting cases with 'Opened' or 'Accepted' status (by lastModified)."""
        sorted_cases = sort_cases(mock_data, "asc", "Opened")
        dates = [case["lastModified"] for case in sorted_cases]
        assert dates == sorted(dates)

    def test_sort_cases_closed_status(self, mock_data):
        """Test sorting cases with 'Closed' status (by dateClosed)."""
        sorted_cases = sort_cases(mock_data, "asc", "Closed")
        # Filter only closed cases for this test
        closed_cases = [case for case in sorted_cases if case.get("dateClosed")]
        dates = [case["dateClosed"] for case in closed_cases]
        assert dates == sorted(dates)

    def test_sort_cases_unknown_status(self, mock_data):
        """Test sorting cases with unknown status (defaults to dateReceived)."""
        sorted_cases = sort_cases(mock_data, "asc", "Unknown")
        dates = [case["dateReceived"] for case in sorted_cases]
        assert dates == sorted(dates)

    def test_paginate_cases(self, mock_data):
        """Test pagination of cases."""
        # Test first page
        page_1, total = paginate_cases(mock_data, page=1, limit=2)
        assert len(page_1) == 2
        assert total == len(mock_data)

        # Test second page
        page_2, total = paginate_cases(mock_data, page=2, limit=2)
        assert len(page_2) == 2
        assert total == len(mock_data)

        # Test page beyond available data
        page_3, total = paginate_cases(mock_data, page=3, limit=2)
        assert len(page_3) == 0
        assert total == len(mock_data)

    def test_set_pagination_headers(self):
        """Test setting pagination headers."""
        response = MagicMock()
        response.headers = {}

        set_pagination_headers(response, total_count=10, page=1, limit=5)

        expected_headers = {
            "Access-Control-Expose-Headers": "X-Total-Count, X-Page, X-Per-Page, X-Total-Pages",
            "X-Total-Count": "10",
            "X-Page": "1",
            "X-Per-Page": "5",
            "X-Total-Pages": "2",
        }

        for key, value in expected_headers.items():
            assert response.headers[key] == value

    def test_find_case_by_reference_success(self, mock_data):
        """Test finding a case by reference successfully."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            case, index, cases = find_case_by_reference("PC-3184-5962")

        assert case["caseReference"] == "PC-3184-5962"
        assert case["fullName"] == "Ember Hamilton"
        assert index == 0
        assert cases == mock_data

    def test_find_case_by_reference_not_found(self, mock_data):
        """Test finding a case by reference when not found."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            with pytest.raises(HTTPException) as exc_info:
                find_case_by_reference("PC-9999-9999")

        assert exc_info.value.status_code == 404
        assert "Case with reference 'PC-9999-9999' not found" in str(
            exc_info.value.detail
        )

    def test_save_cases_to_file_success(self, mock_data):
        """Test saving cases to file successfully."""
        mock_file = mock_open()

        with patch("builtins.open", mock_file):
            save_cases_to_file(mock_data)

        mock_file.assert_called_once()
        # Verify that json.dump was called
        handle = mock_file()
        handle.write.assert_called()

    def test_save_cases_to_file_error(self, mock_data):
        """Test saving cases to file with error."""
        with patch("builtins.open", side_effect=Exception("Write error")):
            with pytest.raises(HTTPException) as exc_info:
                save_cases_to_file(mock_data)

        assert exc_info.value.status_code == 500
        assert "Error saving data" in str(exc_info.value.detail)

    def test_update_case_by_reference_success(self, mock_data):
        """Test updating a case by reference successfully."""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            with patch("app.routers.mock_data.save_cases_to_file") as mock_save:
                test_case = mock_data[0].copy()
                mock_find.return_value = (test_case, 0, mock_data)

                result = update_case_by_reference(
                    "PC-3184-5962", {"fullName": "Updated Name"}
                )

        assert result["fullName"] == "Updated Name"
        assert result["caseReference"] == "PC-3184-5962"
        mock_find.assert_called_once_with("PC-3184-5962")
        mock_save.assert_called_once()

    def test_update_case_by_reference_not_found(self, mock_data):
        """Test updating a case by reference when not found."""
        with patch("app.routers.mock_data.find_case_by_reference") as mock_find:
            mock_find.side_effect = HTTPException(
                status_code=404, detail="Case with reference 'PC-9999-9999' not found"
            )

            with pytest.raises(HTTPException) as exc_info:
                update_case_by_reference("PC-9999-9999", {"fullName": "Updated Name"})

        assert exc_info.value.status_code == 404
        assert "Case with reference 'PC-9999-9999' not found" in str(
            exc_info.value.detail
        )


class TestSearchCases:
    """Test the search_cases function."""

    def test_search_cases_case_reference_exact_match(self, mock_search_data):
        """Test searching by case reference (exact match)."""
        results = search_cases(mock_search_data, "PC-1234-5678")
        assert len(results) == 1
        assert results[0]["caseReference"] == "PC-1234-5678"

    def test_search_cases_phone_number_exact_match(self, mock_search_data):
        """Test searching by phone number (exact match, ignoring spaces)."""
        # Test with spaces
        results = search_cases(mock_search_data, "0777 123 456")
        assert len(results) == 1
        assert results[0]["phoneNumber"] == "0777 123 456"

        # Test without spaces
        results = search_cases(mock_search_data, "07771234567")
        assert len(results) == 0  # No exact match for this number

        # Test partial phone number (should not match as it's exact match)
        results = search_cases(mock_search_data, "0777")
        assert len(results) == 0

    def test_search_cases_full_name_partial_match(self, mock_search_data):
        """Test searching by full name (partial match)."""
        results = search_cases(mock_search_data, "John")
        assert len(results) == 1
        assert results[0]["fullName"] == "John Smith"

        results = search_cases(mock_search_data, "Smith")
        assert len(results) == 1
        assert results[0]["fullName"] == "John Smith"

    def test_search_cases_postcode_exact_match(self, mock_search_data):
        """Test searching by postcode (exact match, ignoring spaces)."""
        # Test with spaces
        results = search_cases(mock_search_data, "SW1A 1AA")
        assert len(results) == 1
        assert results[0]["postcode"] == "SW1A 1AA"

        # Test without spaces
        results = search_cases(mock_search_data, "SW1A1AA")
        assert len(results) == 1
        assert results[0]["postcode"] == "SW1A 1AA"

    def test_search_cases_address_partial_match(self, mock_search_data):
        """Test searching by address (partial match)."""
        results = search_cases(mock_search_data, "Main Street")
        assert len(results) == 1
        assert results[0]["address"] == "123 Main Street, London"

        results = search_cases(mock_search_data, "London")
        assert len(results) == 1
        assert results[0]["address"] == "123 Main Street, London"

    def test_search_cases_no_matches(self, mock_search_data):
        """Test searching with no matches."""
        results = search_cases(mock_search_data, "NonexistentKeyword")
        assert len(results) == 0

    def test_search_cases_empty_keyword(self, mock_search_data):
        """Test searching with empty keyword."""
        results = search_cases(mock_search_data, "")
        assert len(results) == 0

        results = search_cases(mock_search_data, "   ")
        assert len(results) == 0

    def test_search_cases_multiple_matches(self):
        """Test searching with multiple matches."""
        test_data = [
            {
                "fullName": "John Smith",
                "caseReference": "PC-1111-1111",
                "phoneNumber": "01234567890",
                "address": "123 Main Street",
                "postcode": "SW1A 1AA",
                "caseStatus": "New",
            },
            {
                "fullName": "Jane Smith",
                "caseReference": "PC-2222-2222",
                "phoneNumber": "09876543210",
                "address": "456 Oak Street",
                "postcode": "M1 1AA",
                "caseStatus": "Opened",
            },
        ]

        results = search_cases(test_data, "Smith")
        assert len(results) == 2

    def test_search_cases_invalid_data(self):
        """Test searching with invalid case data."""
        invalid_data = [
            {"fullName": "Valid Case", "caseReference": "PC-1111-1111"},
            {"fullName": "No Reference"},  # Missing caseReference
            None,  # Invalid case
            {},  # Empty case
        ]

        results = search_cases(invalid_data, "Valid")
        assert len(results) == 1
        assert results[0]["fullName"] == "Valid Case"

    def test_search_cases_empty_fields(self):
        """Test searching with cases that have empty fields."""
        test_data = [
            {
                "fullName": "",
                "caseReference": "PC-1111-1111",
                "phoneNumber": "",
                "address": "",
                "postcode": "",
            }
        ]

        results = search_cases(test_data, "PC-1111-1111")
        assert len(results) == 1
