# NIT Calicut Health Centre Performance & Operational Access Analytics

**An Academic Analytics Project Using Synthetic College Health-Centre Data**

All data used in this project is 100% synthetic and created for academic demonstration purposes. No real student health records or personal identifiable information are used.

## Project Overview

This GitHub-ready B.Tech academic analytics project simulates an operational health-centre analytics solution tailored for the **National Institute of Technology Calicut (NIT Calicut)** campus, serving approximately 6,500 students, 250 faculty, and 200 general staff members. It demonstrates how structured relational schemas, SQL, Python, interactive dashboards, data-quality validation, and automated reporting can transform operational visibility and service access.

The project is an analytics and reporting demonstration, not a diagnosis tool, prescription system, electronic medical records (EMR) software, or authentication platform.

## Why This Project Was Created

The scenario is inspired by a common institutional health centre problem: manual health cards and historical record registers make it slow to retrieve past visit activity, track wait times, and analyze operational capacity. This project addresses these challenges using a complete synthetic end-to-end data pipeline.

## Architecture

1. **Synthetic Data Generation**: Creates students, faculty, staff, services, staffing capacity, and access matrices across 12 NIT Calicut hostels.
2. **Intentional Data Quality Injection**: Injects realistic dirty data (duplicate visit IDs, negative wait times, out-of-range dates, missing IDs).
3. **Cleaning & Validation**: Applies 9 automated business validation rules to produce clean datasets and audit issue logs.
4. **SQLite Database Layer**: Automatically loads clean relational tables into SQLite.
5. **SQL & Analytical KPIs**: 19 named SQL queries calculate trends, hostel distributions, population cross-comparisons, and capacity exceptions.
6. **Streamlit Analytics Dashboard**: 5 rich interactive pages featuring dynamic filtering, KPI scorecards, and single-patient lookup.

## Data Model & Population Groups

- **Population Groups**:
  - `Student` (6,500 students across 12 NIT Calicut hostels: PG1, PG2, Hostel A, Hostel B, Hostel C, Hostel D, Hostel E, Hostel F, Hostel G, MBH 1, MBH, MLH)
  - `Faculty` (250 teaching faculty across campus departments)
  - `General Staff` (200 administrative and campus maintenance staff)
- `visits`: High-level service interactions, wait times, durations, outcomes, follow-ups, referrals, and satisfaction scores.
- `staff`: Staff roles and shift capacities.
- `services`: 10 core service categories, target wait times, and monthly capacities.
- `access`: Service accessibility status and barriers by student segment.
- `capacity_utilization`: Monthly capacity utilization percentages and exception flags.

## Dataset Summary

- Total Synthetic Population: 6,950 individuals (6,500 students + 250 faculty + 200 staff)
- Dirty Synthetic Visits: 52,080 rows
- Cleaned Synthetic Visits: 51,512 rows
- Time Period: 24 months (January 2024 – December 2025)

## KPI Layer

| KPI | Formula |
|---|---|
| Total Visits | Count of cleaned visit records |
| Unique Individuals Served | Distinct `student_id` in visits |
| Repeat Visit Rate | Individuals with >1 visit / unique individuals served |
| Average Wait Time | Mean `wait_time_minutes` |
| Median Wait Time | Median `wait_time_minutes` |
| Average Consultation Duration | Mean `consultation_duration` |
| Capacity Utilization | Monthly service visits / service monthly capacity |
| Referral Rate | Visits requiring referral / total visits |
| Follow-up Rate | Visits requiring follow-up / total visits |
| Average Satisfaction | Mean satisfaction score (1–5) |
| Exception Count | Service-months exceeding 100% capacity |

## Interactive Streamlit Dashboard

Run locally:

```bash
streamlit run dashboard/app.py
```

### Dashboard Pages:
1. **Health Centre Overview**: Institutional KPIs, monthly volume trends, waiting time trajectories, population breakdown, and 12-hostel distribution.
2. **Population & Demographics**: Comparative analysis of Students vs Faculty vs General Staff across wait times, satisfaction, and symptom profiles.
3. **Access & Utilization**: Access barrier breakdowns, capacity utilization vs threshold (>100%), and wait time correlation scatter plots.
4. **Service Execution & Operations**: Operational workload, target vs actual consultation metrics, and automated Action Required tables.
5. **Patient Health History**: Fast individual synthetic profile lookup (`STUxxxx`, `FACxxxx`, `STFxxxx`) with chronological health event timelines.

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
