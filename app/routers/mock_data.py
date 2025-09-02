import json
import math
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Response, Body
from pathlib import Path
from ..models.mock_case import MockCase, ThirdPartyCreate, ThirdPartyUpdate

router = APIRouter(
    prefix="/mock",
    tags=["mock"],
    responses={404: {"description": "Not found"}},
)

MOCK_DATA_PATH = Path(__file__).parent.parent / "data" / "mock_cases.json"


def load_mock_data() -> List[Dict[str, Any]]:
    """Load mock case data from JSON file."""
    if not MOCK_DATA_PATH.exists():
        raise HTTPException(status_code=404, detail="Mock data file not found")

    if not MOCK_DATA_PATH.exists():
        raise HTTPException(status_code=404, detail="Mock data file not found")

    try:
        with open(MOCK_DATA_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in mock data file")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error loading mock data: {str(e)}"
        )


def update_case_by_reference(case_reference: str, update_data: dict) -> dict:
    """Update a case in the JSON file by reference, only changing provided fields."""
    target_case, case_index, cases = find_case_by_reference(case_reference)

    for key, value in update_data.items():
        target_case[key] = value

    cases[case_index] = target_case
    save_cases_to_file(cases)
    return target_case


def find_case_by_reference(
    case_reference: str,
) -> tuple[dict, int, List[Dict[str, Any]]]:
    """Find a case by reference and return the case, its index, and all cases."""
    cases = load_mock_data()

    for idx, case in enumerate(cases):
        if case.get("caseReference") == case_reference:
            return case, idx, cases

    raise HTTPException(
        status_code=404, detail=f"Case with reference '{case_reference}' not found"
    )


