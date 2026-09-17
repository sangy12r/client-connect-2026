import sqlite3
import tempfile
from pathlib import Path
import secrets


# Streamlit Community Cloud's app source folder isn't reliably writable at
# runtime. Use the system temp directory instead so the database can always
# be created without any external setup. Note: this is temporary/ephemeral
# storage - data resets whenever the app reboots/redeploys/sleeps. This is
# a stand-in while Supabase approval is pending; switch get_connection()
# back to Postgres once that's ready for real client data.
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
            token_created_at TEXT,
            source TEXT DEFAULT 'Imported'
        )
        """
    )

    # Every column the app expects the "clients" table to have, with the
    # SQL type used to add it if it's ever missing (e.g. from an older
    # version of this schema). Self-healing for ANY column - if a future
    # column gets added to the CREATE TABLE above, add it here too.
    expected_columns = {
        "company": "TEXT NOT NULL DEFAULT ''",
        "contact_name": "TEXT NOT NULL DEFAULT ''",
        "designation": "TEXT",
        "mobile": "TEXT",
        "category": "TEXT",
        "priority": "TEXT DEFAULT 'Normal'",
        "rsvp_status": "TEXT DEFAULT 'Pending'",
        "attendees": "INTEGER DEFAULT 0",
        "guest_name": "TEXT",
        "rsvp_date": "TEXT",
        "invitation_sent": "INTEGER DEFAULT 0",
        "invitation_opened": "INTEGER DEFAULT 0",
        "checked_in": "INTEGER DEFAULT 0",
        "check_in_time": "TEXT",
        "rsvp_token": "TEXT",
        "token_created_at": "TEXT",
        "source": "TEXT DEFAULT 'Imported'",
    }

    existing_columns = {
        row[1]
        for row in cursor.execute("PRAGMA table_info(clients)").fetchall()
    }

    for column_name, column_type in expected_columns.items():
        if column_name not in existing_columns:
            cursor.execute(
                f"ALTER TABLE clients ADD COLUMN {column_name} {column_type}"
            )

    connection.commit()
    connection.close()


def generate_rsvp_token():
    return secrets.token_urlsafe(24)
