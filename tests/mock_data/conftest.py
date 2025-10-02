"""
Shared fixtures for mock_data tests.
"""

import pytest


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
            "language": "English",
            "phoneNumber": "0776744581",
            "safeToCall": False,
            "announceCall": True,
            "emailAddress": "ehamilton@yahoo.com",
            "address": "25 Victoria Road, Edinburgh",
            "postcode": "G1 8LB",
            "laaReference": "4235871",
            "thirdParty": {
                "fullName": "Alex Rivers",
                "emailAddress": "alex@rivers.com",
                "contactNumber": "",
                "safeToCall": False,
                "address": "22 Baker Street, London",
                "postcode": "NW1 6XE",
                "relationshipToClient": {
                    "selected": ["Other"],
                },
                "passphraseSetUp": {
                    "selected": ["Yes"],
                    "passphrase": "Secret123",
                },
            },
        },
        {
            "fullName": "Hazel Walker",
            "caseReference": "PC-8372-6419",
            "refCode": "",
            "dateReceived": "2025-05-19T19:00:00-05:00",
            "lastModified": "2025-05-20T10:15:00-05:00",
            "caseStatus": "New",
            "dateOfBirth": "1986-01-08T00:00:00-05:00",
            "clientIsVulnerable": True,
            "language": "French",
            "phoneNumber": "0783017079",
            "safeToCall": False,
            "announceCall": True,
            "emailAddress": "hwalker@yahoo.com",
            "address": "798 Mill Lane, Bradford",
            "postcode": "HU1 7TT",
            "laaReference": "7310481",
            "thirdParty": {
                "fullName": "Pamela Teahouse",
                "emailAddress": "pamela@teahouse.com",
                "contactNumber": "",
                "safeToCall": True,
                "address": "5 Maple Avenue, Manchester",
                "postcode": "M1 2AB",
                "relationshipToClient": {
                    "selected": ["Family member of friend"],
                },
                "passphraseSetUp": {
                    "selected": ["Yes"],
                    "passphrase": "Would you like some tea?",
                },
            },
        },
        {
            "fullName": "Maya Patel",
            "caseReference": "PC-8765-4321",
            "refCode": "",
            "dateReceived": "2025-03-14T19:00:00-05:00",
            "lastModified": "2025-03-15T16:45:00-05:00",
            "caseStatus": "Opened",
            "dateOfBirth": "1986-06-09T00:00:00-05:00",
            "clientIsVulnerable": False,
            "language": "English",
            "phoneNumber": "0777842384",
            "safeToCall": False,
            "announceCall": False,
            "emailAddress": "maya@patel.com",
            "address": "320 Victoria Road, Leeds",
            "postcode": "LE1 7GQ",
            "laaReference": "5173578",
            "thirdParty": None,
        },
        {
            "fullName": "Jack Young",
            "caseReference": "PC-1922-1879",
            "refCode": "",
            "dateReceived": "2025-07-06T19:00:00-05:00",
            "lastModified": "2025-07-07T11:30:00-05:00",
            "dateClosed": "2025-07-07T17:00:00-05:00",
            "caseStatus": "Closed",
            "dateOfBirth": "1981-08-18T00:00:00-05:00",
            "clientIsVulnerable": True,
            "language": "German",
            "phoneNumber": "0786442261",
            "safeToCall": False,
            "announceCall": False,
            "emailAddress": "jack@young.com",
            "address": "870 King Street, Sheffield",
            "postcode": "G1 2LQ",
            "laaReference": "8196672",
            "thirdParty": None,
        },
    ]


@pytest.fixture
def mock_search_data():
    """Mock data specifically for search testing."""
    return [
        {
            "fullName": "John Smith",
            "caseReference": "PC-1234-5678",
            "phoneNumber": "0777 123 456",
            "address": "123 Main Street, London",
            "postcode": "SW1A 1AA",
            "caseStatus": "New",
            "dateOfBirth": "1985-06-15",
            "dateReceived": "2025-01-01T10:00:00-05:00",
            "lastModified": "2025-01-01T10:00:00-05:00",
        },
        {
            "fullName": "Jane Doe",
            "caseReference": "PC-9876-5432",
            "phoneNumber": "07767 44581",
            "address": "456 Oak Avenue, Manchester",
            "postcode": "M1 1AA",
            "caseStatus": "Opened",
            "dateOfBirth": "1990-03-22",
            "dateReceived": "2025-01-02T11:00:00-05:00",
            "lastModified": "2025-01-02T11:00:00-05:00",
        },
        {
            "fullName": "Bob Wilson",
            "caseReference": "PC-1111-2222",
            "phoneNumber": "07776442261",
            "address": "789 Church Road, Birmingham",
            "postcode": "B1 1AA",
            "caseStatus": "Closed",
            "dateOfBirth": "1978-12-10",
            "dateReceived": "2025-01-03T12:00:00-05:00",
            "lastModified": "2025-01-03T12:00:00-05:00",
            "dateClosed": "2025-01-04T15:00:00-05:00",
        },
    ]
