from __future__ import annotations

import os

os.environ.setdefault("MPLCONFIGDIR", str(__import__("pathlib").Path(__file__).resolve().parents[2] / ".matplotlib-cache"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from . import config
from .database import run_sql_file
from .kpis import action_required_table, add_student_fields, calculated_insights, calculate_kpis, monthly_kpis


def _markdown_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    frame = df.head(max_rows).copy() if max_rows else df.copy()
    frame = frame.fillna("")
    headers = list(frame.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in headers) + " |")
    return "\n".join(lines)


def load_processed_data() -> dict[str, pd.DataFrame]:
    return {
        "students": pd.read_csv(config.DATA_PROCESSED / "students.csv"),
        "staff": pd.read_csv(config.DATA_PROCESSED / "staff.csv"),
        "services": pd.read_csv(config.DATA_PROCESSED / "services.csv"),
        "visits": pd.read_csv(config.DATA_PROCESSED / "visits_clean.csv"),
        "access": pd.read_csv(config.DATA_PROCESSED / "access.csv", keep_default_na=False),
        "capacity": pd.read_csv(config.DATA_PROCESSED / "capacity_utilization.csv"),
    }


def _save_bar(df: pd.DataFrame, x: str, y: str, title: str, path: str, color: str = "#2f6f73") -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df[x].astype(str), df[y], color=color)
    ax.set_title(title)
    ax.set_xlabel("")
    ax.set_ylabel(y.replace("_", " ").title())
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    fig.savefig(config.CHARTS_DIR / path, dpi=140)
    plt.close(fig)


def _save_line(df: pd.DataFrame, x: str, y: str, title: str, path: str, color: str = "#3949ab") -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df[x], df[y], marker="o", color=color, linewidth=2)
    ax.set_title(title)
    ax.set_xlabel("")
    ax.set_ylabel(y.replace("_", " ").title())
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(config.CHARTS_DIR / path, dpi=140)
    plt.close(fig)


def generate_charts(data: dict[str, pd.DataFrame]) -> list[str]:
    visits = data["visits"]
    students = data["students"]
    enriched = add_student_fields(visits, students)
    monthly = visits.groupby("year_month").size().reset_index(name="visits")
    service = visits["service_category"].value_counts().reset_index()
    service.columns = ["service_category", "visits"]
    dept = enriched["department"].value_counts().reset_index()
    dept.columns = ["department", "visits"]
    wait = visits.groupby("year_month")["wait_time_minutes"].mean().reset_index(name="avg_wait_time")
    capacity = data["capacity"].groupby("service_category")["capacity_utilization_pct"].mean().reset_index()

    charts = [
        ("monthly_visit_trend.png", monthly, "year_month", "visits", "Monthly Visit Trend", "line"),
        ("visits_by_service.png", service.head(10), "service_category", "visits", "Visits by Service", "bar"),
        ("visits_by_department.png", dept, "department", "visits", "Visits by Department", "bar"),
        ("waiting_time_trend.png", wait, "year_month", "avg_wait_time", "Average Waiting-Time Trend", "line"),
        (
            "capacity_by_service.png",
            capacity.sort_values("capacity_utilization_pct", ascending=False),
            "service_category",
            "capacity_utilization_pct",
            "Average Capacity Utilization by Service",
            "bar",
        ),
    ]
    saved = []
    for filename, frame, x, y, title, kind in charts:
        if kind == "line":
            _save_line(frame, x, y, title, filename)
        else:
            _save_bar(frame, x, y, title, filename)
        saved.append(filename)
    return saved


