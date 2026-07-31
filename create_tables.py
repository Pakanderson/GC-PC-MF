import pymysql

# --- DATABASE CONFIGURATION ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "UB40ghana",  # Update password
    "database": "gc_professionals_club_db",
    "port": 3306,
    "autocommit": True,
}

# --- SQL TABLE SCHEMAS ---
CREATE_CLUB_MEMBERS_TABLE = """
CREATE TABLE IF NOT EXISTS club_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id VARCHAR(20) UNIQUE,                -- Auto-filled as GC-PC-001, etc.
    full_name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(50) NOT NULL,
    nationality VARCHAR(100) NOT NULL,
    hometown_ghana VARCHAR(150) NOT NULL,
    city_germany VARCHAR(150) NOT NULL,
    phone_number VARCHAR(50) NOT NULL,
    membership_category VARCHAR(100) NOT NULL,
    occupation VARCHAR(150),
    skills JSON,
    referral_source VARCHAR(100),
    volunteer_commitment VARCHAR(50) NOT NULL,
    comments TEXT,
    gdpr_consent_given BOOLEAN NOT NULL DEFAULT TRUE,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_LEADERS_TABLE = """
CREATE TABLE IF NOT EXISTS leaders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    leader_id VARCHAR(20) UNIQUE,
    member_id VARCHAR(20) NOT NULL UNIQUE,      -- References GC-PC-001
    leadership_role VARCHAR(100) NOT NULL,
    expertise_areas JSON,
    bio TEXT,
    max_mentees INT DEFAULT 3,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES club_members(member_id) ON DELETE CASCADE
);
"""

CREATE_MENTORSHIP_TABLE = """
CREATE TABLE IF NOT EXISTS mentorship_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id VARCHAR(20) UNIQUE,
    leader_id VARCHAR(20) NOT NULL,
    student_member_id VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'ACTIVE',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (leader_id) REFERENCES leaders(leader_id) ON DELETE CASCADE,
    FOREIGN KEY (student_member_id) REFERENCES club_members(member_id) ON DELETE CASCADE
);
"""


def execute_schema():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_CLUB_MEMBERS_TABLE)
            cursor.execute(CREATE_LEADERS_TABLE)
            cursor.execute(CREATE_MENTORSHIP_TABLE)
            print("✔ Tables updated to use GC-PC-001 format successfully!")
    finally:
        connection.close()


if __name__ == "__main__":
    execute_schema()
