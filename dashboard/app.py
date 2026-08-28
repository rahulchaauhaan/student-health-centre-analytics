from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from healthcentre_analytics import config
from healthcentre_analytics.kpis import (
    action_required_table,
    add_student_fields,
    calculated_insights,
    calculate_kpis,
    monthly_kpis,
)

st.set_page_config(
    page_title="NIT Calicut Health Centre — Operations Intelligence Portal",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# PAGE DEFINITIONS (Professional, No Emojis)
# -------------------------------------------------------------
PAGES = [
    ("Executive Overview", "OPERATIONS"),
    ("Population & Demographics", "POPULATION"),
    ("Access & Capacity Utilization", "CAPACITY"),
    ("Service Execution & Operations", "SERVICES"),
    ("Patient Health History", "RECORDS & REPORTS"),
]
PAGE_NAMES = [p[0] for p in PAGES]

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Executive Overview"

def navigate_to(page_name: str) -> None:
    st.session_state["current_page"] = page_name


# -------------------------------------------------------------
# ENTERPRISE HEALTHCARE DESIGN SYSTEM & CSS
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }

    /* ---------------- TOP NAVBAR STYLING ---------------- */
    .portal-nav-wrapper {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 0.75rem 1.2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }
    .portal-logo {
        font-size: 1.65rem;
        font-weight: 900;
        letter-spacing: -0.5px;
        color: #0050C8 !important;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        line-height: 2.5rem;
    }
    .portal-logo span {
        color: #00A3E0 !important;
    }

    /* Top Nav Action Buttons */
    div[data-testid="column"] button {
        border-radius: 6px !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
        padding: 0.5rem 0.8rem !important;
        transition: all 0.2s ease !important;
        height: 2.5rem !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
        color: #0050C8 !important;
    }
    div[data-testid="column"] button:hover {
        background: linear-gradient(135deg, #0050C8 0%, #00A3E0 100%) !important;
        color: #FFFFFF !important;
        border-color: #00A3E0 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 14px rgba(0, 80, 200, 0.25) !important;
    }
    div[data-testid="column"] button[kind="primary"] {
        background: linear-gradient(135deg, #0050C8 0%, #003087 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #0050C8 !important;
        box-shadow: 0 4px 12px rgba(0, 80, 200, 0.3) !important;
    }

    /* ---------------- PROFESSIONAL ENTERPRISE SIDEBAR ---------------- */
    [data-testid="stSidebar"] {
        background: #001A4E !important;
        border-right: 1px solid #002B66 !important;
        padding-top: 1.2rem !important;
    }
    
    .sidebar-brand-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 163, 224, 0.3);
        border-radius: 8px;
        padding: 1.1rem;
        margin-bottom: 1.5rem;
    }
    .sidebar-brand-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #FFFFFF !important;
        letter-spacing: -0.3px;
    }
    .sidebar-brand-title span {
        color: #00A3E0 !important;
    }
    .sidebar-brand-sub {
        font-size: 0.76rem;
        color: #94A3B8 !important;
        margin-top: 0.2rem;
        letter-spacing: 0.2px;
    }
    .sidebar-brand-badge {
        display: inline-block;
        background: rgba(0, 163, 224, 0.2);
        color: #80D4FA !important;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        margin-top: 0.6rem;
        border: 1px solid rgba(0, 163, 224, 0.4);
    }
    
    .sidebar-section-header {
        font-size: 0.74rem;
        font-weight: 800;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #80D4FA !important;
        margin: 1.2rem 0 0.6rem 0;
    }

    /* Guaranteed 100% High-Contrast Sidebar Button Styling */
    [data-testid="stSidebar"] div.stButton button {
        width: 100% !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 6px !important;
        padding: 0.65rem 0.9rem !important;
        margin-bottom: 0.4rem !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.2px !important;
        text-transform: none !important;
        height: auto !important;
        transition: all 0.2s ease !important;
    }
    /* Inactive sidebar buttons */
    [data-testid="stSidebar"] div.stButton button[kind="secondary"] {
        background-color: rgba(255, 255, 255, 0.07) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #E2E8F0 !important;
    }
    [data-testid="stSidebar"] div.stButton button[kind="secondary"]:hover {
        background-color: rgba(0, 163, 224, 0.25) !important;
        border-color: #00A3E0 !important;
        color: #FFFFFF !important;
        transform: translateX(3px) !important;
    }
    /* Active sidebar button */
    [data-testid="stSidebar"] div.stButton button[kind="primary"] {
        background: linear-gradient(135deg, #0050C8 0%, #00A3E0 100%) !important;
        border: 1px solid #80D4FA !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(0, 80, 200, 0.4) !important;
    }

    /* Sidebar Dropdown Selectbox: 100% Guaranteed High Contrast Visibility */
    [data-testid="stSidebar"] .stSelectbox label p,
    [data-testid="stSidebar"] .stSelectbox label {
        color: #80D4FA !important;
        font-weight: 700 !important;
        font-size: 0.76rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.6px !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #002B66 !important;
        border: 1px solid rgba(0, 163, 224, 0.5) !important;
        border-radius: 6px !important;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] div,
    [data-testid="stSidebar"] div[data-baseweb="select"] span,
    [data-testid="stSidebar"] div[data-baseweb="select"] p {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] svg {
        fill: #00A3E0 !important;
        color: #00A3E0 !important;
    }
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[data-baseweb="menu"] * {
        background-color: #001F5C !important;
        color: #FFFFFF !important;
    }
    div[data-baseweb="popover"] li:hover {
        background-color: #0050C8 !important;
    }

    /* ---------------- HERO BANNER ---------------- */
    .portal-hero {
        background: linear-gradient(135deg, #0050C8 0%, #003087 55%, #001F5C 100%);
        border-radius: 12px;
        padding: 2.2rem 2.5rem;
        color: #FFFFFF !important;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 25px -5px rgba(0, 80, 200, 0.25);
    }
    .hero-tag {
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #80D4FA !important;
        margin-bottom: 0.8rem;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.2;
        letter-spacing: -0.5px;
        margin-bottom: 0.8rem;
        color: #FFFFFF !important;
        max-width: 850px;
    }
    .hero-sub {
        font-size: 1.05rem;
        color: #E2F1FF !important;
        margin-bottom: 1.2rem;
        max-width: 750px;
        line-height: 1.5;
    }
    .hero-disclaimer {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(8px);
        border-left: 4px solid #00A3E0;
        padding: 0.65rem 1rem;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #FFFFFF !important;
        max-width: 900px;
    }

    /* ---------------- KPI CARD ---------------- */
    .portal-kpi-card {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0;
        border-top: 4px solid #0050C8 !important;
        border-radius: 10px;
        padding: 1.2rem 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s, box-shadow 0.2s, border-top-color 0.2s;
    }
    .portal-kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 22px rgba(0, 80, 200, 0.12);
        border-top-color: #00A3E0 !important;
    }
    .kpi-label {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        color: #64748B !important;
        margin-bottom: 0.4rem;
    }
    .kpi-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: #002B66 !important;
        line-height: 1.1;
    }
    .kpi-sub {
        font-size: 0.82rem;
        color: #00A3E0 !important;
        font-weight: 700;
        margin-top: 0.3rem;
    }

    /* ---------------- SECTION HEADINGS ---------------- */
    .portal-section-heading {
        font-size: 1.35rem;
        font-weight: 800;
        color: #002B66 !important;
        margin-top: 1.8rem;
        margin-bottom: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        border-left: 5px solid #00A3E0;
        padding-left: 0.8rem;
    }
    .stMarkdown h3 {
        color: #002B66 !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        margin-top: 0.5rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=60)
def load_data() -> dict[str, pd.DataFrame]:
    required = [
        config.DATA_PROCESSED / "students.csv",
        config.DATA_PROCESSED / "visits_clean.csv",
        config.DATA_PROCESSED / "services.csv",
        config.DATA_PROCESSED / "access.csv",
        config.DATA_PROCESSED / "capacity_utilization.csv",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        with st.spinner("Initializing synthetic healthcare datasets for cloud deployment..."):
            from healthcentre_analytics.data_generation import generate_all, save_generated_data
            from healthcentre_analytics.cleaning_validation import save_cleaned_data
            from healthcentre_analytics.database import create_database, run_sql_file
            from healthcentre_analytics.reporting import export_sql_outputs, generate_monthly_report
            
            generated = generate_all()
            save_generated_data(generated)
            save_cleaned_data()
            create_database()
            run_sql_file()
            export_sql_outputs()
            generate_monthly_report()

    return {
        "students": pd.read_csv(config.DATA_PROCESSED / "students.csv"),
        "visits": pd.read_csv(config.DATA_PROCESSED / "visits_clean.csv"),
        "services": pd.read_csv(config.DATA_PROCESSED / "services.csv"),
        "access": pd.read_csv(config.DATA_PROCESSED / "access.csv", keep_default_na=False),
        "capacity": pd.read_csv(config.DATA_PROCESSED / "capacity_utilization.csv"),
    }


def render_top_navbar(current_page: str) -> None:
    col_logo, b1, b2, b3, b4, b5 = st.columns([2.4, 1.2, 1.2, 1.2, 1.2, 1.6])
    with col_logo:
        st.markdown(
            '<div class="portal-logo">NIT CALICUT <span>HEALTH</span></div>',
            unsafe_allow_html=True,
        )
    with b1:
        if st.button("OPERATIONS", type="primary" if current_page == "Executive Overview" else "secondary", use_container_width=True, key="top_btn_overview"):
            navigate_to("Executive Overview")
            st.rerun()
    with b2:
        if st.button("POPULATION", type="primary" if current_page == "Population & Demographics" else "secondary", use_container_width=True, key="top_btn_population"):
            navigate_to("Population & Demographics")
            st.rerun()
    with b3:
        if st.button("CAPACITY", type="primary" if current_page == "Access & Capacity Utilization" else "secondary", use_container_width=True, key="top_btn_capacity"):
            navigate_to("Access & Capacity Utilization")
            st.rerun()
    with b4:
        if st.button("SERVICES", type="primary" if current_page == "Service Execution & Operations" else "secondary", use_container_width=True, key="top_btn_services"):
            navigate_to("Service Execution & Operations")
            st.rerun()
    with b5:
        if st.button("RECORDS & REPORTS", type="primary" if current_page == "Patient Health History" else "secondary", use_container_width=True, key="top_btn_reports"):
            navigate_to("Patient Health History")
            st.rerun()


def render_hero_banner(tag: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="portal-hero">
            <div class="hero-tag">{tag}</div>
            <div class="hero-title">{title}</div>
            <div class="hero-sub">{subtitle}</div>
            <div class="hero-disclaimer">
                <b>Academic Dataset Notice:</b> 100% synthetic dataset created for academic and demonstration purposes. Contains zero real patient records or protected health data.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_metric_row(items: list[tuple[str, str, str]]) -> None:
    cols = st.columns(len(items))
    for col, (label, val, sub) in zip(cols, items):
        col.markdown(
            f"""
            <div class="portal-kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{val}</div>
                <div class="kpi-sub">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# -------------------------------------------------------------
# 1. EXECUTIVE OVERVIEW (OPERATIONS)
# -------------------------------------------------------------
def overview_page(data: dict[str, pd.DataFrame], filtered_visits: pd.DataFrame, enriched: pd.DataFrame) -> None:
    render_hero_banner(
        tag="CAMPUS HEALTHCARE ANALYTICS | EXECUTIVE OVERVIEW",
        title="Institutional Health Centre Operations & Population Access",
        subtitle="Real-time operational visibility across 6,950 campus community members, service utilization metrics, and capacity pressure points.",
    )

    capacity = data["capacity"]
    kpi = calculate_kpis(filtered_visits, data["students"], data["services"], data["access"], capacity)

    kpi_metric_row(
        [
            ("Total Encounters", f"{kpi['Total Visits']:,}", "24-Month Volume"),
            ("Campus Population", f"{kpi['Unique Students Served']:,}", "Active Individuals"),
            ("Avg Wait Time", f"{kpi['Average Wait Time']} min", "Target: <30 min"),
            ("Capacity Utilization", f"{kpi['Capacity Utilization']}%", "Threshold: 90%"),
            ("Referral Rate", f"{kpi['Referral Rate']}%", "Out-of-Centre Care"),
            ("Patient Satisfaction", f"{kpi['Average Satisfaction']} / 5", "High Benchmark"),
        ]
    )

    st.markdown('<div class="portal-section-heading">Longitudinal Volume & Operational Wait-Time Trends</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    monthly = filtered_visits.groupby("year_month").size().reset_index(name="visits")
    wait = filtered_visits.groupby("year_month")["wait_time_minutes"].mean().reset_index(name="avg_wait_time")
    c1.subheader("Monthly Visit Volume")
    c1.line_chart(monthly, x="year_month", y="visits", color="#0050C8")
    c2.subheader("Average Waiting Time (Minutes)")
    c2.line_chart(wait, x="year_month", y="avg_wait_time", color="#00A3E0")

    st.markdown('<div class="portal-section-heading">Demographics & Service Utilization Demand</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    # Population group breakdown
    pop_col = "population_group" if "population_group" in enriched.columns else "student_segment"
    pop_counts = enriched[pop_col].value_counts().reset_index()
    pop_counts.columns = [pop_col, "visits"]
    c3.subheader("Visits by Population Group")
    c3.bar_chart(pop_counts, x=pop_col, y="visits", color="#0050C8")

    # Service categories
    service = filtered_visits["service_category"].value_counts().reset_index()
    service.columns = ["service_category", "visits"]
    c4.subheader("Top Clinical Service Demand")
    c4.bar_chart(service.head(8), x="service_category", y="visits", color="#00A3E0")

    st.markdown('<div class="portal-section-heading">NIT Calicut 12-Hostel Geographic Distribution</div>', unsafe_allow_html=True)
    student_mask = enriched["population_group"].eq("Student") if "population_group" in enriched.columns else pd.Series(True, index=enriched.index)
    student_visits = enriched.loc[student_mask]
    hostel_data = (
        student_visits.groupby("hostel")
        .agg(visits=("visit_id", "count"), avg_wait=("wait_time_minutes", "mean"))
        .reset_index()
        .sort_values("visits", ascending=False)
    )
    hostel_data["avg_wait"] = hostel_data["avg_wait"].round(1)
    st.bar_chart(hostel_data, x="hostel", y="visits", color="#003087")


# -------------------------------------------------------------
# 2. POPULATION & DEMOGRAPHICS (POPULATION)
# -------------------------------------------------------------
def population_demographics_page(data: dict[str, pd.DataFrame], enriched: pd.DataFrame) -> None:
    render_hero_banner(
        tag="POPULATION HEALTH | CROSS-DEMOGRAPHIC COMPARISON",
        title="Comparative Health Utilization: Students, Faculty & Staff",
        subtitle="Analytic evaluation of access patterns, triage disparities, symptom burdens, and satisfaction metrics across community segments.",
    )

    pop_col = "population_group" if "population_group" in enriched.columns else "student_segment"

    summary = (
        enriched.groupby(pop_col)
        .agg(
            total_visits=("visit_id", "count"),
            unique_people=("student_id", "nunique"),
            avg_wait_time=("wait_time_minutes", "mean"),
            avg_duration=("consultation_duration", "mean"),
            avg_satisfaction=("satisfaction_score", "mean"),
            referrals=("referral_required", "sum"),
            follow_ups=("follow_up_required", "sum"),
        )
        .reset_index()
    )
    summary["avg_wait_time"] = summary["avg_wait_time"].round(1)
    summary["avg_duration"] = summary["avg_duration"].round(1)
    summary["avg_satisfaction"] = summary["avg_satisfaction"].round(2)
    summary["referral_rate_pct"] = ((summary["referrals"] / summary["total_visits"]) * 100).round(1)
    summary["follow_up_rate_pct"] = ((summary["follow_ups"] / summary["total_visits"]) * 100).round(1)

    st.markdown('<div class="portal-section-heading">Population Benchmark Scorecard</div>', unsafe_allow_html=True)
    st.dataframe(summary, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.subheader("Average Wait Time (min)")
    c1.bar_chart(summary, x=pop_col, y="avg_wait_time", color="#0050C8")

    c2.subheader("Satisfaction Score (1-5)")
    c2.bar_chart(summary, x=pop_col, y="avg_satisfaction", color="#00A3E0")

    c3.subheader("Referral Rate (%)")
    c3.bar_chart(summary, x=pop_col, y="referral_rate_pct", color="#002B66")

    st.markdown('<div class="portal-section-heading">Clinical Symptom Prevalence Matrix by Population</div>', unsafe_allow_html=True)
    symp_pivot = enriched.groupby([pop_col, "symptom_category"]).size().unstack(fill_value=0)
    st.dataframe(symp_pivot, use_container_width=True)

    st.markdown('<div class="portal-section-heading">Student Sub-Cohort Analysis</div>', unsafe_allow_html=True)
    student_enriched = enriched.loc[enriched["population_group"].eq("Student")] if "population_group" in enriched.columns else enriched
    segment_summary = (
        student_enriched.groupby("student_segment")
        .agg(
            visits=("visit_id", "count"),
            unique_students=("student_id", "nunique"),
            avg_wait=("wait_time_minutes", "mean"),
            avg_satisfaction=("satisfaction_score", "mean"),
        )
        .reset_index()
    )
    segment_summary["avg_wait"] = segment_summary["avg_wait"].round(1)
    segment_summary["avg_satisfaction"] = segment_summary["avg_satisfaction"].round(2)
    st.dataframe(segment_summary, use_container_width=True)


# -------------------------------------------------------------
# 3. ACCESS & CAPACITY UTILIZATION (CAPACITY)
# -------------------------------------------------------------
def access_capacity_page(data: dict[str, pd.DataFrame], filtered_visits: pd.DataFrame) -> None:
    render_hero_banner(
        tag="OPERATIONS & CAPACITY | ACCESS BOTTLENECKS",
        title="Capacity Utilization, Service Stress & Access Barriers",
        subtitle="Tracking high-workload exceptions (>100% capacity), scheduling barriers, and waiting-time correlation models.",
    )

    access = data["access"]
    capacity = data["capacity"]
    insights = calculated_insights(filtered_visits, data["students"], data["services"], access, capacity)
    joined = capacity.merge(
        filtered_visits.groupby(["year_month", "service_category"])["wait_time_minutes"].mean().reset_index(),
        on=["year_month", "service_category"],
        how="left",
    )

    kpi_metric_row(
        [
            ("Delayed Access Rate", f"{(access['access_status'].eq('Delayed').mean() * 100):.1f}%", "Scheduling Queue"),
            ("Restricted Access Rate", f"{(access['access_status'].eq('Restricted').mean() * 100):.1f}%", "Capacity Bound"),
            ("Avg Expected Wait", f"{access['expected_wait_time'].mean():.1f} min", "Access Model"),
            ("Capacity Exceeded", f"{int(capacity['capacity_utilization_pct'].gt(100).sum())}", "Peak Service-Months"),
        ]
    )

    c1, c2 = st.columns(2)
    status = access["access_status"].value_counts().reset_index()
    status.columns = ["access_status", "count"]
    c1.subheader("Access Status Profile")
    c1.bar_chart(status, x="access_status", y="count", color="#0050C8")

    barriers = access.loc[access["access_barrier"].ne("None")].groupby(["service_category", "access_barrier"]).size().reset_index(name="count")
    c2.subheader("Identified Access Barriers by Service")
    c2.dataframe(barriers.sort_values("count", ascending=False), use_container_width=True)

    st.markdown('<div class="portal-section-heading">Average Capacity Utilization by Service (% of Capacity)</div>', unsafe_allow_html=True)
    util = capacity.groupby("service_category")["capacity_utilization_pct"].mean().sort_values(ascending=False).reset_index()
    st.bar_chart(util, x="service_category", y="capacity_utilization_pct", color="#00A3E0")

    st.markdown('<div class="portal-section-heading">Operational Coupling: Capacity Pressure vs Waiting Time</div>', unsafe_allow_html=True)
    st.scatter_chart(joined, x="capacity_utilization_pct", y="wait_time_minutes", color="service_category")


# -------------------------------------------------------------
# 4. SERVICE EXECUTION & OPERATIONS (SERVICES)
# -------------------------------------------------------------
def operations_page(data: dict[str, pd.DataFrame], filtered_visits: pd.DataFrame) -> None:
    render_hero_banner(
        tag="CLINICAL OPERATIONS | SLA & WORKLOAD MANAGEMENT",
        title="Service Execution, Consultation Efficiency & Action Matrix",
        subtitle="Monitoring triage prioritization, consultation lengths, clinical outcomes, and resource reallocation plans.",
    )

    services = data["services"]
    capacity = data["capacity"]
    monthly = monthly_kpis(filtered_visits, capacity)
    actions = action_required_table(capacity, services)

    kpi_metric_row(
        [
            ("Avg Wait Time", f"{filtered_visits['wait_time_minutes'].mean():.1f} min", "Mean Triage Wait"),
            ("Median Wait Time", f"{filtered_visits['wait_time_minutes'].median():.1f} min", "50th Percentile"),
            ("Avg Consultation", f"{filtered_visits['consultation_duration'].mean():.1f} min", "Standard Duration"),
            ("High-Pressure Events", f"{int(capacity['capacity_utilization_pct'].gt(100).sum())}", "Over 100% Load"),
        ]
    )

    c1, c2 = st.columns(2)
    if "priority" in filtered_visits.columns:
        prio = filtered_visits.groupby("priority").agg(visits=("visit_id", "count"), avg_wait=("wait_time_minutes", "mean")).reset_index()
        prio["avg_wait"] = prio["avg_wait"].round(1)
        c1.subheader("Triage Priority Workload")
        c1.bar_chart(prio, x="priority", y="visits", color="#0050C8")

    if "outcome" in filtered_visits.columns:
        out = filtered_visits["outcome"].value_counts().reset_index()
        out.columns = ["outcome", "visits"]
        c2.subheader("Clinical Outcomes Distribution")
        c2.bar_chart(out, x="outcome", y="visits", color="#00A3E0")

    st.markdown('<div class="portal-section-heading">Service Performance Standards: Target vs Actual</div>', unsafe_allow_html=True)
    target_actual = capacity.groupby("service_category").agg(
        actual_utilization=("capacity_utilization_pct", "mean"),
        target_wait_time=("target_wait_time", "mean"),
    ).reset_index()
    actual_wait = filtered_visits.groupby("service_category")["wait_time_minutes"].mean().reset_index(name="actual_wait_time")
    target_actual = target_actual.merge(actual_wait, on="service_category", how="left")
    st.dataframe(target_actual.round(1), use_container_width=True)

    st.markdown('<div class="portal-section-heading">Action Required Priority Matrix (Management Action Items)</div>', unsafe_allow_html=True)
    st.dataframe(actions, use_container_width=True)


# -------------------------------------------------------------
# 5. PATIENT HEALTH HISTORY & REPORTS (RECORDS & REPORTS)
# -------------------------------------------------------------
def patient_history_page(data: dict[str, pd.DataFrame]) -> None:
    render_hero_banner(
        tag="INDIVIDUAL HEALTH RECORDS | SYNTHETIC PROFILE EXPLORER",
        title="Single Patient Longitudinal History & Analytical Reports",
        subtitle="Simulates instant structured historical retrieval across students, faculty, and staff records, plus automated executive report downloads.",
    )

    students = data["students"]
    visits = data["visits"]

    tab_record, tab_reports = st.tabs(["Patient Record Lookup", "Management Reports Export"])

    with tab_record:
        c1, c2 = st.columns([1, 2])
        pop_options = ["All"] + sorted(students["population_group"].unique().tolist()) if "population_group" in students.columns else ["All"]
        pop_filter = c1.selectbox("Filter Population Group", pop_options)

        cand_students = students if pop_filter == "All" else students.loc[students["population_group"].eq(pop_filter)]
        id_list = cand_students["student_id"].tolist()

        default_index = 0
        if "STU0421" in id_list:
            default_index = id_list.index("STU0421")
        elif "FAC0001" in id_list:
            default_index = id_list.index("FAC0001")

        selected = c2.selectbox("Select Synthetic Patient ID", id_list, index=default_index)
        person = students.loc[students["student_id"].eq(selected)].iloc[0]
        history = visits.loc[visits["student_id"].eq(selected)].sort_values("visit_date", ascending=False)

        st.markdown('<div class="portal-section-heading">Patient Demographic Profile Card</div>', unsafe_allow_html=True)
        kpi_metric_row(
            [
                ("Patient ID", str(person["student_id"]), "Synthetic ID"),
                ("Population Group", str(person.get("population_group", "Student")), "Campus Role"),
                ("Department", str(person["department"]), "Academic Unit"),
                ("Program / Designation", str(person["program"]), "Cadre"),
                ("Hostel / Residence", str(person["hostel"]), "Campus Location"),
            ]
        )

        st.markdown('<div class="portal-section-heading">Longitudinal Visit Summary</div>', unsafe_allow_html=True)
        if history.empty:
            st.info("No recorded health visits found for this synthetic record.")
        else:
            kpi_metric_row(
                [
                    ("Total Encounters", f"{len(history):,}", "Recorded Visits"),
                    ("Last Health Visit", str(history["visit_date"].max()), "Recent Record"),
                    ("Avg Waiting Time", f"{history['wait_time_minutes'].mean():.1f} min", "Individual Avg"),
                    ("Follow-ups Advised", f"{int(history['follow_up_required'].sum())}", "Clinical Reviews"),
                    ("Referrals Issued", f"{int(history['referral_required'].sum())}", "Specialist Esc."),
                ]
            )

            c1_sub, c2_sub = st.columns(2)
            timeline = history.sort_values("visit_date").groupby("visit_date").size().reset_index(name="visits")
            c1_sub.subheader("Visit Frequency Timeline")
            c1_sub.line_chart(timeline, x="visit_date", y="visits", color="#0050C8")

            by_service = history["service_category"].value_counts().reset_index()
            by_service.columns = ["service_category", "visits"]
            c2_sub.subheader("Services Utilized")
            c2_sub.bar_chart(by_service, x="service_category", y="visits", color="#00A3E0")

            st.markdown('<div class="portal-section-heading">Complete Chronological Encounters Table</div>', unsafe_allow_html=True)
            st.dataframe(
                history[
                    [
                        "visit_date",
                        "service_category",
                        "visit_category",
                        "priority",
                        "wait_time_minutes",
                        "consultation_duration",
                        "outcome",
                        "follow_up_required",
                        "referral_required",
                        "satisfaction_score",
                    ]
                ],
                use_container_width=True,
            )

    with tab_reports:
        st.markdown('<div class="portal-section-heading">Executive Monthly Reports & SQL Data Outputs</div>', unsafe_allow_html=True)
        latest_report = config.REPORTS_DIR / "monthly_management_report_latest.md"
        if latest_report.exists():
            report_text = latest_report.read_text()
            st.download_button(
                "Download Latest Monthly Management Report (.md)",
                data=report_text,
                file_name="NIT_Calicut_Health_Monthly_Report.md",
                mime="text/markdown",
                type="primary",
            )
            with st.expander("Preview Monthly Management Report (Markdown)", expanded=True):
                st.markdown(report_text)
        else:
            st.info("Run `python python/generate_monthly_report.py` to generate the latest management report.")


# -------------------------------------------------------------
# MAIN APP ENTRY POINT
# -------------------------------------------------------------
def main() -> None:
    data = load_data()
    students = data["students"]
    visits = data["visits"]
    enriched_full = add_student_fields(visits, students)

    # ------------------ PROFESSIONAL SIDEBAR ------------------
    st.sidebar.markdown(
        """
        <div class="sidebar-brand-card">
            <div class="sidebar-brand-title">NIT CALICUT <span>HEALTH</span></div>
            <div class="sidebar-brand-sub">Healthcare Performance Analytics</div>
            <div class="sidebar-brand-badge">OPERATIONAL INTELLIGENCE SYSTEM</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown('<div class="sidebar-section-header">NAVIGATION PORTAL</div>', unsafe_allow_html=True)

    # Render professional sidebar buttons with 100% visible high contrast styling
    for page_name, code in PAGES:
        is_active = st.session_state["current_page"] == page_name
        if st.sidebar.button(
            page_name,
            key=f"side_btn_{code}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            navigate_to(page_name)
            st.rerun()

    active_page = st.session_state["current_page"]

    st.sidebar.markdown('<div class="sidebar-section-header">GLOBAL DATA FILTERS</div>', unsafe_allow_html=True)

    # Filter Population Group
    pop_options = ["All"] + sorted(students["population_group"].unique().tolist()) if "population_group" in students.columns else ["All"]
    selected_pop = st.sidebar.selectbox("Population Group", pop_options, key="global_pop_filter")

    # Filter Year/Month
    month_options = ["All"] + sorted(visits["year_month"].unique().tolist())
    selected_month = st.sidebar.selectbox("Period (Year-Month)", month_options, key="global_month_filter")

    # Apply Filters
    filtered_visits = visits.copy()
    filtered_enriched = enriched_full.copy()

    if selected_pop != "All" and "population_group" in filtered_enriched.columns:
        valid_ids = set(students.loc[students["population_group"].eq(selected_pop), "student_id"])
        filtered_visits = filtered_visits.loc[filtered_visits["student_id"].isin(valid_ids)]
        filtered_enriched = filtered_enriched.loc[filtered_enriched["population_group"].eq(selected_pop)]

    if selected_month != "All":
        filtered_visits = filtered_visits.loc[filtered_visits["year_month"].eq(selected_month)]
        filtered_enriched = filtered_enriched.loc[filtered_enriched["year_month"].eq(selected_month)]

    # Render interactive top navbar
    render_top_navbar(active_page)

    # Render active page view
    if active_page == "Executive Overview":
        overview_page(data, filtered_visits, filtered_enriched)
    elif active_page == "Population & Demographics":
        population_demographics_page(data, filtered_enriched)
    elif active_page == "Access & Capacity Utilization":
        access_capacity_page(data, filtered_visits)
    elif active_page == "Service Execution & Operations":
        operations_page(data, filtered_visits)
    else:
        patient_history_page(data)


if __name__ == "__main__":
    main()
