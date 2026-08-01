import os
import pymysql

# Database connection credentials from environment or defaults
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "your_mysql_password")  # Replace with your local MySQL password
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "gc_professionals_club_db")

def create_database():
    connection = None
    try:
        # Connect to MySQL server (without selecting a database)
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT,
            autocommit=True
        )
        
        with connection.cursor() as cursor:
            # Create Database with UTF-8 support
            sql = f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            cursor.execute(sql)
            print(f"[SUCCESS] Database '{DB_NAME}' created or already exists!")
            
    except Exception as e:
        print(f"[ERROR] Failed to create database: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    create_database()