import csv
from datetime import datetime, date
from functools import wraps
import io
import os

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, make_response, render_template, request
from flask_cors import CORS
from flask_mail import Mail, Message
from pydantic import ValidationError

from models import CouncilMember, Leader, MentorshipAssignment, db
from schemas import MemberRegistrationSchema

# Load Environment Variables from .env
load_dotenv()

# Initialize App & Setup Extensions
app = Flask(__name__)
CORS(app)

# ==========================================
# 1. Database Configuration MYSQL
# ==========================================
# DB_USER = os.getenv("DB_USER", "root")
# DB_PASS = os.getenv("DB_PASS", "your_mysql_password")
# DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
# DB_PORT = os.getenv("DB_PORT", "3306")
# DB_NAME = os.getenv("DB_NAME", "gc_professionals_club_db")

# app.config["SQLALCHEMY_DATABASE_URI"] = (
#     f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# )
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# ==========================================
# 1. Database Configuration Switch to SQLite
# ==========================================
# If running locally with MySQL credentials in .env, it uses MySQL.
# Otherwise, it defaults to a local SQLite database file ('site.db').
# ==========================================
# 1. Database Configuration
# ==========================================
db_url = os.getenv("DATABASE_URL")
db_pass = os.getenv("DB_PASS")

if db_url:
    # --- Priority 1: Render / Cloud PostgreSQL ---
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url

elif db_pass:
    # --- Priority 2: Local MySQL ---
    db_user = os.getenv("DB_USER", "root")
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "gc_professionals_club_db")
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    )

else:
    # --- Priority 3: Local SQLite Fallback ---
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/club.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# ==========================================
# 2. Mail Configuration
# ==========================================
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "your-email@gmail.com")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "your-app-password")
app.config["MAIL_DEFAULT_SENDER"] = (
    "Ghana Council NRW - Professionals Club",
    os.getenv("MAIL_USERNAME", "your-email@gmail.com"),
)

# Initialize Extensions
db.init_app(app)
mail = Mail(app)

with app.app_context():
    db.create_all()


# ==========================================
# 3. BASIC AUTH HELPER FUNCTIONS (PASTE HERE!)
# ==========================================
def check_auth(username, password):
    """Reads credentials from .env and verifies login."""
    admin_username = os.getenv("ADMIN_USER", "admin")
    admin_password = os.getenv("ADMIN_PASS", "GhanaCouncil2026!")
    return username == admin_username and password == admin_password


def requires_auth(f):
    """Decorator to trigger browser login prompt."""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return Response(
                "Access Denied: Invalid Admin Credentials.",
                401,
                {"WWW-Authenticate": 'Basic realm="Admin Access Required"'},
            )
        return f(*args, **kwargs)

    return decorated


# ==========================================
# 4. Email Dispatch Helper
# ==========================================
def send_confirmation_email(recipient_email, full_name, category):
    try:
        msg = Message(
            subject="Welcome to the Ghana Council NRW — Professionals Club",
            recipients=[recipient_email],
        )

        msg.body = f"""Dear {full_name},

Thank you for registering with Ghana Council NRW — Professionals Club!

We have successfully received your registration under the category: {category}.
Our administrative team will review your details shortly.

Kind regards,
Ghana Council NRW Team
Düsseldorf, Germany
"""

        mail.send(msg)
        return True
    except Exception as e:
        print(f"[Email Error] Failed to send email to {recipient_email}: {str(e)}")
        return False


# ==========================================
# 5. Public Routes (No Auth Needed)
# ==========================================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/register", methods=["POST"])
def register_member():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No JSON payload provided"}), 400

    try:
        validated_data = MemberRegistrationSchema(**data)
    except ValidationError as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Validation failed",
                    "errors": e.errors(),
                }
            ),
            422,
        )

    try:
        parsed_dob = datetime.strptime(
            f"{validated_data.dob_month_year}-01", "%Y-%m-%d"
        ).date()
    except ValueError:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Invalid date format for birth month/year.",
                }
            ),
            400,
        )

    new_member = CouncilMember(
        full_name=validated_data.full_name,
        date_of_birth=parsed_dob,
        gender=validated_data.gender,
        nationality=validated_data.nationality,
        hometown_ghana=validated_data.hometown_ghana,
        city_germany=validated_data.city_germany,
        phone_number=validated_data.phone_number,
        membership_category=validated_data.membership_category,
        occupation=validated_data.occupation,
        skills=validated_data.skills,
        referral_source=validated_data.referral_source,
        volunteer_commitment=validated_data.volunteer_commitment,
        comments=validated_data.comments,
        gdpr_consent_given=validated_data.gdpr_consent_given,
    )

    try:
        db.session.add(new_member)
        db.session.flush()  # Generates auto-increment numeric id
        new_member.generate_formatted_id()  # Sets member_id = GC-PC-001
        db.session.commit()

        recipient_email = data.get("email")
        email_sent = False
        if recipient_email:
            email_sent = send_confirmation_email(
                recipient_email=recipient_email,
                full_name=new_member.full_name,
                category=new_member.membership_category,
            )

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Registration completed successfully!",
                    "member_id": new_member.member_id,
                    "email_sent": email_sent,
                }
            ),
            201,
        )

    except Exception as err:
        db.session.rollback()
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Database transaction failed",
                    "details": str(err),
                }
            ),
            500,
        )


