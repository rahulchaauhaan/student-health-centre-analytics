# NIT Calicut Health Centre Performance & Patient Access Analytics
## Comprehensive Project Story, Architecture & Interview Explanation Guide

---

## 1. Executive Summary & Project Origin Story

### The Problem
At major residential educational institutions like the **National Institute of Technology Calicut (NIT Calicut)**, the campus Health Centre serves a community of nearly **7,000 residents** (students, faculty, and campus staff). Traditionally, institutional health clinics rely on manual paper registration booklets and physical health cards. This creates major operational bottlenecks:
1. **Slow Historical Retrieval:** Looking up past medical visits, allergy records, or follow-up history takes minutes of manual searching through physical archives.
2. **Zero Capacity Visibility:** Clinic administrators lack real-time visibility into peak workload seasons, leading to doctor shortages during exam periods or monsoon viral outbreaks.
3. **Unmonitored Wait-Time Disparities:** Certain hostels or cohorts (e.g., first-year students or sports participants) face scheduling delays that go unnoticed without structured data.

### The Solution
This project simulates an **end-to-end Healthcare Operations & Data Analytics Platform**. It demonstrates how relational data modeling, automated data-quality validation, SQL querying, and an interactive web portal can transform clinic operations without clinical complexity.

### Strict Privacy & Academic Scope Notice
- **100% Synthetic Data:** Zero real patient records or Personally Identifiable Information (PII) are used.
- **Pure Operations & Analytics:** The project focuses on service utilization, triage wait times, and capacity planning. It explicitly does **not** perform medical diagnosis, prescription writing, or clinical decision-making.

---

## 2. Institutional Demographics & Campus Model (NIT Calicut)

The simulation models the entire active population of the NIT Calicut campus:

- **Total Campus Population:** **6,950 individuals**
  - **Students (6,500):** Across undergraduate (B.Tech, B.Sc) and postgraduate programs (M.Tech, MBA, M.Sc).
  - **Faculty (250):** Academic teaching staff across departments residing in campus quarters.
  - **General Staff (200):** Administrative, maintenance, library, security, and clinic support staff.
- **12 Campus Hostels Modeled:** `PG1`, `PG2`, `Hostel A`, `Hostel B`, `Hostel C`, `Hostel D`, `Hostel E`, `Hostel F`, `Hostel G`, `MBH 1`, `MBH`, `MLH`.
- **Student Sub-Cohorts:** `Hostel Resident`, `First Year`, `Final Year`, `Sports Participant`.
- **10 Core Health Centre Services:**
  1. *General Consultation* (High volume, primary care)
  2. *Respiratory Care* (Seasonal surges during monsoon/winter)
  3. *Gastrointestinal* (Food & waterborne health)
  4. *Musculoskeletal* (Sports & physical strain)
  5. *Dermatology / Skin Care*
  6. *Injury & Minor Trauma* (Emergency first aid, sports injuries)
  7. *Preventive Care & Health Checkups*
  8. *Follow-up Consultations*
  9. *Referral Coordination* (Escalation to tertiary city hospitals)
  10. *Other Support Services*

---

## 3. The 6-Layer Technical Architecture

```
Layer 1: Synthetic Data Generation (Statistical & Seasonal Probability Engine)
        ↓
Layer 2: Intentional Data-Quality Corruption (Realistic Dirty Data Injection)
        ↓
Layer 3: Cleaning & Validation Engine (9 Automated Business Rules & Audit Log)
        ↓
Layer 4: SQLite Database Layer (Relational Schema & Foreign Key Constraints)
        ↓
Layer 5: SQL Analytical Engine (19 Named Queries & KPI Extraction)
        ↓
Layer 6: Interactive Web Portal & Reporting (Streamlit UI + Automated Markdown Reports)
```

