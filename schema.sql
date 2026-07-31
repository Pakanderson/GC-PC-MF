CREATE TABLE council_members (
    member_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    full_name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(50) NOT NULL,
    nationality VARCHAR(100) NOT NULL,
    hometown_ghana VARCHAR(150) NOT NULL,
    city_germany VARCHAR(150) NOT NULL,
    phone_number VARCHAR(50) NOT NULL,
    membership_category VARCHAR(100) NOT NULL,
    occupation VARCHAR(150),
    skills JSON,                             -- Replaced Postgres TEXT[] with MySQL JSON
    referral_source VARCHAR(100),
    volunteer_commitment VARCHAR(50) NOT NULL,
    comments TEXT,
    gdpr_consent_given BOOLEAN NOT NULL DEFAULT TRUE,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 



SELECT * FROM gc_professionals_club_db.club_members;