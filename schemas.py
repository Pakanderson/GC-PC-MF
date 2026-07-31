from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


# --- Dropdown Choice Definitions ---
class MembershipCategoryEnum(str, Enum):
    CLUB_MEMBER = "Club Member"
    CLUB_MENTOR = "Club Mentor"
    CLUB_MENTEE = "Club Mentee"


class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    PREFER_NOT_TO_SAY = "Prefer not to say"


class VolunteerCommitmentEnum(str, Enum):
    YES = "Yes"
    NO = "No"
    MAYBE = "Maybe"


# --- Validation Schema ---
class MemberRegistrationSchema(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    dob_month_year: str = Field(
        ...,
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
        description="Month and Year in YYYY-MM format",
    )
    gender: GenderEnum
    nationality: str = Field(default="Ghanaian", max_length=100)
    hometown_ghana: str = Field(..., max_length=150)
    city_germany: str = Field(..., max_length=150)
    phone_number: str = Field(..., max_length=50)
    membership_category: MembershipCategoryEnum

    occupation: Optional[str] = None
    skills: Optional[List[str]] = None
    referral_source: Optional[str] = None
    volunteer_commitment: VolunteerCommitmentEnum
    comments: Optional[str] = None
    gdpr_consent_given: bool = True