### Layer 1: Synthetic Data Generation (`data_generation.py`)
- Simulates 24 months of longitudinal clinic encounters (**January 2024 through December 2025**).
- Embeds realistic academic and seasonal epidemiological distributions:
  - **Exam Stress Waves (March, April, October, November):** General consultation and follow-up demand rises by +40%.
  - **Monsoon & Winter Waves (January, February, August, September, December):** Respiratory and viral cases rise by +25%.
  - **Preventive Surge (July):** Beginning of the academic year health screenings.
  - **Monday/Tuesday Surges:** Early-week clinic demand surges by +10%.

### Layer 2: Intentional Data Corruption (`data_generation.py`)
To mimic real-world hospital data entry errors, the generator injects dirty data:
- Duplicate visit records
- Missing student/patient IDs (`NaN`)
- Impossible negative waiting times (`-15 min`)
- Extreme consultation durations (`0 min` or `240 min`)
- Out-of-range satisfaction ratings (`0` or `7` on a 1–5 scale)
- Corrupted date formats (`2027-15-99`)
- Logical contradictions (e.g., referral flag set to `True` but outcome marked as `Resolved`)

### Layer 3: Cleaning & Validation Engine (`cleaning_validation.py`)
Applies **9 explicit business validation rules** to produce clean production datasets and generates audit reports (`reports/data_quality_cleaned.csv` and `reports/cleaning_issue_log.csv`):
1. `wait_time_minutes >= 0`
2. `consultation_duration` between 1 and 120 minutes
3. Valid foreign key reference to a synthetic student/staff ID
4. Valid service category name (alias normalization)
5. Detection and deduplication of repeated `visit_id`s
6. Logical consistency: If referral flag is `True`, outcome must be `Referred`
7. Satisfaction score bounded within `1.0` to `5.0`
8. Visit date within valid range (`2024-01-01` to `2025-12-31`)
9. Logical consistency: If outcome is `Follow-up Advised`, follow-up flag must be `True`

### Layer 4: SQLite Database Layer (`database.py`, `schema.sql`)
Loads validated data into a normalized relational database (`health_centre.db`):
- `students`: Demographic dimensions (ID, Department, Program, Year, Hostel, Cohort, Population Group).
- `staff`: Clinic staff roles, service areas, shift assignments, and monthly capacity targets.
- `services`: Service categories, monthly capacity limits, and target wait times.
- `visits`: Cleaned encounter records (dates, categories, priority, wait times, durations, outcomes, scores).
- `access`: Student segment access status (`Available`, `Delayed`, `Restricted`) and barriers.
- `capacity_utilization`: Monthly aggregated volume vs. service capacity with exception flags.

### Layer 5: SQL Analysis & KPI Layer (`analysis_queries.sql`, `kpis.py`)
Executes **19 named analytical SQL queries** covering:
- Monthly volume & waiting-time trajectories
- Service demand shares & capacity bottlenecks
- Department-level & 12-hostel geographic utilization
- Cross-demographic comparisons (Students vs. Faculty vs. Staff)
- Referral rates, follow-up rates, and patient satisfaction trends
- SLA exceptions (capacity utilization >100% or wait times >150% of target)

### Layer 6: Enterprise Streamlit Web Portal (`dashboard/app.py`)
An interactive web application featuring:
- **Corporate UI Design:** Styled with a professional healthcare color palette (Royal Cobalt `#0050C8`, Electric Cyan `#00A3E0`, Deep Navy `#001F5C`, clean slate surfaces).
- **Interactive Top Navbar & Deep-Navy Sidebar:** Real-time page switching synchronized with session state.
- **Global Filters:** Dynamically filter metrics by Population Group (Student, Faculty, Staff) and Time Period (Year-Month).
- **5 Dedicated Analytic Views:**
  1. *Executive Overview:* Macro KPIs, longitudinal visit & wait trends, population shares, hostel rankings.
  2. *Population & Demographics:* Cross-cohort scorecards, symptom prevalence matrices, and student sub-segment analysis.
  3. *Access & Capacity Utilization:* High-workload flags (>100%), barrier pareto charts, and utilization-wait scatter models.
  4. *Service Execution & Operations:* Triage priority workloads, consultation durations, outcome distributions, and the *Action Required Priority Matrix*.
  5. *Patient Health History & Reports:* Instant single-patient historical lookup (`STUxxxx`, `FACxxxx`, `STFxxxx`) and downloadable executive markdown reports.

