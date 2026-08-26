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


st.set_page_config(page_title="Student Health Centre Analytics", layout="wide")


@st.cache_data
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
        st.error("Processed data is missing. Run `python python/run_pipeline.py` from the project root.")
        st.stop()
    return {
        "students": pd.read_csv(config.DATA_PROCESSED / "students.csv"),
        "visits": pd.read_csv(config.DATA_PROCESSED / "visits_clean.csv"),
        "services": pd.read_csv(config.DATA_PROCESSED / "services.csv"),
        "access": pd.read_csv(config.DATA_PROCESSED / "access.csv", keep_default_na=False),
        "capacity": pd.read_csv(config.DATA_PROCESSED / "capacity_utilization.csv"),
    }


def metric_row(items: list[tuple[str, str]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)


def overview(data: dict[str, pd.DataFrame]) -> None:
    visits = data["visits"]
    enriched = add_student_fields(visits, data["students"])
    capacity = data["capacity"]
    kpi = calculate_kpis(visits, data["students"], data["services"], data["access"], capacity)

    metric_row(
        [
            ("Total Visits", f"{kpi['Total Visits']:,}"),
            ("Unique Students", f"{kpi['Unique Students Served']:,}"),
            ("Avg Wait Time", f"{kpi['Average Wait Time']} min"),
            ("Capacity Utilization", f"{kpi['Capacity Utilization']}%"),
            ("Referral Rate", f"{kpi['Referral Rate']}%"),
            ("Satisfaction", f"{kpi['Average Satisfaction']} / 5"),
        ]
    )

    left, right = st.columns(2)
    monthly = visits.groupby("year_month").size().reset_index(name="visits")
    wait = visits.groupby("year_month")["wait_time_minutes"].mean().reset_index(name="avg_wait_time")
    left.subheader("Monthly Visit Trend")
    left.line_chart(monthly, x="year_month", y="visits")
    right.subheader("Waiting-Time Trend")
    right.line_chart(wait, x="year_month", y="avg_wait_time")

    c1, c2, c3 = st.columns(3)
    service = visits["service_category"].value_counts().reset_index()
    service.columns = ["service_category", "visits"]
    c1.subheader("Visits by Service")
    c1.bar_chart(service, x="service_category", y="visits")
    department = enriched["department"].value_counts().reset_index()
    department.columns = ["department", "visits"]
    c2.subheader("Visits by Department")
    c2.bar_chart(department, x="department", y="visits")
    hostel = enriched["hostel"].value_counts().reset_index()
    hostel.columns = ["hostel", "visits"]
    c3.subheader("Visits by Hostel")
    c3.bar_chart(hostel, x="hostel", y="visits")

    st.subheader("Service Utilization")
    util = capacity.groupby("service_category")["capacity_utilization_pct"].mean().sort_values(ascending=False).reset_index()
    st.bar_chart(util, x="service_category", y="capacity_utilization_pct")


def access_utilization(data: dict[str, pd.DataFrame]) -> None:
    visits = data["visits"]
    access = data["access"]
    capacity = data["capacity"]
    insights = calculated_insights(visits, data["students"], data["services"], access, capacity)
    joined = capacity.merge(
        visits.groupby(["year_month", "service_category"])["wait_time_minutes"].mean().reset_index(),
        on=["year_month", "service_category"],
        how="left",
    )

    metric_row(
        [
            ("Delayed Access", f"{(access['access_status'].eq('Delayed').mean() * 100):.1f}%"),
            ("Restricted Access", f"{(access['access_status'].eq('Restricted').mean() * 100):.1f}%"),
            ("Avg Expected Wait", f"{access['expected_wait_time'].mean():.1f} min"),
            ("Capacity Exceptions", f"{int(capacity['capacity_utilization_pct'].gt(100).sum())}"),
        ]
    )

    c1, c2 = st.columns(2)
    status = access["access_status"].value_counts().reset_index()
    status.columns = ["access_status", "count"]
    c1.subheader("Access Status Distribution")
    c1.bar_chart(status, x="access_status", y="count")
    barriers = access.loc[access["access_barrier"].ne("None")].groupby(["service_category", "access_barrier"]).size().reset_index(name="count")
    c2.subheader("Access Barriers by Service")
    c2.dataframe(barriers.sort_values("count", ascending=False), use_container_width=True)

    c3, c4 = st.columns(2)
    util = capacity.groupby("service_category")["capacity_utilization_pct"].mean().sort_values(ascending=False).reset_index()
    c3.subheader("Utilization vs Capacity")
    c3.bar_chart(util, x="service_category", y="capacity_utilization_pct")
    segment = access.groupby(["student_segment", "access_status"]).size().reset_index(name="count")
    c4.subheader("Access Status by Student Segment")
    c4.dataframe(segment, use_container_width=True)

    st.subheader("Wait Time vs Utilization")
    st.scatter_chart(joined, x="capacity_utilization_pct", y="wait_time_minutes", color="service_category")

    st.subheader("Key Insights")
    for key in ["capacity_pressure", "segment_delay", "utilization_wait_correlation"]:
        st.write(f"- {insights[key]}")


def operations(data: dict[str, pd.DataFrame]) -> None:
    visits = data["visits"]
    services = data["services"]
    capacity = data["capacity"]
    monthly = monthly_kpis(visits, capacity)
    actions = action_required_table(capacity, services)

    metric_row(
        [
            ("Avg Wait Time", f"{visits['wait_time_minutes'].mean():.1f} min"),
            ("Median Wait Time", f"{visits['wait_time_minutes'].median():.1f} min"),
            ("Avg Consultation", f"{visits['consultation_duration'].mean():.1f} min"),
            ("Exceptions", f"{int(capacity['capacity_utilization_pct'].gt(100).sum())}"),
        ]
    )

    c1, c2 = st.columns(2)
    service_workload = visits["service_category"].value_counts().reset_index()
    service_workload.columns = ["service_category", "visits"]
    c1.subheader("Service Workload")
    c1.bar_chart(service_workload, x="service_category", y="visits")
    c2.subheader("Monthly Performance")
    c2.line_chart(monthly, x="year_month", y=["total_visits", "avg_wait_time"])

    st.subheader("Target vs Actual")
    target_actual = capacity.groupby("service_category").agg(
        actual_utilization=("capacity_utilization_pct", "mean"),
        target_wait_time=("target_wait_time", "mean"),
    ).reset_index()
    actual_wait = visits.groupby("service_category")["wait_time_minutes"].mean().reset_index(name="actual_wait_time")
    target_actual = target_actual.merge(actual_wait, on="service_category", how="left")
    st.dataframe(target_actual.round(1), use_container_width=True)

    st.subheader("Action Required")
    st.dataframe(actions, use_container_width=True)


def student_history(data: dict[str, pd.DataFrame]) -> None:
    st.info("Synthetic Academic Dataset - Not Real Medical Records")
    students = data["students"]
    visits = data["visits"]
    default_index = int(students.index[students["student_id"].eq("STU0421")][0]) if "STU0421" in set(students["student_id"]) else 0
    selected = st.selectbox("Synthetic Student ID", students["student_id"].tolist(), index=default_index)
    student = students.loc[students["student_id"].eq(selected)].iloc[0]
    history = visits.loc[visits["student_id"].eq(selected)].sort_values("visit_date", ascending=False)

    st.subheader("Student Overview")
    metric_row(
        [
            ("Department", student["department"]),
            ("Program", student["program"]),
            ("Year", str(student["year_of_study"])),
            ("Hostel", student["hostel"]),
        ]
    )

    st.subheader("Historical Summary")
    if history.empty:
        st.write("No visits found for this synthetic student.")
        return
    metric_row(
        [
            ("Total Visits", f"{len(history):,}"),
            ("Last Visit", str(history["visit_date"].max())),
            ("Avg Wait Time", f"{history['wait_time_minutes'].mean():.1f} min"),
            ("Follow-ups", f"{int(history['follow_up_required'].sum())}"),
            ("Referrals", f"{int(history['referral_required'].sum())}"),
        ]
    )

    c1, c2 = st.columns(2)
    timeline = history.sort_values("visit_date").groupby("visit_date").size().reset_index(name="visits")
    c1.subheader("Historical Timeline")
    c1.line_chart(timeline, x="visit_date", y="visits")
    by_service = history["service_category"].value_counts().reset_index()
    by_service.columns = ["service_category", "visits"]
    c2.subheader("Service Categories")
    c2.bar_chart(by_service, x="service_category", y="visits")

    st.subheader("Visit History")
    st.dataframe(
        history[
            [
                "visit_date",
                "service_category",
                "visit_category",
                "wait_time_minutes",
                "outcome",
                "follow_up_required",
                "referral_required",
            ]
        ],
        use_container_width=True,
    )


def main() -> None:
    st.title("Student Health Centre Analytics")
    st.caption("Synthetic Academic Dataset - Not Real Medical Records")
    data = load_data()
    page = st.sidebar.radio(
        "Pages",
        [
            "Health Centre Overview",
            "Access & Utilization",
            "Service Execution & Operations",
            "Student Health History",
        ],
    )
    if page == "Health Centre Overview":
        overview(data)
    elif page == "Access & Utilization":
        access_utilization(data)
    elif page == "Service Execution & Operations":
        operations(data)
    else:
        student_history(data)


if __name__ == "__main__":
    main()