# ==========================================
# 6. PROTECTED ADMIN ROUTES (Uses @requires_auth)
# ==========================================
@app.route("/admin/members")
@requires_auth  # <--- PASTE DECORATOR HERE
def admin_dashboard():
    category = request.args.get("category", "")
    search = request.args.get("search", "")

    query = CouncilMember.query

    if category:
        query = query.filter(CouncilMember.membership_category == category)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (CouncilMember.full_name.ilike(search_filter))
            | (CouncilMember.city_germany.ilike(search_filter))
            | (CouncilMember.occupation.ilike(search_filter))
            | (CouncilMember.phone_number.ilike(search_filter))
        )

    members = query.order_by(CouncilMember.submitted_at.desc()).all()

    return render_template(
        "admin.html",
        members=members,
        selected_category=category,
        search_query=search,
    )


@app.route("/admin/members/export")
@requires_auth  # <--- PASTE DECORATOR HERE ALSO
def export_members_csv():
    category = request.args.get("category", "")
    search = request.args.get("search", "")

    query = CouncilMember.query

    if category:
        query = query.filter(CouncilMember.membership_category == category)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (CouncilMember.full_name.ilike(search_filter))
            | (CouncilMember.city_germany.ilike(search_filter))
            | (CouncilMember.occupation.ilike(search_filter))
        )

    members = query.order_by(CouncilMember.submitted_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "Member ID",
            "Full Name",
            "Date of Birth (Month/Year)",
            "Gender",
            "Nationality",
            "Hometown (Ghana)",
            "City (Germany)",
            "Phone Number",
            "Membership Category",
            "Occupation",
            "Skills",
            "Referral Source",
            "Volunteer Commitment",
            "Submitted At",
        ]
    )

    for m in members:
        dob_formatted = m.date_of_birth.strftime("%Y-%m") if m.date_of_birth else ""
        skills_str = ", ".join(m.skills) if m.skills else ""
        submitted_str = (
            m.submitted_at.strftime("%Y-%m-%d %H:%M:%S") if m.submitted_at else ""
        )

        writer.writerow(
            [
                m.member_id,
                m.full_name,
                dob_formatted,
                m.gender,
                m.nationality,
                m.hometown_ghana,
                m.city_germany,
                m.phone_number,
                m.membership_category,
                m.occupation or "",
                skills_str,
                m.referral_source or "",
                m.volunteer_commitment,
                submitted_str,
            ]
        )

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = (
        f"attachment; filename=club_members_{datetime.now().strftime('%Y%m%d')}.csv"
    )
    response.headers["Content-type"] = "text/csv"
    return response


# ==========================================
# 7. Mentorship Management API Routes
# ==========================================
@app.route("/api/leaders/register", methods=["POST"])
def register_leader():
    data = request.get_json() or {}
    member_id = data.get("member_id")
    role = data.get("leadership_role", "Mentor")
    expertise = data.get("expertise_areas", [])
    bio = data.get("bio", "")
    max_mentees = data.get("max_mentees", 3)

    if not member_id:
        return jsonify({"status": "error", "message": "member_id is required"}), 400

    member = CouncilMember.query.filter_by(member_id=member_id).first()
    if not member:
        return jsonify({"status": "error", "message": "Member not found"}), 404

    existing_leader = Leader.query.filter_by(member_id=member_id).first()
    if existing_leader:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Member is already registered as a leader",
                }
            ),
            400,
        )

    new_leader = Leader(
        member_id=member_id,
        leadership_role=role,
        expertise_areas=expertise,
        bio=bio,
        max_mentees=max_mentees,
    )

    try:
        db.session.add(new_leader)
        db.session.flush()
        new_leader.generate_formatted_id()  # Sets leader_id = GC-L-001
        db.session.commit()

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Leader profile created successfully",
                    "leader_id": new_leader.leader_id,
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Database transaction failed",
                    "details": str(e),
                }
            ),
            500,
        )


@app.route("/api/mentorship/assign", methods=["POST"])
def assign_mentor():
    data = request.get_json() or {}
    leader_id = data.get("leader_id")
    student_member_id = data.get("student_member_id")
    notes = data.get("notes", "")

    if not leader_id or not student_member_id:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Both leader_id and student_member_id are required",
                }
            ),
            400,
        )

    leader = Leader.query.filter_by(leader_id=leader_id).first()
    if not leader or not leader.is_active:
        return (
            jsonify(
                {"status": "error", "message": "Valid active mentor (leader) not found"}
            ),
            404,
        )

    student = CouncilMember.query.filter_by(member_id=student_member_id).first()
    if not student:
        return jsonify({"status": "error", "message": "Student member not found"}), 404

    active_count = MentorshipAssignment.query.filter_by(
        leader_id=leader_id, status="ACTIVE"
    ).count()
    if active_count >= leader.max_mentees:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Mentor has reached maximum capacity ({leader.max_mentees})",
                }
            ),
            400,
        )

    existing_assignment = MentorshipAssignment.query.filter_by(
        leader_id=leader_id, student_member_id=student_member_id, status="ACTIVE"
    ).first()

    if existing_assignment:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Active mentorship assignment already exists for this pair",
                }
            ),
            400,
        )

    assignment = MentorshipAssignment(
        leader_id=leader_id,
        student_member_id=student_member_id,
        start_date=date.today(),
        status="ACTIVE",
        notes=notes,
    )

    try:
        db.session.add(assignment)
        db.session.flush()
        assignment.generate_formatted_id()  # Sets assignment_id = GC-MA-001
        db.session.commit()

        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Mentor '{leader.member.full_name}' assigned to '{student.full_name}' successfully!",
                    "assignment_id": assignment.assignment_id,
                    "start_date": assignment.start_date.isoformat(),
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Database transaction failed",
                    "details": str(e),
                }
            ),
            500,
        )


# ==========================================
# 8. Entry Point
# ==========================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
