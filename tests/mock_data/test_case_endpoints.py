"""
Tests for case endpoints in mock_data.py.
"""

from unittest.mock import patch

from app.routers.mock_data import (
    get_cases_by_status,
    filter_cases_by_status,
)
from app.models.mock_case import MockCase


class TestCaseEndpoints:
    """Test the case-related API endpoints."""

    def test_get_new_cases(self, client, mock_data):
        """Test GET /mock/cases/new endpoint."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.get("/latest/mock/cases/new")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Check that pagination headers are set
        assert "X-Total-Count" in response.headers
        assert "X-Page" in response.headers
        assert "X-Per-Page" in response.headers
        assert "X-Total-Pages" in response.headers

    def test_get_new_cases_with_pagination(self, client, mock_data):
        """Test GET /mock/cases/new endpoint with pagination."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.get("/latest/mock/cases/new?page=1&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2
        assert response.headers["X-Per-Page"] == "2"

    def test_get_new_cases_with_sorting(self, client, mock_data):
        """Test GET /mock/cases/new endpoint with sorting."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.get("/latest/mock/cases/new?sortOrder=asc")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_opened_cases(self, client, mock_data):
        """Test GET /mock/cases/opened endpoint."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.get("/latest/mock/cases/opened")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_accepted_cases(self, client, mock_data):
        """Test GET /mock/cases/accepted endpoint."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.get("/latest/mock/cases/accepted")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_closed_cases(self, client, mock_data):
        """Test GET /mock/cases/closed endpoint."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.get("/latest/mock/cases/closed")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_case_by_reference_success(self, client, mock_data):
        """Test GET /mock/cases/{case_reference} endpoint with valid case reference."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            response = client.get("/latest/mock/cases/PC-3184-5962")

            assert response.status_code == 200
            data = response.json()
            assert data["caseReference"] == "PC-3184-5962"

    def test_get_case_by_reference_not_found(self, client):
        """Test GET /mock/cases/{case_reference} endpoint with invalid case reference."""
        with patch("app.routers.mock_data.load_mock_data", return_value=[]):
            response = client.get("/latest/mock/cases/PC-9999-9999")

            assert response.status_code == 404
            assert (
                "Case with reference 'PC-9999-9999' not found"
                in response.json()["detail"]
            )

    def test_update_case_by_reference_success(self, client, mock_data):
        """Test PUT /mock/cases/{case_reference} endpoint with valid data."""
        with patch("app.routers.mock_data.update_case_by_reference") as mock_update:
            updated_case = mock_data[0].copy()
            updated_case["fullName"] = "Updated Name"
            mock_update.return_value = updated_case

            response = client.put(
                "/latest/mock/cases/PC-3184-5962", json={"fullName": "Updated Name"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["fullName"] == "Updated Name"
        assert data["caseReference"] == "PC-3184-5962"

    def test_update_case_by_reference_not_found(self, client):
        """Test PUT /mock/cases/{case_reference} endpoint with invalid case reference."""
        with patch("app.routers.mock_data.load_mock_data", return_value=[]):
            response = client.put(
                "/latest/mock/cases/PC-9999-9999",
                json={"case_type": "CLA", "status": "closed"},
            )

            assert response.status_code == 404
            assert (
                "Case with reference 'PC-9999-9999' not found"
                in response.json()["detail"]
            )

    def test_search_cases_success(self, client, mock_search_data):
        """Test GET /mock/cases/search endpoint with valid keyword."""
        with patch(
            "app.routers.mock_data.load_mock_data", return_value=mock_search_data
        ):
            response = client.get("/latest/mock/cases/search?keyword=John")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 0

    def test_search_cases_with_status_filter(self, client, mock_search_data):
        """Test search with status filter."""
        with patch(
            "app.routers.mock_data.load_mock_data", return_value=mock_search_data
        ):
            response = client.get("/latest/mock/cases/search?keyword=John&status=New")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_search_cases_with_pagination(self, client, mock_search_data):
        """Test search with pagination parameters."""
        with patch(
            "app.routers.mock_data.load_mock_data", return_value=mock_search_data
        ):
            response = client.get(
                "/latest/mock/cases/search?keyword=John&page=1&limit=5"
            )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert response.headers["X-Per-Page"] == "5"

    def test_search_cases_with_sorting(self, client, mock_search_data):
        """Test search with sorting parameters."""
        with patch(
            "app.routers.mock_data.load_mock_data", return_value=mock_search_data
        ):
            response = client.get(
                "/latest/mock/cases/search?keyword=John&sortOrder=asc"
            )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_search_cases_missing_keyword(self, client):
        """Test search endpoint without keyword parameter."""
        response = client.get("/latest/mock/cases/search")
        assert (
            response.status_code == 422
        )  # Validation error for missing required parameter

    def test_search_cases_empty_keyword(self, client, mock_search_data):
        """Test search endpoint with empty keyword."""
        with patch(
            "app.routers.mock_data.load_mock_data", return_value=mock_search_data
        ):
            response = client.get("/latest/mock/cases/search?keyword=")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0  # Empty keyword should return no results

    def test_search_cases_all_status_filter(self, client, mock_search_data):
        """Test search with 'all' status filter."""
        with patch(
            "app.routers.mock_data.load_mock_data", return_value=mock_search_data
        ):
            response = client.get("/latest/mock/cases/search?keyword=John&status=all")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestCaseStatusFiltering:
    """Test case status filtering functionality."""

    def test_get_cases_by_status_function(self, mock_data):
        """Test the get_cases_by_status utility function."""
        with patch("app.routers.mock_data.load_mock_data", return_value=mock_data):
            from fastapi import Response

            response_mock = Response()
            result = get_cases_by_status("New", response_mock)

        assert isinstance(result, list)
        assert all(isinstance(case, MockCase) for case in result)

    def test_filter_new_cases(self, mock_data):
        """Test filtering for new cases."""
        new_cases = filter_cases_by_status(mock_data, "New")
        for case in new_cases:
            assert case["caseStatus"] == "New"

    def test_filter_opened_cases(self, mock_data):
        """Test filtering for opened cases."""
        opened_cases = filter_cases_by_status(mock_data, "Opened")
        for case in opened_cases:
            assert case["caseStatus"] == "Opened"

    def test_filter_accepted_cases(self, mock_data):
        """Test filtering for accepted cases."""
        accepted_cases = filter_cases_by_status(mock_data, "Accepted")
        for case in accepted_cases:
            assert case["caseStatus"] == "Accepted"

    def test_filter_closed_cases(self, mock_data):
        """Test filtering for closed cases."""
        closed_cases = filter_cases_by_status(mock_data, "Closed")
        for case in closed_cases:
            assert case["caseStatus"] == "Closed"

    def test_filter_all_cases(self, mock_data):
        """Test filtering with 'all' status returns all cases."""
        all_cases = filter_cases_by_status(mock_data, "all")
        assert len(all_cases) == len(mock_data)

    def test_filter_case_insensitive(self, mock_data):
        """Test that status filtering is case insensitive."""
        new_cases_lower = filter_cases_by_status(mock_data, "new")
        new_cases_upper = filter_cases_by_status(mock_data, "NEW")
        new_cases_mixed = filter_cases_by_status(mock_data, "New")

        assert len(new_cases_lower) == len(new_cases_upper) == len(new_cases_mixed)
