import sqlite3
import tempfile
from pathlib import Path
import secrets


# Streamlit Community Cloud's app source folder isn't reliably writable at
# runtime. Use the system temp directory instead so the database can always
# be created. Note: like the source folder, this is ephemeral storage too -
# data will still reset whenever the app reboots/redeploys. Export your CSVs
# regularly from the app's export buttons to keep a backup.
DATABASE_PATH = Path(tempfile.gettempdir()) / "client_connect.db"


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            designation TEXT,
            email TEXT NOT NULL UNIQUE,
            mobile TEXT,
            category TEXT,
            priority TEXT DEFAULT 'Normal',
            rsvp_status TEXT DEFAULT 'Pending',
            attendees INTEGER DEFAULT 0,
            guest_name TEXT,
            rsvp_date TEXT,
            invitation_sent INTEGER DEFAULT 0,
            invitation_opened INTEGER DEFAULT 0,
            checked_in INTEGER DEFAULT 0,
            check_in_time TEXT,
            rsvp_token TEXT,
            token_created_at TEXT
        )
        """
    )

    existing_columns = [
        row[1]
        for row in cursor.execute("PRAGMA table_info(clients)").fetchall()
    ]

    if "rsvp_token" not in existing_columns:
        cursor.execute("ALTER TABLE clients ADD COLUMN rsvp_token TEXT")

    if "token_created_at" not in existing_columns:
        cursor.execute("ALTER TABLE clients ADD COLUMN token_created_at TEXT")

    connection.commit()
    connection.close()


def generate_rsvp_token():
    return secrets.token_urlsafe(24)
