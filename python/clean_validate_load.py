from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from healthcentre_analytics.cleaning_validation import save_cleaned_data
from healthcentre_analytics.database import create_database, run_sql_file
from healthcentre_analytics.reporting import export_sql_outputs


def main() -> None:
    result = save_cleaned_data()
    create_database()
    sql_results = run_sql_file()
    export_sql_outputs()
    print(f"Cleaned visits: {len(result['visits']):,}")
    print(f"SQLite database loaded with {len(sql_results)} named SQL analyses exported to reports/.")


if __name__ == "__main__":
    main()
