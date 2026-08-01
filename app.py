import os
import io
import csv
from functools import wraps
from datetime import datetime
from flask import Flask, request, jsonify, render_template, make_response, Response
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    make_response,
    flash,
)
from flask_cors import CORS
from flask_mail import Mail, Message
from pydantic import ValidationError

from models import db, CouncilMember, MentorshipAssignment
from schemas import MemberRegistrationSchema

app = Flask(__name__)
CORS(app)

# ==========================================
# 1. Database Configuration
# ==========================================
db_url = os.getenv("DATABASE_URL")

if db_url and db_url.strip():
    # --- Production / Cloud Database (Render PostgreSQL) ---
    db_url = db_url.strip()
    # Fix Render's legacy 'postgres://' prefix for SQLAlchemy
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url

elif os.getenv("DB_PASS") and os.getenv("DB_PASS").strip():
    # --- Local Development (MySQL) ---
    db_user = os.getenv("DB_USER", "root")
    db_pass = os.getenv("DB_PASS").strip()
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "gc_professionals_club_db")
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    )

else:
    # --- Local Emergency Fallback Only (SQLite) ---
    instance_path = os.path.join(app.root_path, "instance")
    os.makedirs(instance_path, exist_ok=True)
    db_file_path = os.path.join(instance_path, "club.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_file_path}"
    print("⚠️ WARNING: Running on local SQLite! Data will reset on deployment.")

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
    "Ghana Council NRW e.V.",
    os.getenv("MAIL_USERNAME", "info@ghanacouncil-nrw.de"),
)

db.init_app(app)
mail = Mail(app)

with app.app_context():
    db.create_all()

# ==========================================
# 3. Admin Security (Supports Up to 5 Accounts)
# ==========================================
ADMIN_ACCOUNTS = {
    os.getenv("ADMIN_USER", "admin"): os.getenv("ADMIN_PASS", "GhanaCouncil2026!")
}

# Load individual admin accounts (ADMIN1_USER/PASS through ADMIN5_USER/PASS)
for i in range(1, 6):
    u = os.getenv(f"ADMIN{i}_USER")
    p = os.getenv(f"ADMIN{i}_PASS")
    if u and p:
        ADMIN_ACCOUNTS[u] = p


def requires_admin_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if (
            not auth
            or auth.username not in ADMIN_ACCOUNTS
            or ADMIN_ACCOUNTS[auth.username] != auth.password
        ):
            return Response(
                "Admin Authentication Required",
                401,
                {"WWW-Authenticate": 'Basic realm="Login Required"'},
            )
        return f(*args, **kwargs)

    return decorated


# ==========================================
# 4. Helper Functions
# ==========================================
def send_confirmation_email(recipient_email, full_name, category):
    try:
        msg = Message(
            subject="Ghana Council NRW Professionals Club — Registration Confirmation",
            recipients=[recipient_email],
        )
        msg.body = f"Dear {full_name},\n\nThank you for registering with the Ghana Council NRW Professionals Club as a {category}.\n\nKind regards,\nGhana Council NRW e.V."
        mail.send(msg)
        return True
    except Exception as e:
        print(f"[Email Error] {str(e)}")
        return False


# ==========================================
# 5. Public Routes
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

    # Prevent duplicate registrations by Email or Phone
    existing_member = CouncilMember.query.filter(
        (CouncilMember.email == validated_data.email)
        | (CouncilMember.phone == validated_data.phone)
    ).first()

    if existing_member:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "A member with this email or phone number is already registered.",
                }
            ),
            409,
        )

    dob_date = None
    if validated_data.dob_month_year:
        try:
            dob_date = datetime.strptime(
                f"{validated_data.dob_month_year}-01", "%Y-%m-%d"
            ).date()
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid DOB format"}), 400

    new_member = CouncilMember(
        profile_photo=validated_data.profile_photo,
        full_name=validated_data.full_name,
        email=validated_data.email,
        date_of_birth=dob_date,
        gender=validated_data.gender,
        nationality=validated_data.nationality,
        hometown_ghana=validated_data.hometown_ghana,
        residence_germany=validated_data.residence_germany,
        phone=validated_data.phone,
        preferred_contact_method=validated_data.preferred_contact_method,
        city_region_germany=validated_data.city_region_germany,
        languages_spoken=validated_data.languages_spoken,
        hear_about_club=validated_data.hear_about_club,
        profession=validated_data.profession,
        comments=validated_data.comments,
        membership_category=validated_data.membership_category,
        mentee_seeking=validated_data.mentee_seeking,
        mentee_goals=validated_data.mentee_goals,
        mentor_preferred_background=validated_data.mentor_preferred_background,
        workshop_topics=validated_data.workshop_topics,
        help_organize_events=validated_data.help_organize_events,
        job_title=validated_data.job_title,
        industry_sector=validated_data.industry_sector,
        years_experience=validated_data.years_experience,
        qualification_field=validated_data.qualification_field,
        key_skills=validated_data.key_skills,
        linkedin_profile=validated_data.linkedin_profile,
        mentor_areas=validated_data.mentor_areas,
        mentoring_format=validated_data.mentoring_format,
        max_mentees=validated_data.max_mentees,
        mentor_availability=validated_data.mentor_availability,
        workshop_speaker=validated_data.workshop_speaker,
        event_availability=validated_data.event_availability,
        gdpr_consent=validated_data.gdpr_consent,
        terms_consent=validated_data.terms_consent,
        status="Pending",  # Requires Admin Review
    )

    try:
        db.session.add(new_member)
        db.session.flush()
        new_member.generate_formatted_id()
        db.session.commit()
        send_confirmation_email(
            new_member.email, new_member.full_name, new_member.membership_category
        )
        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Registration submitted successfully! Pending admin review.",
                    "member_id": new_member.member_id,
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
# 6. Protected Admin Routes
# ==========================================


