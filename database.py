import secrets

import psycopg2
import streamlit as st


class _PGCursorWrapper:
    """Makes a psycopg2 cursor behave like sqlite3's: supports the same
    .execute(sql, params).fetchone()/.fetchall() chaining, and translates
    sqlite-style "?" placeholders to psycopg2-style "%s" automatically so
    none of the existing SQL strings elsewhere in the app need to change."""

    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, sql, params=None):
        translated_sql = sql.replace("?", "%s")
        self._cursor.execute(translated_sql, params or ())
        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    @property
    def description(self):
        return self._cursor.description

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def __iter__(self):
        return iter(self._cursor)

    def close(self):
        self._cursor.close()


class _PGConnectionWrapper:
    """Makes a psycopg2 connection behave like sqlite3's Connection object:
    connection.execute(sql, params) works directly, and connection.cursor()
    works for pandas' read_sql_query()."""

    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql, params=None):
        cursor = self._conn.cursor()
        return _PGCursorWrapper(cursor).execute(sql, params)

    def cursor(self):
        return _PGCursorWrapper(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

    def rollback(self):
        self._conn.rollback()


def get_connection():
    return _PGConnectionWrapper(psycopg2.connect(st.secrets["DATABASE_URL"]))


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            company TEXT NOT NULL DEFAULT '',
            contact_name TEXT NOT NULL DEFAULT '',
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

    cursor.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_name = 'clients'"
    )
    existing_columns = {row[0] for row in cursor.fetchall()}

    for column_name, column_type in expected_columns.items():
        if column_name not in existing_columns:
            cursor.execute(f"ALTER TABLE clients ADD COLUMN {column_name} {column_type}")

    connection.commit()
    connection.close()


def generate_rsvp_token():
    return secrets.token_urlsafe(24)
