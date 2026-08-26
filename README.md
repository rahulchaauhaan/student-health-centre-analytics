# Student Health Centre Access & Service Performance Analytics

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

- Synthetic students: 6,500
- Dirty synthetic visit rows: 52,080
- Cleaned synthetic visits: 51,515
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

- Total Visits: 51,515
- Unique Students Served: 6,497
- Repeat Visit Rate: 99.63%
- Average Wait Time: 28.84 minutes
- Capacity Utilization: 89.05%
- Referral Rate: 7.27%
- Follow-up Rate: 19.63%
- Average Satisfaction: 4.41 / 5
- Exception Count: 77

## Findings

- 2025-03 had the highest activity with 2,499 visits.
- General Consultation was the highest-demand service with 15,633 visits.
- Respiratory reached the highest monthly capacity pressure at 203.8% in 2025-01.
- First Year had the most delayed or restricted access combinations in the synthetic access matrix.
- Utilization and wait time correlation was 0.61, indicating measurable operational coupling.
- Day Scholar generated the highest visit volume among hostel/day-scholar groups.

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