@app.route("/admin/members", methods=["GET"])
@requires_admin_auth
def view_members():
    category = request.args.get("category")
    status_filter = request.args.get("status")

    query = CouncilMember.query
    if category:
        query = query.filter_by(membership_category=category)
    if status_filter:
        query = query.filter_by(status=status_filter)

    members = query.order_by(CouncilMember.id.desc()).all()
    mentors = CouncilMember.query.filter_by(
        membership_category="Mentor", status="Accepted"
    ).all()
    mentees = CouncilMember.query.filter_by(
        membership_category="Mentee", status="Accepted"
    ).all()
    assignments = MentorshipAssignment.query.order_by(
        MentorshipAssignment.id.desc()
    ).all()

    return render_template(
        "admin.html",
        members=members,
        selected_category=category,
        selected_status=status_filter,
        mentors=mentors,
        mentees=mentees,
        assignments=assignments,
    )


# --- HTML Form Actions for Admin Dashboard ---


# ==========================================
# 6. Protected Admin Routes (HTML Actions)
# ==========================================


@app.route("/admin/members/<int:member_id>/accept", methods=["POST"])
@requires_admin_auth
def accept_member_html(member_id):
    try:
        member = CouncilMember.query.get(member_id)
        if member:
            member.status = "Accepted"
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error accepting member {member_id}: {e}")
    return redirect(url_for("view_members"))


@app.route("/admin/members/<int:member_id>/reject", methods=["POST"])
@requires_admin_auth
def reject_member_html(member_id):
    try:
        member = CouncilMember.query.get(member_id)
        if member:
            member.status = "Rejected"
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error rejecting member {member_id}: {e}")
    return redirect(url_for("view_members"))


@app.route("/admin/members/<int:member_id>/remove", methods=["POST"])
@requires_admin_auth
def delete_member_html(member_id):
    try:
        member = CouncilMember.query.get(member_id)
        if member:
            db.session.delete(member)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting member {member_id}: {e}")
    return redirect(url_for("view_members"))


# --- API Routes for JSON updates ---


@app.route("/admin/members/<int:member_id>/status", methods=["POST"])
@requires_admin_auth
def update_member_status(member_id):
    data = request.get_json()
    new_status = data.get("status")

    if new_status not in ["Accepted", "Rejected", "Pending"]:
        return jsonify({"status": "error", "message": "Invalid status value"}), 400

    member = CouncilMember.query.get_or_404(member_id)
    member.status = new_status
    db.session.commit()
    return jsonify(
        {"status": "success", "message": f"Member status updated to {new_status}"}
    )


@app.route("/admin/members/<int:member_id>/delete", methods=["DELETE"])
@requires_admin_auth
def delete_member(member_id):
    member = CouncilMember.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    return jsonify(
        {"status": "success", "message": "Member record deleted successfully"}
    )


@app.route("/admin/assign-mentorship", methods=["POST"])
@requires_admin_auth
def assign_mentorship():
    data = request.get_json()
    mentor_id = data.get("mentor_id")
    mentee_id = data.get("mentee_id")
    focus_area = data.get("focus_area")
    end_date_str = data.get("end_date")

    if not mentor_id or not mentee_id:
        return (
            jsonify({"status": "error", "message": "Mentor and Mentee are required"}),
            400,
        )

    end_date = None
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return (
                jsonify({"status": "error", "message": "Invalid end date format"}),
                400,
            )

    assignment = MentorshipAssignment(
        mentor_id=mentor_id,
        mentee_id=mentee_id,
        focus_area=focus_area,
        end_date=end_date,
        notes=data.get("notes"),
    )

    db.session.add(assignment)
    db.session.commit()
    return jsonify(
        {"status": "success", "message": "Mentorship assignment created successfully!"}
    )


@app.route("/admin/members/export", methods=["GET"])
@requires_admin_auth
def export_members_csv():
    category = request.args.get("category")
    query = CouncilMember.query
    if category:
        query = query.filter_by(membership_category=category)

    members = query.order_by(CouncilMember.id.asc()).all()

    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(
        [
            "Member ID",
            "Full Name",
            "Email",
            "Phone",
            "Category",
            "Status",
            "City",
            "Submitted At",
        ]
    )

    for m in members:
        writer.writerow(
            [
                m.member_id,
                m.full_name,
                m.email,
                m.phone,
                m.membership_category,
                m.status,
                m.city_region_germany,
                m.submitted_at.strftime("%Y-%m-%d %H:%M:%S") if m.submitted_at else "",
            ]
        )

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=club_members.csv"
    output.headers["Content-type"] = "text/csv"
    return output


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
