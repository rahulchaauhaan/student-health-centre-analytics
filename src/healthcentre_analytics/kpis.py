from __future__ import annotations

import numpy as np
import pandas as pd


def add_student_fields(visits: pd.DataFrame, students: pd.DataFrame) -> pd.DataFrame:
    cols = ["student_id", "department", "program", "year_of_study", "hostel", "student_segment"]
    return visits.merge(students[cols], on="student_id", how="left")


def calculate_kpis(
    visits: pd.DataFrame,
    students: pd.DataFrame,
    services: pd.DataFrame,
    access: pd.DataFrame,
    capacity: pd.DataFrame,
) -> dict[str, float]:
    unique_students = visits["student_id"].nunique()
    repeat_students = visits.groupby("student_id").size().gt(1).sum()
    access_status = access["access_status"].value_counts(normalize=True)
    latest_month = visits["year_month"].max()
    previous_month = sorted(visits["year_month"].unique())[-2]
    current_volume = len(visits.loc[visits["year_month"].eq(latest_month)])
    previous_volume = len(visits.loc[visits["year_month"].eq(previous_month)])
    monthly_growth = ((current_volume - previous_volume) / previous_volume * 100) if previous_volume else 0
    exception_count = int(capacity["capacity_utilization_pct"].gt(100).sum())

    return {
        "Total Visits": int(len(visits)),
        "Unique Students Served": int(unique_students),
        "Repeat Visit Rate": round(repeat_students / unique_students * 100, 2),
        "Average Wait Time": round(visits["wait_time_minutes"].mean(), 2),
        "Median Wait Time": round(visits["wait_time_minutes"].median(), 2),
        "Average Consultation Duration": round(visits["consultation_duration"].mean(), 2),
        "Service Utilization": round(len(visits) / services["monthly_capacity"].sum() / visits["year_month"].nunique() * 100, 2),
        "Capacity Utilization": round(capacity["capacity_utilization_pct"].mean(), 2),
        "Referral Rate": round(visits["referral_required"].mean() * 100, 2),
        "Follow-up Rate": round(visits["follow_up_required"].mean() * 100, 2),
        "Average Satisfaction": round(visits["satisfaction_score"].mean(), 2),
        "Access Restriction Rate": round(access_status.get("Restricted", 0) * 100, 2),
        "Delayed Access Rate": round(access_status.get("Delayed", 0) * 100, 2),
        "Monthly Growth": round(monthly_growth, 2),
        "Exception Count": exception_count,
    }


def monthly_kpis(visits: pd.DataFrame, capacity: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        visits.groupby("year_month")
        .agg(
            total_visits=("visit_id", "count"),
            unique_students=("student_id", "nunique"),
            avg_wait_time=("wait_time_minutes", "mean"),
            median_wait_time=("wait_time_minutes", "median"),
            referral_rate=("referral_required", "mean"),
            follow_up_rate=("follow_up_required", "mean"),
            avg_satisfaction=("satisfaction_score", "mean"),
        )
        .reset_index()
    )
    cap = capacity.groupby("year_month")["capacity_utilization_pct"].mean().reset_index(name="avg_capacity_utilization_pct")
    monthly = monthly.merge(cap, on="year_month", how="left")
    monthly["monthly_growth_pct"] = monthly["total_visits"].pct_change().replace([np.inf, -np.inf], 0).fillna(0) * 100
    rate_cols = ["referral_rate", "follow_up_rate"]
    monthly[rate_cols] = monthly[rate_cols] * 100
    return monthly.round(2)


def action_required_table(capacity: pd.DataFrame, services: pd.DataFrame) -> pd.DataFrame:
    high_pressure = capacity.loc[capacity["capacity_utilization_pct"].ge(95)].copy()
    if high_pressure.empty:
        high_pressure = capacity.nlargest(10, "capacity_utilization_pct").copy()
    table = high_pressure.merge(services[["service_category", "service_name"]], on="service_category", how="left")
    table["Service Area"] = table["service_name"]
    table["Metric"] = "Monthly capacity utilization"
    table["Actual"] = table["capacity_utilization_pct"].round(1).astype(str) + "%"
    table["Target"] = "90% or lower"
    table["Gap"] = (table["capacity_utilization_pct"] - 90).round(1).astype(str) + " pp"
    table["Priority"] = pd.cut(
        table["capacity_utilization_pct"],
        bins=[0, 100, 115, 999],
        labels=["Medium", "High", "Critical"],
        include_lowest=True,
    ).astype(str)
    table["Recommended Action"] = np.where(
        table["capacity_utilization_pct"].ge(115),
        "Add temporary capacity or extend service hours during peak months",
        "Review scheduling and redistribute staff coverage",
    )
    return table[
        ["year_month", "Service Area", "Metric", "Actual", "Target", "Gap", "Priority", "Recommended Action"]
    ].sort_values(["Priority", "year_month"], ascending=[True, False])


def calculated_insights(
    visits: pd.DataFrame,
    students: pd.DataFrame,
    services: pd.DataFrame,
    access: pd.DataFrame,
    capacity: pd.DataFrame,
) -> dict[str, str]:
    enriched = add_student_fields(visits, students)
    busiest_month = visits.groupby("year_month").size().idxmax()
    busiest_count = int(visits.groupby("year_month").size().max())
    top_service = visits["service_category"].value_counts().idxmax()
    top_service_count = int(visits["service_category"].value_counts().max())
    pressure = capacity.loc[capacity["capacity_utilization_pct"].idxmax()]
    segment_delay = (
        access.loc[access["access_status"].isin(["Delayed", "Restricted"])]
        .groupby("student_segment")
        .size()
        .sort_values(ascending=False)
    )
    segment = segment_delay.index[0] if not segment_delay.empty else "No segment"
    util_wait = (
        capacity.merge(
            visits.groupby(["year_month", "service_category"])["wait_time_minutes"].mean().reset_index(),
            on=["year_month", "service_category"],
            how="left",
        )[["capacity_utilization_pct", "wait_time_minutes"]]
        .corr()
        .iloc[0, 1]
    )
    top_hostel = enriched["hostel"].value_counts().idxmax()
    return {
        "busiest_month": f"{busiest_month} had the highest activity with {busiest_count:,} visits.",
        "top_service": f"{top_service} was the highest-demand service with {top_service_count:,} visits.",
        "capacity_pressure": (
            f"{pressure['service_category']} reached the highest monthly capacity pressure at "
            f"{pressure['capacity_utilization_pct']:.1f}% in {pressure['year_month']}."
        ),
        "segment_delay": f"{segment} had the most delayed or restricted access combinations in the synthetic access matrix.",
        "utilization_wait_correlation": f"Utilization and wait time correlation was {util_wait:.2f}, indicating measurable operational coupling.",
        "top_hostel": f"{top_hostel} generated the highest visit volume among hostel/day-scholar groups.",
    }
