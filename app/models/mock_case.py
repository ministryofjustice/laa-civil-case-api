from pydantic import BaseModel, field_validator, Field
from typing import Optional, List, Dict


class PassphraseSetup(BaseModel):
    """Passphrase setup structure."""

    selected: List[str] = Field(
        default_factory=list, description="Selected passphrase setup options"
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

    @field_validator("safeToCall", mode="before")
    @classmethod
    def validate_safe_to_call(cls, v):
        if v == "" or v is None:
            return True
        if isinstance(v, str):
            if v.lower() in ("true", "1", "yes"):
                return True
            elif v.lower() in ("false", "0", "no"):
                return False
            else:
                return True
        return bool(v)


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

    @field_validator("safeToCall", mode="before")
    @classmethod
    def validate_safe_to_call(cls, v):
        if v == "" or v is None:
            return None  # Keep as None for updates to indicate no change
        if isinstance(v, str):
            if v.lower() in ("true", "1", "yes"):
                return True
            elif v.lower() in ("false", "0", "no"):
                return False
            else:
                return True  # Default to True for invalid string values
        return bool(v)


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
    language: Optional[str] = "English"
    phoneNumber: Optional[str] = ""
    safeToCall: Optional[bool] = False
    announceCall: Optional[bool] = False
    emailAddress: Optional[str] = ""
    address: Optional[str] = ""
    postcode: Optional[str] = ""
    laaReference: Optional[str] = ""
    thirdParty: Optional[ThirdParty] = None