def save_cases_to_file(cases: List[Dict[str, Any]]) -> None:
    """Save cases data back to the JSON file."""
    try:
        with open(MOCK_DATA_PATH, "w", encoding="utf-8") as file:
            json.dump(cases, file, indent=2, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving data: {str(e)}")


def filter_cases_by_status(
    cases: List[Dict[str, Any]], status: str
) -> List[Dict[str, Any]]:
    """Filter cases by status. Returns all cases when status is 'all'."""
    # If status is "all", return all cases without filtering
    if status.lower() == "all":
        return cases

    # Otherwise filter by the specified status
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


def search_cases(
    cases: List[Dict[str, Any]],
    keyword: str,
) -> List[Dict[str, Any]]:
    """Search cases by keyword across multiple fields with specific matching rules."""
    # Return empty list if keyword is empty or just whitespace
    if not keyword or not keyword.strip():
        return []

    keyword_lower = keyword.lower()
    keyword_no_spaces = keyword.replace(" ", "").lower()

    def matches_case(case: Dict[str, Any]) -> bool:
        """Check if a case matches the search keyword."""
        if not case or not isinstance(case, dict) or not case.get("caseReference"):
            return False

        # Define search criteria as a list of (field_value, match_type) tuples
        search_criteria = [
            # Case reference (exact match, case-insensitive)
            (str(case.get("caseReference", "")).lower(), "exact", keyword_lower),
            # Phone number (exact match, ignore whitespace)
            (
                str(case.get("phoneNumber", "")).replace(" ", "").lower(),
                "exact",
                keyword_no_spaces,
            ),
            # Full name (partial match, case-insensitive)
            (str(case.get("fullName", "")).lower(), "partial", keyword_lower),
            # Postcode (exact match, case-insensitive, ignore whitespace)
            (
                str(case.get("postcode", "")).replace(" ", "").lower(),
                "exact",
                keyword_no_spaces,
            ),
            # Address (partial match, case-insensitive)
            (str(case.get("address", "")).lower(), "partial", keyword_lower),
        ]

        # Check if any criteria matches
        return any(
            (match_type == "exact" and field_value == search_value)
            or (match_type == "partial" and search_value in field_value)
            for field_value, match_type, search_value in search_criteria
        )

    return [case for case in cases if matches_case(case)]


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
    target_case, _, _ = find_case_by_reference(case_reference)
    return MockCase(**target_case)


@router.put(
    "/cases/{case_reference}",
    tags=["mock"],
    response_model=MockCase,
    summary="Update mock case by reference (partial update)",
    description="Updates fields of a specific mock case by case reference. Only provided fields will be changed.",
)
async def put_case_by_reference(
    case_reference: str,
    update_data: dict = Body(..., example={"fullName": "New Name"}),
) -> MockCase:
    """Update fields of a specific mock case by case reference."""
    updated_case = update_case_by_reference(case_reference, update_data)
    return MockCase(**updated_case)


@router.get(
    "/cases/search",
    tags=["mock"],
    response_model=List[MockCase],
    summary="Search mock cases",
    description="Search cases by keyword across case reference, phone number (ignores spaces), full name, postcode (ignores spaces), and address with optional status filter. Results are sorted by lastModified date.",
)
async def search_mock_cases(
    response: Response,
    keyword: str = Query(..., description="Keyword to search across multiple fields"),
    status: Optional[str] = Query(
        None,
        description="Filter by case status: new, opened, closed, accepted, all (returns all statuses)",
    ),
    sortOrder: Optional[str] = Query(
        "desc", description="Sort order 'asc' or 'desc' by lastModified date"
    ),
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    limit: int = Query(20, ge=1, le=100, description="Number of records per page"),
) -> List[MockCase]:
    """Search cases by keyword across multiple fields with pagination, optional status filter, and sorting by lastModified date."""
    all_cases = load_mock_data()

    # Apply search filter
    filtered_cases = search_cases(all_cases, keyword)

    # Apply status filter if provided
    if status:
        filtered_cases = filter_cases_by_status(filtered_cases, status)

    # Add console log here to see total results after search and filtering
    print(
        f"Search for '{keyword}'{f' with status filter {status}' if status else ''} found {len(filtered_cases)} results"
    )

    # Sort by lastModified date
    reverse = sortOrder.lower() == "desc"
    sorted_cases = sorted(
        filtered_cases, key=lambda case: case.get("lastModified", ""), reverse=reverse
    )

    # Apply pagination
    paginated_cases, total_count = paginate_cases(sorted_cases, page, limit)

    set_pagination_headers(response, total_count, page, limit)
    return [MockCase(**case) for case in paginated_cases]


@router.post(
    "/cases/{case_reference}/third-party",
    tags=["mock"],
    response_model=MockCase,
    summary="Add third party to a case",
    description="Adds third party information to a specific case by case reference. Only fullName is mandatory.",
)
async def add_third_party_to_case(
    case_reference: str,
    third_party_data: ThirdPartyCreate = Body(
        ...,
        example={
            "fullName": "John Smith",
            "emailAddress": "john.smith@email.com",
            "contactNumber": "0123456789",
            "safeToCall": True,
            "address": "123 Main Street, London",
            "postcode": "SW1A 1AA",
        },
    ),
) -> MockCase:
    """Add third party information to a specific case by case reference."""
    target_case, case_index, cases = find_case_by_reference(case_reference)

    # Convert ThirdPartyCreate to dict and add to case
    third_party_dict = third_party_data.model_dump(exclude_unset=True)
    target_case["thirdParty"] = third_party_dict

    # Update the case in the list and save
    cases[case_index] = target_case
    save_cases_to_file(cases)

    return MockCase(**target_case)


@router.put(
    "/cases/{case_reference}/third-party",
    tags=["mock"],
    response_model=MockCase,
    summary="Update third party information for a case",
    description="Updates third party information for a specific case by case reference. Only fullName is mandatory, other fields are optional.",
)
async def update_third_party_for_case(
    case_reference: str,
    third_party_data: ThirdPartyUpdate = Body(
        ...,
        example={
            "fullName": "John Smith Updated",
            "emailAddress": "john.updated@email.com",
            "safeToCall": False,
        },
    ),
) -> MockCase:
    """Update third party information for a specific case by case reference."""
    target_case, case_index, cases = find_case_by_reference(case_reference)

    # Check if case has existing third party information
    if "thirdParty" not in target_case or target_case["thirdParty"] is None:
        raise HTTPException(
            status_code=404,
            detail=f"No third party information found for case '{case_reference}'",
        )

    # Get existing third party data
    existing_third_party = target_case["thirdParty"]

    # Update only provided fields (exclude_unset=True means only fields that were explicitly set)
    update_data = third_party_data.model_dump(exclude_unset=True)

    # Merge with existing data
    for key, value in update_data.items():
        existing_third_party[key] = value

    # Update the case in the list and save
    target_case["thirdParty"] = existing_third_party
    cases[case_index] = target_case
    save_cases_to_file(cases)

    return MockCase(**target_case)