def generate_monthly_report(period: str | None = None) -> str:
    data = load_processed_data()
    visits = data["visits"]
    period = period or visits["year_month"].max()
    period_visits = visits.loc[visits["year_month"].eq(period)].copy()
    period_capacity = data["capacity"].loc[data["capacity"]["year_month"].eq(period)].copy()
    kpi = calculate_kpis(data["visits"], data["students"], data["services"], data["access"], data["capacity"])
    insights = calculated_insights(data["visits"], data["students"], data["services"], data["access"], data["capacity"])
    actions = action_required_table(data["capacity"], data["services"]).head(12)
    charts = generate_charts(data)

    service_summary = (
        period_visits.groupby("service_category")
        .agg(visits=("visit_id", "count"), avg_wait=("wait_time_minutes", "mean"), referral_rate=("referral_required", "mean"))
        .reset_index()
        .sort_values("visits", ascending=False)
    )
    service_summary["avg_wait"] = service_summary["avg_wait"].round(1)
    service_summary["referral_rate"] = (service_summary["referral_rate"] * 100).round(1)
    period_capacity = period_capacity.sort_values("capacity_utilization_pct", ascending=False)

    report = f"""# Monthly Management Report: {period}

Synthetic Academic Dataset - Not Real Medical Records

## Executive Summary

- Total cleaned visits in full 24-month dataset: {kpi['Total Visits']:,}
- Unique synthetic students served: {kpi['Unique Students Served']:,}
- Average wait time: {kpi['Average Wait Time']} minutes
- Average capacity utilization: {kpi['Capacity Utilization']}%
- Referral rate: {kpi['Referral Rate']}%
- Average satisfaction: {kpi['Average Satisfaction']} / 5

## Current Month Snapshot

- Visits in {period}: {len(period_visits):,}
- Unique students in {period}: {period_visits['student_id'].nunique():,}
- Average wait time in {period}: {period_visits['wait_time_minutes'].mean():.1f} minutes
- Services above 100% capacity in {period}: {int(period_capacity['capacity_utilization_pct'].gt(100).sum())}

## Calculated Insights

- {insights['busiest_month']}
- {insights['top_service']}
- {insights['capacity_pressure']}
- {insights['segment_delay']}
- {insights['utilization_wait_correlation']}

## Service Summary

{_markdown_table(service_summary)}

## Highest Capacity Pressure

{_markdown_table(period_capacity, max_rows=10)}

## Action Required

{_markdown_table(actions)}

## Charts Generated

{chr(10).join(f'- assets/charts/{name}' for name in charts)}

## Responsible Use Note

This report is an academic analytics demonstration using only synthetic data. It supports operational review,
not diagnosis, treatment, or clinical decision-making.
"""
    output_path = config.REPORTS_DIR / f"monthly_management_report_{period}.md"
    output_path.write_text(report)
    (config.REPORTS_DIR / "monthly_management_report_latest.md").write_text(report)
    service_summary.to_csv(config.REPORTS_DIR / f"service_summary_{period}.csv", index=False)
    actions.to_csv(config.REPORTS_DIR / "action_required.csv", index=False)
    monthly_kpis(data["visits"], data["capacity"]).to_csv(config.REPORTS_DIR / "monthly_kpis.csv", index=False)
    return str(output_path)


