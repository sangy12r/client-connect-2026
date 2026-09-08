import sqlite3
from pathlib import Path
import secrets
from datetime import datetime

DATABASE_PATH = Path(__file__).parent / "client_connect_demo.db"

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            designation TEXT,
            email TEXT NOT NULL UNIQUE,
            category TEXT,
            priority TEXT DEFAULT 'Normal',
            rsvp_status TEXT DEFAULT 'Pending',
            rsvp_date TEXT,
            invitation_sent INTEGER DEFAULT 0,
            invitation_opened INTEGER DEFAULT 0,
            checked_in INTEGER DEFAULT 0,
            check_in_time TEXT,
            rsvp_token TEXT UNIQUE,
            token_created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def generate_rsvp_token():
    return secrets.token_urlsafe(24)

def seed_demo_data():
    initialize_database()
    conn = get_connection()
    if conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]:
        conn.close()
        return
    rows = [
        ("ABC Shipping", "Mr Test Client", "General Manager", "test1@example.com", "Shipping", "High", "Accepted", "2026-09-05 10:15:00"),
        ("XYZ Logistics", "Ms Test Client", "Director", "test2@example.com", "Logistics", "Normal", "Pending", None),
        ("PQR Marine", "Mr Demo Client", "Managing Director", "test3@example.com", "Marine", "High", "Declined", "2026-09-06 14:30:00"),
    ]
    for company, contact, designation, email, category, priority, status, rsvp_date in rows:
        conn.execute("""
            INSERT INTO clients
            (company, contact_name, designation, email, category, priority,
             rsvp_status, rsvp_date, invitation_sent, rsvp_token, token_created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        """, (company, contact, designation, email, category, priority, status,
              rsvp_date, generate_rsvp_token(), datetime.now().isoformat(timespec="seconds")))
    conn.commit()
    conn.close()
