from pydantic import BaseModel, field_validator, Field
from typing import Optional, List, Dict


class ReasonableAdjustments(BaseModel):
    """Reasonable adjustments structure."""

    selected: Optional[List[str]] = []
    available: Optional[List[str]] = []
    additionalInfo: Optional[str] = ""


class PassphraseSetup(BaseModel):
    """Passphrase setup structure."""

    selected: List[str] = Field(
        default_factory=list, description="Selected passphrase setup options"
    )
    available: List[str] = Field(
        default_factory=lambda: [
            "Yes",
            "No, client is a child or patient",
            "No, client is subject to power of attorney",
            "No, client cannot communicate on the phone due to disability",
            "No, client cannot communicate on the phone due to a language requirement",
            "Other",
        ],
        description="Available passphrase setup options",
    )
    passphrase: Optional[str] = Field(
        None, description="The actual passphrase if set up"
    )


class ThirdParty(BaseModel):
    """Third party contact information structure."""

    fullName: str
    emailAddress: Optional[str] = None
    contactNumber: Optional[str] = None
    safeToCall: bool = False
    address: Optional[str] = None
    postcode: Optional[str] = None
    relationshipToClient: Optional[Dict[str, List[str]]] = None
    passphraseSetUp: Optional[PassphraseSetup] = None


class ThirdPartyCreate(BaseModel):
    """Request model for creating third party information."""

    fullName: str
    emailAddress: Optional[str] = None
    contactNumber: Optional[str] = None
    safeToCall: Optional[bool] = False
    address: Optional[str] = None
    postcode: Optional[str] = None
    relationshipToClient: Optional[Dict[str, List[str]]] = None
    passphraseSetUp: Optional[PassphraseSetup] = None

    @field_validator("fullName")
    @classmethod
    def validate_full_name(cls, v):
        if not v or not v.strip():
            raise ValueError("fullName is required and cannot be empty")
        return v.strip()


class ThirdPartyUpdate(BaseModel):
    """Request model for updating third party information."""

    fullName: str
    emailAddress: Optional[str] = None
    contactNumber: Optional[str] = None
    safeToCall: Optional[bool] = None
    address: Optional[str] = None
    postcode: Optional[str] = None
    relationshipToClient: Optional[Dict[str, List[str]]] = None
    passphraseSetUp: Optional[PassphraseSetup] = None

    @field_validator("fullName")
    @classmethod
    def validate_full_name(cls, v):
        if not v or not v.strip():
            raise ValueError("fullName is required and cannot be empty")
        return v.strip()


class MockCase(BaseModel):
    """Mock case data structure."""

    fullName: str
    caseReference: str
    refCode: Optional[str] = ""
    dateReceived: str
    lastModified: Optional[str] = None
    dateClosed: Optional[str] = None
    caseStatus: str
    dateOfBirth: str  # Changed from DateOfBirth object to string
    clientIsVulnerable: Optional[bool] = False
    reasonableAdjustments: Optional[ReasonableAdjustments] = None
    language: Optional[str] = "English"
    phoneNumber: Optional[str] = ""
    safeToCall: Optional[bool] = False
    announceCall: Optional[bool] = False
    emailAddress: Optional[str] = ""
    address: Optional[str] = ""
    postcode: Optional[str] = ""
    laaReference: Optional[str] = ""
    thirdParty: Optional[ThirdParty] = None
