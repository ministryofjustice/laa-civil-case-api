import json
import math
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from pathlib import Path
from ..models.mock_case import MockCase

router = APIRouter(
    prefix="/mock",
    tags=["mock"],
    responses={404: {"description": "Not found"}},
)


def load_mock_data() -> List[Dict[str, Any]]:
    """Load mock case data from JSON file."""
    mock_data_path = Path(__file__).parent.parent / "data" / "mock_cases.json"

    if not mock_data_path.exists():
        raise HTTPException(status_code=404, detail="Mock data file not found")

    try:
        with open(mock_data_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in mock data file")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error loading mock data: {str(e)}"
        )


def filter_cases_by_status(
    cases: List[Dict[str, Any]], status: str
) -> List[Dict[str, Any]]:
    """Filter cases by status."""
    return [
        case for case in cases if case.get("caseStatus", "").lower() == status.lower()
    ]


def sort_cases(
    cases: List[Dict[str, Any]], sort_order: str, status: str
) -> List[Dict[str, Any]]:
    """Sort cases by appropriate date field for each status."""

    def get_date_received(case):
        return case.get("dateReceived", "")

    def get_last_modified(case):
        return case.get("lastModified", "")

    def get_date_closed(case):
        return case.get("dateClosed", "")

    # Use different date fields based on case status
    if status.lower() == "new":
        key_func = get_date_received
    elif status.lower() in ["opened", "accepted"]:
        key_func = get_last_modified
    elif status.lower() == "closed":
        key_func = get_date_closed
    else:
        # Default to dateReceived if unknown status
        key_func = get_date_received

    reverse = sort_order.lower() == "desc"
    return sorted(cases, key=key_func, reverse=reverse)


def paginate_cases(
    cases: List[Dict[str, Any]], page: int, limit: int
) -> tuple[List[Dict[str, Any]], int]:
    """Paginate cases and return the subset with total count."""
    total_count = len(cases)
    start_index = (page - 1) * limit
    end_index = start_index + limit
    return cases[start_index:end_index], total_count


def set_pagination_headers(response: Response, total_count: int, page: int, limit: int):
    """Set pagination headers in the response."""
    total_pages = math.ceil(total_count / limit) if limit > 0 else 1

    response.headers["Access-Control-Expose-Headers"] = (
        "X-Total-Count, X-Page, X-Per-Page, X-Total-Pages"
    )
    response.headers["X-Total-Count"] = str(total_count)
    response.headers["X-Page"] = str(page)
    response.headers["X-Per-Page"] = str(limit)
    response.headers["X-Total-Pages"] = str(total_pages)


def get_cases_by_status(
    status: str,
    response: Response,
    sortOrder: str = "desc",
    page: int = 1,
    limit: int = 10,
) -> List[MockCase]:
    """Generic function to get cases by status with pagination and sorting."""
    all_cases = load_mock_data()
    filtered_cases = filter_cases_by_status(all_cases, status)
    sorted_cases = sort_cases(filtered_cases, sortOrder, status)
    paginated_cases, total_count = paginate_cases(sorted_cases, page, limit)

    set_pagination_headers(response, total_count, page, limit)
    return [MockCase(**case) for case in paginated_cases]


@router.get(
    "/cases/new",
    tags=["mock"],
    response_model=List[MockCase],
    summary="Get new mock cases",
    description="Returns new mock cases with pagination and sorting",
)
async def get_new_cases(
    response: Response,
    sortOrder: Optional[str] = Query("desc", description="Sort order 'asc' or 'desc'"),
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    limit: int = Query(10, ge=1, le=100, description="Number of records per page"),
) -> List[MockCase]:
    """Get new cases with pagination and sorting."""
    return get_cases_by_status("New", response, sortOrder, page, limit)


@router.get(
    "/cases/opened",
    tags=["mock"],
    response_model=List[MockCase],
    summary="Get opened mock cases",
    description="Returns opened mock cases with pagination and sorting",
)
async def get_opened_cases(
    response: Response,
    sortOrder: Optional[str] = Query("desc", description="Sort order 'asc' or 'desc'"),
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    limit: int = Query(10, ge=1, le=100, description="Number of records per page"),
) -> List[MockCase]:
    """Get opened cases with pagination and sorting."""
    return get_cases_by_status("Opened", response, sortOrder, page, limit)


@router.get(
    "/cases/accepted",
    tags=["mock"],
    response_model=List[MockCase],
    summary="Get accepted mock cases",
    description="Returns accepted mock cases with pagination and sorting",
)
async def get_accepted_cases(
    response: Response,
    sortOrder: Optional[str] = Query("desc", description="Sort order 'asc' or 'desc'"),
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    limit: int = Query(10, ge=1, le=100, description="Number of records per page"),
) -> List[MockCase]:
    """Get accepted cases with pagination and sorting."""
    return get_cases_by_status("Accepted", response, sortOrder, page, limit)


@router.get(
    "/cases/closed",
    tags=["mock"],
    response_model=List[MockCase],
    summary="Get closed mock cases",
    description="Returns closed mock cases with pagination and sorting",
)
async def get_closed_cases(
    response: Response,
    sortOrder: Optional[str] = Query("desc", description="Sort order 'asc' or 'desc'"),
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    limit: int = Query(10, ge=1, le=100, description="Number of records per page"),
) -> List[MockCase]:
    """Get closed cases with pagination and sorting."""
    return get_cases_by_status("Closed", response, sortOrder, page, limit)


@router.get(
    "/cases/{case_reference}",
    tags=["mock"],
    response_model=MockCase,
    summary="Get mock case by reference",
    description="Returns a specific mock case by case reference",
)
async def get_mock_case_by_reference(case_reference: str) -> MockCase:
    """Get a specific mock case by case reference."""
    mock_data = load_mock_data()

    for case in mock_data:
        if case.get("caseReference") == case_reference:
            return MockCase(**case)

    raise HTTPException(
        status_code=404, detail=f"Case with reference '{case_reference}' not found"
    )