def generate_business_questions_doc() -> str:
    data = load_processed_data()
    sql_results = run_sql_file()
    kpi = calculate_kpis(data["visits"], data["students"], data["services"], data["access"], data["capacity"])
    insights = calculated_insights(data["visits"], data["students"], data["services"], data["access"], data["capacity"])
    top_wait = sql_results["03_average_waiting_time"].iloc[0]
    top_dept = sql_results["04_department_level_utilization"].iloc[0]
    top_hostel = sql_results["05_hostel_level_utilization"].iloc[0]
    top_referral = sql_results["07_referral_rate"].iloc[0]
    exception_frame = sql_results["15_exception_identification"]
    top_gap = exception_frame.iloc[0] if not exception_frame.empty else None

    doc = f"""# Business Questions

All findings use synthetic college health-centre data generated for this academic course project.

| # | Business question | KPI | SQL/Python method | Result | Interpretation | Recommendation |
|---|---|---|---|---|---|---|
| 1 | What are the busiest health-centre periods? | Monthly visit volume | SQL GROUP BY year_month and Python trend chart | {insights['busiest_month']} | Demand rises during exam and respiratory-pressure periods in the synthetic pattern. | Pre-plan staffing and registration support for peak months. |
| 2 | Which services have the highest demand? | Service visit count | SQL JOIN visits to services and rank by count | {insights['top_service']} | General access is the main workload driver. | Protect core consultation capacity before adding new services. |
| 3 | Which services experience capacity pressure? | Capacity utilization | SQL CTE ranks service-month utilization | {insights['capacity_pressure']} | Some service-month combinations exceed planned monthly capacity. | Use temporary capacity, better appointment spacing, or triage during pressure months. |
| 4 | Which departments/hostels generate the most visits? | Department and hostel utilization | SQL LEFT JOIN students to visits | {top_dept['department']} had {int(top_dept['total_visits']):,} visits; {top_hostel['hostel']} had {int(top_hostel['total_visits']):,}. | Utilization differs by academic and residence groups. | Share targeted preventive communication with high-use groups. |
| 5 | Which services have the longest waiting times? | Average wait time | SQL GROUP BY service_category with HAVING threshold | {top_wait['service_category']} averaged {top_wait['avg_wait_time']} minutes. | Higher complexity and pressure raise waits. | Monitor queue design and staff allocation for these services. |
| 6 | What proportion of visits require referral? | Referral rate | SQL CASE WHEN referral_required = 1 | Overall referral rate was {kpi['Referral Rate']}%; highest was {top_referral['service_category']} at {top_referral['referral_rate_pct']}%. | Referrals are concentrated in specific service categories. | Review referral coordination workload separately from basic visit counts. |
| 7 | Which student segments experience greater access delays? | Delayed/restricted access rate | SQL grouped access-status matrix | {insights['segment_delay']} | Access pressure is not evenly distributed across segments. | Use student-segment reporting to spot scheduling and access barriers. |
| 8 | Is higher utilization associated with longer waiting time? | Utilization-wait correlation | Python correlation between service-month utilization and average wait | {insights['utilization_wait_correlation']} | The synthetic data shows measurable coupling between capacity use and wait time. | Treat wait time as an early signal of capacity pressure. |
| 9 | Where are the largest operational execution gaps? | Exception count and gap | SQL exception query with CASE WHEN | {"Top exception: " + str(top_gap['service_category']) + " in " + str(top_gap['year_month']) + " at " + str(top_gap['capacity_utilization_pct']) + "% utilization." if top_gap is not None else "No capacity exceptions were produced in this run."} | Execution gaps appear where demand exceeds practical service capacity. | Prioritize peak-month service-area staffing and follow-up coordination. |
| 10 | What operational improvements should management consider? | Combined KPI layer | Python KPI layer, SQL exceptions, dashboard views | {kpi['Exception Count']} capacity exceptions flagged across the dataset. | Recurring reporting can convert manual record review into measurable operations management. | Automate monthly KPI review, monitor exceptions, and validate data quality before decision-making. |

## Stakeholder Scenario

The health centre wants a better understanding of historical utilization, workload, waiting times and access barriers so that it can improve recurring reporting and allocate operational capacity more effectively.

Business question -> requirements -> structured dataset -> data validation -> SQL -> Python -> dashboard -> insight -> recommendation.
"""
    path = config.PROJECT_ROOT / "docs" / "business_questions.md"
    path.write_text(doc)
    return str(path)


def export_sql_outputs() -> None:
    results = run_sql_file()
    for name, frame in results.items():
        frame.to_csv(config.REPORTS_DIR / f"{name}.csv", index=False)


