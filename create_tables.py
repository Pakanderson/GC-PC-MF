import os
import pymysql

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv(
    "DB_PASS", "your_mysql_password"
)  # Replace with your local MySQL password
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "gc_professionals_club_db")

# Table SQL Schemas
SQL_CREATE_CLUB_MEMBERS = """
CREATE TABLE IF NOT EXISTS club_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id VARCHAR(50) UNIQUE,
    
    -- Page 1: Personal & Contact Info
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    date_of_birth DATE NULL,
    gender VARCHAR(50) NULL,
    nationality VARCHAR(100) NULL,
    hometown_ghana VARCHAR(150) NULL,
    residence_germany VARCHAR(150) NULL,
    phone VARCHAR(50) NOT NULL,
    preferred_contact_method VARCHAR(50) NULL,
    city_region_germany VARCHAR(150) NULL,
    languages_spoken JSON NULL,
    
    -- Page 1: Professional Background
    job_title VARCHAR(255) NULL,
    industry_sector VARCHAR(150) NULL,
    years_experience VARCHAR(50) NULL,
    qualification_field VARCHAR(255) NULL,
    key_skills JSON NULL,
    linkedin_profile VARCHAR(255) NULL,
    membership_category VARCHAR(50) NOT NULL,
    
    -- Page 2: Mentor Block
    mentor_areas JSON NULL,
    mentoring_format VARCHAR(50) NULL,
    max_mentees VARCHAR(20) NULL,
    mentor_availability JSON NULL,
    workshop_speaker VARCHAR(20) NULL,
    
    -- Page 2: Mentee Block
    mentee_seeking JSON NULL,
    mentee_goals TEXT NULL,
    mentor_preferred_background VARCHAR(255) NULL,
    
    -- Page 2: Member Block
    workshop_topics JSON NULL,
    help_organize_events VARCHAR(20) NULL,
    
    -- Engagement, Consent & General Comments
    event_availability JSON NULL,
    hear_about_club VARCHAR(150) NULL,
    gdpr_consent BOOLEAN NOT NULL DEFAULT FALSE,
    terms_consent BOOLEAN NOT NULL DEFAULT FALSE,
    profession VARCHAR(255) NULL,
    comments TEXT NULL,
    
    -- Timestamps
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_category (membership_category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

SQL_CREATE_LEADERS = """
CREATE TABLE IF NOT EXISTS leaders (
    leader_id VARCHAR(50) PRIMARY KEY,
    member_id INT NOT NULL,
    role_title VARCHAR(150) NOT NULL,
    bio TEXT NULL,
    active_status BOOLEAN DEFAULT TRUE,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES club_members(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

SQL_CREATE_MENTORSHIP_ASSIGNMENTS = """
CREATE TABLE IF NOT EXISTS mentorship_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mentor_member_id INT NOT NULL,
    mentee_member_id INT NOT NULL,
    focus_area VARCHAR(255) NULL,
    status VARCHAR(50) DEFAULT 'Active',
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ended_at DATETIME NULL,
    FOREIGN KEY (mentor_member_id) REFERENCES club_members(id) ON DELETE CASCADE,
    FOREIGN KEY (mentee_member_id) REFERENCES club_members(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

SQL_CREATE_WORKSHOPS_WEBINARS = """
CREATE TABLE IF NOT EXISTS workshops_webinars (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    event_type VARCHAR(50) NOT NULL, -- Workshop, Webinar, Forum
    speaker_member_id INT NULL,
    scheduled_at DATETIME NULL,
    location_url VARCHAR(255) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (speaker_member_id) REFERENCES club_members(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""


def create_tables():
    connection = None
    try:
        # Connect directly to target database
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT,
            database=DB_NAME,
            autocommit=True,
        )

        with connection.cursor() as cursor:
            print("[INFO] Creating tables in database...")
            cursor.execute(SQL_CREATE_CLUB_MEMBERS)
            print("  - Table 'club_members' created successfully.")
            cursor.execute(SQL_CREATE_LEADERS)
            print("  - Table 'leaders' created successfully.")
            cursor.execute(SQL_CREATE_MENTORSHIP_ASSIGNMENTS)
            print("  - Table 'mentorship_assignments' created successfully.")
            cursor.execute(SQL_CREATE_WORKSHOPS_WEBINARS)
            print("  - Table 'workshops_webinars' created successfully.")

        print(f"[SUCCESS] All tables initialized in database '{DB_NAME}'!")

    except Exception as e:
        print(f"[ERROR] Failed to create tables: {e}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    create_tables()
