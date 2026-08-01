import os
from app import app, db

# Paste your copied External Database URL between the quotes below:
EXTERNAL_DB_URL = "postgresql://gc_db_1c13_user:05B1IFjvHcaGSKqJy01G8M7amKH2AHbe@dpg-d9me388ae00c73f532i0-a.frankfurt-postgres.render.com/gc_db_1c13"

# Render external URLs start with postgresql://
if EXTERNAL_DB_URL.startswith("postgres://"):
    EXTERNAL_DB_URL = EXTERNAL_DB_URL.replace("postgres://", "postgresql://", 1)

# Temporarily override database URI to connect to Render directly
app.config["SQLALCHEMY_DATABASE_URI"] = EXTERNAL_DB_URL

print("Connecting to Render PostgreSQL database...")

with app.app_context():
    print("Dropping all existing tables...")
    db.drop_all()
    print("Creating all tables from scratch...")
    db.create_all()
    print("✅ SUCCESS: Render PostgreSQL database wiped and fully recreated!")