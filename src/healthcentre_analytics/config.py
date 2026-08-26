from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATABASE_DIR = PROJECT_ROOT / "database"
SQL_DIR = PROJECT_ROOT / "sql"
REPORTS_DIR = PROJECT_ROOT / "reports"
CHARTS_DIR = PROJECT_ROOT / "assets" / "charts"

DB_PATH = DATABASE_DIR / "health_centre.db"

RANDOM_SEED = 42
STUDENT_COUNT = 6500
VISIT_COUNT = 52000

START_DATE = "2024-01-01"
END_DATE = "2025-12-31"

DEPARTMENTS = [
    "Computer Science",
    "Electronics",
    "Mechanical",
    "Civil",
    "Electrical",
    "Biotechnology",
    "Business Administration",
    "Applied Sciences",
]

PROGRAMS = ["B.Tech", "M.Tech", "MBA", "B.Sc", "M.Sc"]
HOSTELS = ["Hostel A", "Hostel B", "Hostel C", "Hostel D", "Hostel E", "Day Scholar"]
SEGMENTS = ["Hostel Resident", "Day Scholar", "First Year", "Final Year", "Sports Participant"]

SERVICE_CATEGORIES = [
    "General Consultation",
    "Respiratory",
    "Gastrointestinal",
    "Musculoskeletal",
    "Skin",
    "Injury",
    "Preventive Care",
    "Follow-up",
    "Referral Coordination",
    "Other",
]

VISIT_CATEGORIES = ["Walk-in", "Scheduled", "Emergency Support", "Follow-up"]
PRIORITIES = ["Low", "Routine", "Urgent"]
OUTCOMES = ["Resolved", "Follow-up Advised", "Referred", "Observation", "Information Provided"]

STAFF_ROWS = [
    ("STF001", "Medical Officer", "Consultation", "Morning", 720),
    ("STF002", "Medical Officer", "Consultation", "Afternoon", 690),
    ("STF003", "Nurse", "First Aid", "Morning", 780),
    ("STF004", "Nurse", "First Aid", "Evening", 650),
    ("STF005", "Health Assistant", "Registration", "Morning", 950),
    ("STF006", "Health Assistant", "Follow-up Coordination", "Afternoon", 520),
    ("STF007", "Reception/Registration", "Registration", "Full Day", 1100),
    ("STF008", "Health Assistant", "Referral Desk", "Afternoon", 360),
]

SERVICES_ROWS = [
    ("SRV001", "General Consultation", "General Consultation", 760, 25),
    ("SRV002", "Respiratory Care", "Respiratory", 260, 30),
    ("SRV003", "Gastrointestinal Support", "Gastrointestinal", 190, 30),
    ("SRV004", "Musculoskeletal Support", "Musculoskeletal", 165, 35),
    ("SRV005", "Skin Consultation", "Skin", 150, 30),
    ("SRV006", "First Aid and Injury", "Injury", 220, 20),
    ("SRV007", "Preventive Consultation", "Preventive Care", 210, 20),
    ("SRV008", "Follow-up", "Follow-up", 185, 25),
    ("SRV009", "Referral Coordination", "Referral Coordination", 85, 20),
    ("SRV010", "Other Support", "Other", 135, 25),
]

CATEGORY_ALIASES = {
    "Gen Consultation": "General Consultation",
    "general consultation": "General Consultation",
    "Resp": "Respiratory",
    "Gastro": "Gastrointestinal",
    "Muskuloskeletal": "Musculoskeletal",
    "Preventative Care": "Preventive Care",
    "Referral": "Referral Coordination",
}
