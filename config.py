# Meítǐ Shāngchéng — Employee Management System (EMS)
# Flask + SQLAlchemy configuration.
#
# Database: MySQL is the target platform per the Technical Constraints
# (project plan 8.3), but SQLite works out of the box so the prototype can be
# started with zero infrastructure. Pick with the EMS_DATABASE env variable:
#
#   set EMS_DATABASE=mysql        (Windows cmd)
#   export EMS_DATABASE=mysql     (Git Bash / macOS / Linux)
#
# Required Python packages: flask, flask-sqlalchemy, pymysql (only for MySQL),
# python-dotenv (optional, loads a .env file).

import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

try:  # optional convenience: read variables from a local .env file
    from dotenv import load_dotenv

    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:  # pragma: no cover - dotenv is optional
    pass


def _mysql_uri() -> str:
    """Build the MySQL connection string from individual settings."""
    user = os.environ.get("MYSQL_USER", "ems_user")
    password = os.environ.get("MYSQL_PASSWORD", "ems_password")
    host = os.environ.get("MYSQL_HOST", "127.0.0.1")
    port = os.environ.get("MYSQL_PORT", "3306")
    database = os.environ.get("MYSQL_DATABASE", "ems")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


class Config:
    """Base configuration shared by every environment."""

    SECRET_KEY = os.environ.get("EMS_SECRET_KEY", "ems-dev-secret-key-change-me")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Business rules taken from the URS / project plan.
    SHIFT_TEMPLATES = [
        {
            "code": "EARLY",
            "name": "Early shift",
            "start_time": "08:00",
            "end_time": "12:00",
        },
        {
            "code": "MID",
            "name": "Mid shift",
            "start_time": "12:00",
            "end_time": "16:00",
        },
        {
            "code": "LATE",
            "name": "Late shift",
            "start_time": "16:00",
            "end_time": "20:00",
        },
    ]

    WEEKDAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    DEFAULT_WORKING_DAYS = [0, 1, 2, 3, 4]  # URS 1.4: 5 working days per week
    MAX_SHIFTS_PER_WEEK = 7

    # How many days ahead an employee may state availability (FR-03).
    PREFERENCE_WINDOW_DAYS = 14

    # Self-service registration switch.  Keep it on for the demo; set
    # EMS_ALLOW_REGISTRATION=0 before exposing the site on the internet.
    ALLOW_SELF_REGISTRATION = os.environ.get("EMS_ALLOW_REGISTRATION", "1") == "1"

    # Non-functional requirement NFR-02: every user action answers within 1s.
    JSON_SORT_KEYS = False
    TEMPLATES_AUTO_RELOAD = True

    @staticmethod
    def database_uri() -> str:
        backend = os.environ.get("EMS_DATABASE", "sqlite").strip().lower()
        if backend == "mysql":
            return _mysql_uri()
        if backend == "memory":
            return "sqlite://"
        path = os.environ.get(
            "EMS_SQLITE_PATH", os.path.join(BASE_DIR, "instance", "ems.sqlite3")
        )
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return "sqlite:///" + path.replace("\\", "/")

    SQLALCHEMY_DATABASE_URI = database_uri()


class TestConfig(Config):
    """In-memory database used by the automated test suite."""

    TESTING = True
    WTF_CSRF_ENABLED = False  # the hand-rolled CSRF guard is bypassed in tests
    SQLALCHEMY_DATABASE_URI = "sqlite://"
