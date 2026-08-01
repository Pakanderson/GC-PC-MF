from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class CouncilMember(db.Model):
    """
    SQLAlchemy Model for the Ghana Council NRW Professionals Club Members.
    Stores Page 1 (Personal & Contact Info, Professional Background)
    and Page 2 (Category-Specifics & Consent details).
    """

    __tablename__ = "club_members"

    # Primary Keys & Identifiers
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_id = db.Column(db.String(50), unique=True, nullable=True)  # e.g., GC-PC-001

    # Page 1: Personal & Contact Info
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)
    date_of_birth = db.Column(db.Date, nullable=True)  # Stored as YYYY-MM-01
    gender = db.Column(db.String(50), nullable=True)
    nationality = db.Column(db.String(100), nullable=True)
    hometown_ghana = db.Column(db.String(150), nullable=True)
    residence_germany = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(50), nullable=False)
    preferred_contact_method = db.Column(db.String(50), nullable=True)
    city_region_germany = db.Column(db.String(150), nullable=True)
    languages_spoken = db.Column(
        db.JSON, nullable=True
    )  # Stores list e.g. ["English", "German"]

    # Page 1: Professional Background
    job_title = db.Column(db.String(255), nullable=True)
    industry_sector = db.Column(db.String(150), nullable=True)
    years_experience = db.Column(db.String(50), nullable=True)
    qualification_field = db.Column(db.String(255), nullable=True)
    key_skills = db.Column(db.JSON, nullable=True)
    linkedin_profile = db.Column(db.String(255), nullable=True)
    membership_category = db.Column(
        db.String(50), nullable=False
    )  # Mentor / Mentee / Member

    # Page 2: Mentor Specifics
    mentor_areas = db.Column(db.JSON, nullable=True)
    mentoring_format = db.Column(db.String(50), nullable=True)
    max_mentees = db.Column(db.String(20), nullable=True)
    mentor_availability = db.Column(db.JSON, nullable=True)
    workshop_speaker = db.Column(db.String(20), nullable=True)  # Yes / No / Maybe

    # Page 2: Mentee Specifics
    mentee_seeking = db.Column(db.JSON, nullable=True)
    mentee_goals = db.Column(db.Text, nullable=True)
    mentor_preferred_background = db.Column(db.String(255), nullable=True)

    # Page 2: Member Specifics
    workshop_topics = db.Column(db.JSON, nullable=True)
    help_organize_events = db.Column(db.String(20), nullable=True)  # Yes / No / Maybe

    # Engagement, Consent & General Comments
    event_availability = db.Column(db.JSON, nullable=True)
    hear_about_club = db.Column(db.String(150), nullable=True)
    gdpr_consent = db.Column(db.Boolean, nullable=False, default=False)
    terms_consent = db.Column(db.Boolean, nullable=False, default=False)
    profession = db.Column(db.String(255), nullable=True)
    comments = db.Column(db.Text, nullable=True)

    # System Timestamps
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def generate_formatted_id(self):
        """Generates readable membership ID e.g., GC-PC-001 based on internal numeric ID."""
        if self.id:
            self.member_id = f"GC-PC-{self.id:03d}"

    def to_dict(self):
        """Converts model attributes to a JSON-serializable dictionary."""
        return {
            "id": self.id,
            "member_id": self.member_id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "membership_category": self.membership_category,
            "job_title": self.job_title,
            "industry_sector": self.industry_sector,
            "city_region_germany": self.city_region_germany,
            "submitted_at": (
                self.submitted_at.isoformat() if self.submitted_at else None
            ),
        }
