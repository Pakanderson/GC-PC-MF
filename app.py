import os
import io
import csv
from datetime import datetime
from flask import Flask, request, jsonify, render_template, make_response
from flask_cors import CORS
from flask_mail import Mail, Message
from pydantic import ValidationError

from models import db, CouncilMember
from schemas import MemberRegistrationSchema

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# ==========================================
# 1. Database Configuration (3-Tier Fallback)
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
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)
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
    "Ghana Council NRW e.V.",
    os.getenv("MAIL_USERNAME", "info@ghanacouncil-nrw.de"),
)

# Initialize Extensions
db.init_app(app)
mail = Mail(app)

# Initialize Tables Contextually
with app.app_context():
    db.create_all()


# ==========================================
# 3. Helper Functions & Email Dispatch
# ==========================================
def send_confirmation_email(recipient_email, full_name, category):
    """Sends registration confirmation email to the applicant."""
    try:
        msg = Message(
            subject="Ghana Council NRW Professionals Club — Registration Confirmation",
            recipients=[recipient_email],
        )
        msg.body = f"""Dear {full_name},

Thank you for registering with the Ghana Council NRW Professionals Club!

We have successfully received your membership application as a: {category}.
Our administrative team is reviewing your profile and will follow up with event invites, networking updates, or mentorship matching shortly.

Kind regards,
Ghana Council NRW e.V. Initiative
Düsseldorf, Germany
info@ghanacouncil-nrw.de
www.ghanacouncil-nrw.de
"""
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <h2 style="color: #006B3F; text-align: center;">Ghana Council NRW e.V.</h2>
            <p style="text-align: center; color: #666; font-size: 14px;">Professionals Club — Membership Registration</p>
            <hr style="border: 0; border-top: 1px solid #ccc;">
            <p>Welcome, <strong>{full_name}</strong>!</p>
            <p>Thank you for submitting your membership application to the Ghana Council NRW Professionals Club.</p>
            <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #006B3F; margin: 20px 0;">
                <p style="margin: 0; font-weight: bold;">Membership Category: <span style="color: #006B3F;">{category}</span></p>
                <p style="margin: 5px 0 0 0; color: #555;">Status: Application Received & Under Review</p>
            </div>
            <p>If you have any questions or need to update your details, please feel free to contact us at <a href="mailto:info@ghanacouncil-nrw.de">info@ghanacouncil-nrw.de</a>.</p>
            <br>
            <p style="margin: 0;">Warm regards,</p>
            <p style="margin: 0; font-weight: bold;">Ghana Council NRW e.V. Team</p>
            <p style="color: #888; font-size: 12px; margin-top: 5px;">Düsseldorf, Germany</p>
        </div>
        """
        mail.send(msg)
        return True
    except Exception as e:
        print(f"[Email Error] Failed to send email to {recipient_email}: {str(e)}")
        return False


# ==========================================
# 4. Web & API Routes
# ==========================================


@app.route("/")
def home():
    """Renders the main membership registration form."""
    return render_template("index.html")


@app.route("/api/register", methods=["POST"])
def register_member():
    """Handles submission of Page 1 (Member/Mentee) or Page 1 + Page 2 (Mentor) data."""
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No JSON payload provided"}), 400

    # Validate incoming payload against Pydantic schema
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

    # Convert YYYY-MM dob string to standard SQL Date format (YYYY-MM-01)
    dob_date = None
    if validated_data.dob_month_year:
        try:
            dob_date = datetime.strptime(
                f"{validated_data.dob_month_year}-01", "%Y-%m-%d"
            ).date()
        except ValueError:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Invalid date format for Date of Birth. Use YYYY-MM.",
                    }
                ),
                400,
            )

    # Map payload to database model
    new_member = CouncilMember(
        # Profile Photo
        profile_photo=validated_data.profile_photo,
        # Page 1: Personal & Contact Info
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
        # Mentee Block (Page 1)
        mentee_seeking=validated_data.mentee_seeking,
        mentee_goals=validated_data.mentee_goals,
        mentor_preferred_background=validated_data.mentor_preferred_background,
        # Member Block (Page 1)
        workshop_topics=validated_data.workshop_topics,
        help_organize_events=validated_data.help_organize_events,
        # Mentor Professional & Matching Fields (Page 2)
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
        # Engagement & Consent
        event_availability=validated_data.event_availability,
        gdpr_consent=validated_data.gdpr_consent,
        terms_consent=validated_data.terms_consent,
    )

    try:
        db.session.add(new_member)
        db.session.flush()  # Acquire auto-increment ID

        # Generate custom readable ID (e.g., GC-PC-001)
        new_member.generate_formatted_id()
        db.session.commit()

        # Send confirmation email
        email_sent = send_confirmation_email(
            recipient_email=new_member.email,
            full_name=new_member.full_name,
            category=new_member.membership_category,
        )

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Registration submitted successfully!",
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


@app.route("/admin/members", methods=["GET"])
def view_members():
    """Renders administrative member dashboard."""
    category = request.args.get("category")
    query = CouncilMember.query

    if category:
        query = query.filter_by(membership_category=category)

    members = query.order_by(CouncilMember.id.desc()).all()
    return render_template("admin.html", members=members, selected_category=category)


@app.route("/admin/members/export", methods=["GET"])
def export_members_csv():
    """Exports all members or filtered member list as CSV."""
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
            "Profession / Job Title",
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
                m.job_title or m.profession or "",
                m.city_region_germany,
                m.submitted_at.strftime("%Y-%m-%d %H:%M:%S") if m.submitted_at else "",
            ]
        )

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=club_members.csv"
    output.headers["Content-type"] = "text/csv"
    return output


# ==========================================
# 5. Application Entry Point
# ==========================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
