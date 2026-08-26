from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from healthcentre_analytics.data_generation import generate_all, save_generated_data
from healthcentre_analytics.cleaning_validation import save_cleaned_data
from healthcentre_analytics.database import create_database, run_sql_file
from healthcentre_analytics.reporting import (
    export_sql_outputs,
    generate_business_questions_doc,
    generate_monthly_report,
    generate_readme,
)


def main() -> None:
    generated = generate_all()
    save_generated_data(generated)
    cleaned = save_cleaned_data()
    create_database()
    sql_results = run_sql_file()
    export_sql_outputs()
    report_path = generate_monthly_report()
    bq_path = generate_business_questions_doc()
    readme_path = generate_readme()

    print("Pipeline completed successfully.")
    print(f"Synthetic students: {len(cleaned['students']):,}")
    print(f"Dirty visit rows: {len(generated.visits_dirty):,}")
    print(f"Cleaned visits: {len(cleaned['visits']):,}")
    print(f"SQL analyses executed: {len(sql_results)}")
    print(f"Monthly report: {report_path}")
    print(f"Business questions: {bq_path}")
    print(f"README: {readme_path}")


if __name__ == "__main__":
    main()