---

## 4. Key Performance Indicators (KPIs) & Findings

| KPI | Formula | Value | Strategic Interpretation |
|---|---|---|---|
| **Total Encounters** | Cleaned clinic visits | **51,512** | Average of ~2,146 visits per month across 24 months. |
| **Unique Individuals** | Distinct IDs served | **6,947** | Reached 99.9% of the modeled campus community. |
| **Repeat Visit Rate** | Individuals with >1 visit / total | **99.51%** | Reflects ongoing primary and follow-up care. |
| **Average Wait Time** | Mean triage waiting time | **28.88 min** | Meets the institutional target SLA of <30 minutes. |
| **Median Wait Time** | 50th percentile wait time | **27.0 min** | Demonstrates stable non-skewed waiting distribution. |
| **Avg Consultation Duration** | Mean consultation length | **13.92 min** | Standard primary outpatient duration. |
| **Capacity Utilization** | Total visits / Monthly capacity | **88.87%** | Near the 90% optimal threshold without chronic overload. |
| **Referral Rate** | Visits requiring specialist referral / total | **7.20%** | Standard for primary care clinics escalating to city hospitals. |
| **Follow-up Rate** | Visits requiring follow-up / total | **19.64%** | ~1 in 5 encounters requires planned review. |
| **Average Satisfaction** | Mean patient rating (1–5) | **4.41 / 5** | High satisfaction inversely correlated with wait times. |
| **Capacity Exceptions** | Service-months exceeding 100% capacity | **76 events** | Peak winter and exam surges requiring temporary resource shift. |

---

## 5. Summary of Key Analytical Insights

1. **Peak Workload Seasonality:**
   - **March 2025** recorded the highest single-month volume (2,487 visits) driven by mid-semester examinations.
   - **Respiratory Care** reached peak monthly stress in **August 2025** at **195.8% capacity utilization** due to monsoon seasonal illnesses.
2. **Core Workload Driver:**
   - **General Consultation** represents the largest single workload share (15,710 visits, ~30.5% of all encounters).
3. **Operational Coupling (Wait Time vs. Capacity):**
   - Pearson correlation between capacity pressure and patient waiting times is **+0.62**, confirming that service bottlenecks directly degrade patient waiting times.
4. **Demographic Equity:**
   - First-year students experienced higher scheduling delays in initial months before acclimatizing to clinic scheduling procedures.

---

## 6. How to Explain This Project in Interviews / Portfolio Reviews

### 30-Second Elevator Pitch:
> *"I built an end-to-end healthcare operations analytics platform simulating patient access and clinic performance for the NIT Calicut campus serving nearly 7,000 residents. I engineered a synthetic data pipeline with statistical seasonality, designed an automated 9-rule data validation engine, loaded normalized tables into SQLite, authored 19 SQL analytical queries, and deployed a live interactive Streamlit web dashboard with demographic filtering and single-patient historical retrieval."*

### Key Technical Talking Points:
1. **Data Engineering:** Statistical generation with seasonal weighting + intentional dirty data injection + automated data-quality audits.
2. **Data Modeling & SQL:** 3NF relational schema in SQLite with primary/foreign keys and 19 analytical queries utilizing window functions, CTEs, and aggregation.
3. **Product & UI/UX:** Clean corporate styling with real-time session state management, responsive charts, and global dimensional filters.
4. **Cloud Deployment:** Zero-config auto-initialization pipeline deployed on **Streamlit Community Cloud** with public 24/7 availability.

---

### Permanent Live Links:
- **Live Interactive Dashboard:** `https://nitc-health-analytics.streamlit.app`
- **GitHub Repository:** `https://github.com/rahulchaauhaan/student-health-centre-analytics`
