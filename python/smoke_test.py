from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from healthcentre_analytics import config
from healthcentre_analytics.database import run_sql_file
from healthcentre_analytics.reporting import load_processed_data


def assert_file(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"Missing expected file: {path}")


def main() -> None:
    expected_files = [
        config.DATA_PROCESSED / "students.csv",
        config.DATA_PROCESSED / "visits_clean.csv",
        config.DB_PATH,
        config.REPORTS_DIR / "monthly_management_report_latest.md",
        config.PROJECT_ROOT / "docs" / "business_questions.md",
        config.PROJECT_ROOT / "README.md",
    ]
    for path in expected_files:
        assert_file(path)

    data = load_processed_data()
    assert len(data["students"]) == 6500
    assert 30000 <= len(data["visits"]) <= 80000
    assert data["visits"]["student_id"].nunique() > 6000
    assert data["visits"]["wait_time_minutes"].min() >= 0
    assert data["visits"]["consultation_duration"].between(1, 120).all()
    assert data["visits"]["satisfaction_score"].between(1, 5).all()
    assert data["capacity"]["capacity_utilization_pct"].gt(100).sum() > 0

    with sqlite3.connect(config.DB_PATH) as conn:
        visit_rows = pd.read_sql_query("SELECT COUNT(*) AS n FROM visits", conn).iloc[0]["n"]
    assert visit_rows == len(data["visits"])

    sql_results = run_sql_file()
    assert len(sql_results) == 15
    assert all(not frame.empty for name, frame in sql_results.items() if name != "15_exception_identification")
    assert not sql_results["15_exception_identification"].empty
    print("Smoke test passed.")


if __name__ == "__main__":
    main()
