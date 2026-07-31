import pymysql

# --- DATABASE CONFIGURATION ---
HOST = "localhost"
USER = "root"
PASSWORD = "UB40ghana"  # <--- Change to your MySQL password
PORT = 3306

try:
    # Connect to MySQL server (without selecting a specific database)
    connection = pymysql.connect(
        host=HOST, user=USER, password=PASSWORD, port=PORT, autocommit=True
    )

    with connection.cursor() as cursor:
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS gc_professionals_club_db "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        )
        print("✔ Database 'gc_professionals_club_db' created successfully!")

finally:
    if "connection" in locals() and connection.open:
        connection.close()