def generate_readme() -> str:
    data = load_processed_data()
    kpi = calculate_kpis(data["visits"], data["students"], data["services"], data["access"], data["capacity"])
    insights = calculated_insights(data["visits"], data["students"], data["services"], data["access"], data["capacity"])
    readme = f"""# Student Health Centre Access & Service Performance Analytics

**An Academic Analytics Project Using Synthetic College Health-Centre Data**

All data used in this project is synthetic and created for academic purposes. No real student health records are used.

## Project Overview

This GitHub-ready B.Tech course project simulates a digital analytics solution for a fictional college health centre serving approximately 6,000-7,000 students. It demonstrates how structured data, SQL, Python, dashboards, data-quality validation, and automated reporting can improve historical retrieval and operational analytics.

The project does not build a diagnosis system, prescription tool, clinical decision engine, authentication system, or real medical-record application.

## Why This Project Was Created

The scenario is inspired by a common operational problem: manual health cards and historical records can make it slow to retrieve past visit activity and analyze service workload. This project models that problem with synthetic data and shows a responsible analytics workflow.

## Architecture

1. Synthetic data generation creates students, visits, services, staff, and access records.
2. Data-quality issues are intentionally inserted into visit data.
3. Cleaning and validation applies explicit business rules.
4. Cleaned data is loaded into SQLite.
5. SQL and Python calculate KPIs, trends, exceptions, and recurring reports.
6. Streamlit presents four dashboard pages, including a synthetic student history explorer.

## Data Model

- `students`: synthetic student profile attributes such as department, program, year, hostel, and segment.
- `visits`: high-level health-centre service interactions, wait times, outcomes, follow-ups, referrals, and satisfaction.
- `staff`: fictional staff/service-area capacity context.
- `services`: service category, capacity, and wait-time targets.
- `access`: service-category access status and barriers by synthetic student segment.
- `capacity_utilization`: service-month utilization and capacity exception flags.

## Dataset Size

- Synthetic students: {len(data['students']):,}
- Dirty synthetic visit rows: {len(pd.read_csv(config.DATA_RAW / 'visits_dirty.csv')):,}
- Cleaned synthetic visits: {len(data['visits']):,}
- Time period: 24 months from 2024-01 through 2025-12

## KPI Layer

| KPI | Formula |
|---|---|
| Total Visits | Count of cleaned visit records |
| Unique Students Served | Distinct `student_id` in visits |
| Repeat Visit Rate | Students with more than one visit / unique students served |
| Average Wait Time | Mean `wait_time_minutes` |
| Median Wait Time | Median `wait_time_minutes` |
| Average Consultation Duration | Mean `consultation_duration` |
| Service Utilization | Total visits / total service monthly capacity / number of months |
| Capacity Utilization | Service-month visits / service monthly capacity |
| Referral Rate | Visits requiring referral / total visits |
| Follow-up Rate | Visits requiring follow-up / total visits |
| Average Satisfaction | Mean satisfaction score |
| Access Restriction Rate | Restricted access combinations / all access combinations |
| Delayed Access Rate | Delayed access combinations / all access combinations |
| Monthly Growth | Latest month visits vs previous month visits |
| Exception Count | Service-month capacity utilization above 100% |

## Main KPIs

- Total Visits: {kpi['Total Visits']:,}
- Unique Students Served: {kpi['Unique Students Served']:,}
- Repeat Visit Rate: {kpi['Repeat Visit Rate']}%
- Average Wait Time: {kpi['Average Wait Time']} minutes
- Capacity Utilization: {kpi['Capacity Utilization']}%
- Referral Rate: {kpi['Referral Rate']}%
- Follow-up Rate: {kpi['Follow-up Rate']}%
- Average Satisfaction: {kpi['Average Satisfaction']} / 5
- Exception Count: {kpi['Exception Count']}

## Findings

- {insights['busiest_month']}
- {insights['top_service']}
- {insights['capacity_pressure']}
- {insights['segment_delay']}
- {insights['utilization_wait_correlation']}
- {insights['top_hostel']}

## Dashboard

Run:

```bash
streamlit run dashboard/app.py
```

Pages:

- Health Centre Overview
- Access & Utilization
- Service Execution & Operations
- Student Health History

The student history page accepts synthetic IDs such as `STU0421` and demonstrates fast historical retrieval from structured records. It is clearly labelled as a synthetic academic dataset and not a real clinical record system.

## How To Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python python/run_pipeline.py
python python/smoke_test.py
streamlit run dashboard/app.py
```

If your environment already has the required packages, run `python python/run_pipeline.py` directly.

## SQL

The SQLite schema is in `database/schema.sql`. Analysis queries are in `sql/analysis_queries.sql` and demonstrate `SELECT`, `WHERE`, `GROUP BY`, `HAVING`, joins, left joins, `CASE WHEN`, CTEs, and window functions.

## Data Quality

The raw data intentionally contains duplicate visit IDs, missing IDs, inconsistent service category labels, invalid dates, negative waits, impossible durations, invalid satisfaction scores, invalid service categories, and inconsistent outcome/referral flags.

Reports:

- `reports/data_quality_raw.csv`
- `reports/data_quality_cleaned.csv`
- `reports/cleaning_issue_log.csv`

## Automated Reporting

`python/generate_monthly_report.py` creates KPI summaries, exception tables, charts, and a management report in `reports/monthly_management_report_latest.md`.

## AI Considerations

Responsible AI could help summarize KPI movement, draft stakeholder summaries, identify unusual trends, and suggest follow-up analytics questions. This repository does not include an integrated AI feature. Any future AI-generated analytical summary would need validation against the underlying data and must not diagnose students, make treatment recommendations, or make medical decisions.

## Limitations

- The dataset is synthetic and does not represent actual student health behaviour.
- Health categories are intentionally high level and non-diagnostic.
- The dashboard is an academic analytics prototype, not a production medical system.
- Capacity assumptions are simplified for course-project clarity.

## Future Work

- Add role-based governance design for a real-world privacy review.
- Add scheduling simulation for what-if capacity planning.
- Add automated anomaly detection with clear human validation.
- Add unit tests for each business rule and KPI formula.
"""
    path = config.PROJECT_ROOT / "README.md"
    path.write_text(readme)
    return str(path)
