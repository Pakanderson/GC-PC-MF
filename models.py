from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ==========================================
# 1. Club Members Table
# ==========================================
class CouncilMember(db.Model):
    __tablename__ = "club_members"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_id = db.Column(
        db.String(20), unique=True, nullable=True
    )  # Populated as GC-PC-001
    full_name = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    nationality = db.Column(db.String(100), nullable=False, default="Ghanaian")
    hometown_ghana = db.Column(db.String(150), nullable=False)
    city_germany = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)
    membership_category = db.Column(db.String(100), nullable=False)

    # Professional & Skill Details
    occupation = db.Column(db.String(150), nullable=True)
    skills = db.Column(db.JSON, nullable=True)
    referral_source = db.Column(db.String(100), nullable=True)
    volunteer_commitment = db.Column(db.String(50), nullable=False)
    comments = db.Column(db.Text, nullable=True)

    # Metadata & GDPR
    gdpr_consent_given = db.Column(db.Boolean, nullable=False, default=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    leadership_profile = db.relationship(
        "Leader", backref="member", uselist=False, cascade="all, delete-orphan"
    )
    mentorship_as_student = db.relationship(
        "MentorshipAssignment",
        foreign_keys="MentorshipAssignment.student_member_id",
        backref="student",
        cascade="all, delete-orphan",
    )

    def generate_formatted_id(self):
        """Sets member_id as GC-PC-001 based on auto-increment id."""
        if self.id and not self.member_id:
            self.member_id = f"GC-PC-{self.id:03d}"

    def to_dict(self):
        return {
            "id": self.id,
            "member_id": self.member_id,
            "full_name": self.full_name,
            "membership_category": self.membership_category,
            "city_germany": self.city_germany,
            "phone_number": self.phone_number,
            "submitted_at": (
                self.submitted_at.isoformat() if self.submitted_at else None
            ),
        }


# ==========================================
# 2. Leaders / Mentors Table
# ==========================================
class Leader(db.Model):
    __tablename__ = "leaders"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    leader_id = db.Column(
        db.String(20), unique=True, nullable=True
    )  # Populated as GC-L-001
    member_id = db.Column(
        db.String(20),
        db.ForeignKey("club_members.member_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    leadership_role = db.Column(db.String(100), nullable=False)
    expertise_areas = db.Column(db.JSON, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    max_mentees = db.Column(db.Integer, default=3)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    mentorships = db.relationship(
        "MentorshipAssignment",
        foreign_keys="MentorshipAssignment.leader_id",
        backref="mentor",
        cascade="all, delete-orphan",
    )
    workshops = db.relationship(
        "WorkshopWebinar", backref="host_leader", cascade="all, delete-orphan"
    )

    def generate_formatted_id(self):
        """Sets leader_id as GC-L-001 based on auto-increment id."""
        if self.id and not self.leader_id:
            self.leader_id = f"GC-L-{self.id:03d}"


# ==========================================
# 3. Mentorship Assignments Table
# ==========================================
class MentorshipAssignment(db.Model):
    __tablename__ = "mentorship_assignments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assignment_id = db.Column(
        db.String(20), unique=True, nullable=True
    )  # Populated as GC-MA-001
    leader_id = db.Column(
        db.String(20),
        db.ForeignKey("leaders.leader_id", ondelete="CASCADE"),
        nullable=False,
    )
    student_member_id = db.Column(
        db.String(20),
        db.ForeignKey("club_members.member_id", ondelete="CASCADE"),
        nullable=False,
    )
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default="ACTIVE")
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def generate_formatted_id(self):
        """Sets assignment_id as GC-MA-001 based on auto-increment id."""
        if self.id and not self.assignment_id:
            self.assignment_id = f"GC-MA-{self.id:03d}"


# ==========================================
# 4. Workshops & Webinars Table
# ==========================================
class WorkshopWebinar(db.Model):
    __tablename__ = "workshops_webinars"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(
        db.String(20), unique=True, nullable=True
    )  # Populated as GC-WW-001
    leader_id = db.Column(
        db.String(20),
        db.ForeignKey("leaders.leader_id", ondelete="CASCADE"),
        nullable=False,
    )
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_type = db.Column(db.String(50), nullable=False)  # 'WORKSHOP' or 'WEBINAR'
    event_date = db.Column(db.DateTime, nullable=False)
    meeting_link = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def generate_formatted_id(self):
        """Sets event_id as GC-WW-001 based on auto-increment id."""
        if self.id and not self.event_id:
            self.event_id = f"GC-WW-{self.id:03d}"
