from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class MemberRegistrationSchema(BaseModel):
    """
    Pydantic Schema for validating registration requests.
    Supports Base64 profile photo, Page 1 submission (Member/Mentee),
    and Page 2 submission (Mentor).
    """

    # Profile Photo
    profile_photo: Optional[str] = None

    # Page 1: Personal & Contact Info
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    dob_month_year: Optional[str] = Field(
        None, pattern=r"^\d{4}-\d{2}$"
    )  # e.g., "1995-08"
    gender: Optional[str] = None
    nationality: Optional[str] = None
    hometown_ghana: Optional[str] = None
    residence_germany: Optional[str] = None
    phone: str = Field(..., min_length=5, max_length=50)
    preferred_contact_method: Optional[str] = None
    city_region_germany: Optional[str] = None
    languages_spoken: Optional[List[str]] = Field(default_factory=list)

    # Page 1: General Questions for Everyone
    hear_about_club: Optional[str] = None
    profession: Optional[str] = None
    comments: Optional[str] = None
    membership_category: str = Field(..., pattern=r"^(Member|Mentee|Mentor)$")

    # Mentee Block (Page 1)
    mentee_seeking: Optional[List[str]] = Field(default_factory=list)
    mentee_goals: Optional[str] = None
    mentor_preferred_background: Optional[str] = None

    # Member Block (Page 1)
    workshop_topics: Optional[List[str]] = Field(default_factory=list)
    help_organize_events: Optional[str] = None

    # Mentor Professional & Matching Block (Page 2 - Mentors Only)
    job_title: Optional[str] = None
    industry_sector: Optional[str] = None
    years_experience: Optional[str] = None
    qualification_field: Optional[str] = None
    key_skills: Optional[List[str]] = Field(default_factory=list)
    linkedin_profile: Optional[str] = None
    mentor_areas: Optional[List[str]] = Field(default_factory=list)
    mentoring_format: Optional[str] = None
    max_mentees: Optional[str] = None
    mentor_availability: Optional[List[str]] = Field(default_factory=list)
    workshop_speaker: Optional[str] = None

    # Engagement & Consent
    event_availability: Optional[List[str]] = Field(default_factory=list)
    gdpr_consent: bool = Field(..., equals=True)
    terms_consent: bool = Field(..., equals=True)

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Kwame Mensah",
                "email": "kwame.mensah@example.com",
                "phone": "+49 176 12345678",
                "membership_category": "Mentee",
                "gdpr_consent": True,
                "terms_consent": True,
            }
        }
