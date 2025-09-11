# Mock Data Tests

This directory contains tests for the mock data functionality, organized by functionality area.

## Test Files Structure

### `conftest.py`
Contains shared fixtures used across all test files:
- `mock_data()` - Sample mock case data for testing
- `mock_search_data()` - Specialized data for search functionality tests

### `test_helper_functions.py`
Tests for utility/helper functions:
- `load_mock_data()` - Loading data from JSON file
- `filter_cases_by_status()` - Status filtering functionality
- `sort_cases()` - Case sorting by different date fields
- `paginate_cases()` - Pagination functionality
- `search_cases()` - Search functionality across multiple fields
- `find_case_by_reference()` - Finding cases by reference
- `save_cases_to_file()` - Saving data back to JSON file
- `update_case_by_reference()` - Updating case data

### `test_case_endpoints.py`
Tests for case-related API endpoints:
- GET `/mock/cases/new` - Get new cases
- GET `/mock/cases/opened` - Get opened cases
- GET `/mock/cases/accepted` - Get accepted cases
- GET `/mock/cases/closed` - Get closed cases
- GET `/mock/cases/{case_reference}` - Get specific case
- PUT `/mock/cases/{case_reference}` - Update case
- GET `/mock/cases/search` - Search cases
- Status filtering functionality
- Pagination and sorting parameters

### `test_third_party_endpoints.py`
Tests for third-party related API endpoints:
- POST `/mock/cases/{case_reference}/third-party` - Add third party
- PUT `/mock/cases/{case_reference}/third-party` - Update third party
- DELETE `/mock/cases/{case_reference}/third-party` - Delete third party
- Validation of mandatory `fullName` field
- Error handling for missing cases/third parties
- Model validation tests for `ThirdPartyCreate` and `ThirdPartyUpdate`

### `test_models.py`
Tests for Pydantic models:
- `MockCase` - Main case model validation
- `ThirdParty` - Third party information model
- `ThirdPartyCreate` - Request model for creating third parties
- `ThirdPartyUpdate` - Request model for updating third parties
- Field validation, default values, and model interactions

## Running Tests

### Run all mock data tests:
```bash
pytest tests/mock_data/
```

### Run specific test files:
```bash
# Helper functions only
pytest tests/mock_data/test_helper_functions.py

# Case endpoints only
pytest tests/mock_data/test_case_endpoints.py

# Third party endpoints only
pytest tests/mock_data/test_third_party_endpoints.py

# Models only
pytest tests/mock_data/test_models.py
```

### Run specific test classes:
```bash
# Search functionality tests
pytest tests/mock_data/test_helper_functions.py::TestSearchCases

# Third party validation tests
pytest tests/mock_data/test_third_party_endpoints.py::TestThirdPartyModels
```

## Test Coverage

The tests cover:
- ✅ All helper functions with success and error cases
- ✅ All API endpoints with various parameter combinations
- ✅ Model validation including edge cases
- ✅ Error handling and HTTP status codes
- ✅ Data persistence (saving/loading from file)
- ✅ Search functionality across multiple fields
- ✅ Pagination and sorting
- ✅ Third party CRUD operations
- ✅ Mandatory field validation (`fullName`)
- ✅ Field trimming and data sanitization

## Key Testing Patterns

1. **Mocking**: External dependencies (file operations, data loading) are mocked
2. **Fixtures**: Shared test data is provided via `conftest.py`
3. **Error Testing**: Both success and failure scenarios are tested
4. **Validation Testing**: Pydantic model validation is thoroughly tested
5. **Integration Testing**: API endpoints are tested with TestClient
6. **Edge Cases**: Empty data, invalid inputs, and boundary conditions are tested

## Migration from Original File

The original `test_mock_data.py` has been split into focused test files:
- Reduced file size from 1500+ lines to manageable chunks
- Improved test organization and discoverability
- Easier maintenance and parallel development
- Better test isolation and focused testing
- Clearer separation of concerns
