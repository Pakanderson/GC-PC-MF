from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class MemberRegistrationSchema(BaseModel):
    """
    Pydantic Schema for validating payload received from the frontend form.
    Matches all Page 1 and Page 2 fields.
    """

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

    # Page 1: Professional Background
    job_title: Optional[str] = None
    industry_sector: Optional[str] = None
    years_experience: Optional[str] = None
    qualification_field: Optional[str] = None
    key_skills: Optional[List[str]] = Field(default_factory=list)
    linkedin_profile: Optional[str] = None
    membership_category: str = Field(..., pattern=r"^(Mentor|Mentee|Member)$")

    # Page 2: Mentor Block
    mentor_areas: Optional[List[str]] = Field(default_factory=list)
    mentoring_format: Optional[str] = None
    max_mentees: Optional[str] = None
    mentor_availability: Optional[List[str]] = Field(default_factory=list)
    workshop_speaker: Optional[str] = None

    # Page 2: Mentee Block
    mentee_seeking: Optional[List[str]] = Field(default_factory=list)
    mentee_goals: Optional[str] = None
    mentor_preferred_background: Optional[str] = None

    # Page 2: Member Block
    workshop_topics: Optional[List[str]] = Field(default_factory=list)
    help_organize_events: Optional[str] = None

    # Engagement, Consent & General Comments
    event_availability: Optional[List[str]] = Field(default_factory=list)
    hear_about_club: Optional[str] = None
    gdpr_consent: bool = Field(..., equals=True)
    terms_consent: bool = Field(..., equals=True)
    profession: Optional[str] = None
    comments: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Kwame Mensah",
                "email": "kwame.mensah@example.com",
                "dob_month_year": "1992-05",
                "gender": "Male",
                "nationality": "Ghanaian",
                "hometown_ghana": "Kumasi",
                "residence_germany": "Düsseldorf",
                "phone": "+49 176 12345678",
                "preferred_contact_method": "WhatsApp",
                "city_region_germany": "Düsseldorf, NRW",
                "languages_spoken": ["English", "German", "Twi"],
                "job_title": "Software Engineer",
                "industry_sector": "IT",
                "years_experience": "5–10",
                "qualification_field": "M.Sc. Computer Science",
                "key_skills": ["Software Engineering", "IT"],
                "linkedin_profile": "https://linkedin.com/in/kwamemensah",
                "membership_category": "Mentor",
                "mentor_areas": ["Career guidance", "Technical mentoring"],
                "mentoring_format": "1-on-1",
                "max_mentees": "2–3",
                "mentor_availability": ["Weekday evenings", "Weekends"],
                "workshop_speaker": "Yes",
                "event_availability": ["Weekends"],
                "hear_about_club": "Social Media",
                "gdpr_consent": True,
                "terms_consent": True,
                "profession": "IT Professional",
                "comments": "Excited to join!",
            }
        }
