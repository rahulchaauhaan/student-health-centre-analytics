from __future__ import annotations

import pandas as pd

from . import config
from .utils import pct


def load_raw_data() -> dict[str, pd.DataFrame]:
    return {
        "students": pd.read_csv(config.DATA_RAW / "students.csv"),
        "staff": pd.read_csv(config.DATA_RAW / "staff.csv"),
        "services": pd.read_csv(config.DATA_RAW / "services.csv"),
        "visits": pd.read_csv(config.DATA_RAW / "visits_dirty.csv"),
        "access": pd.read_csv(config.DATA_RAW / "access.csv", keep_default_na=False),
    }


def _normalize_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().map({"true": True, "false": False, "1": True, "0": False}).fillna(False)


def evaluate_business_rules(
    visits: pd.DataFrame,
    students: pd.DataFrame,
    services: pd.DataFrame,
    access: pd.DataFrame | None = None,
) -> pd.DataFrame:
    valid_students = set(students["student_id"])
    valid_services = set(services["service_category"])
    parsed_dates = pd.to_datetime(visits["visit_date"], errors="coerce")
    referrals = _normalize_bool(visits["referral_required"])
    followups = _normalize_bool(visits["follow_up_required"])
    satisfaction = pd.to_numeric(visits["satisfaction_score"], errors="coerce")
    wait = pd.to_numeric(visits["wait_time_minutes"], errors="coerce")
    duration = pd.to_numeric(visits["consultation_duration"], errors="coerce")

    checks = [
        ("RULE 1", "wait_time_minutes >= 0", wait.ge(0)),
        ("RULE 2", "consultation_duration between 1 and 120 minutes", duration.between(1, 120)),
        ("RULE 3", "every visit references a valid synthetic student", visits["student_id"].isin(valid_students)),
        ("RULE 4", "every visit references a valid service category", visits["service_category"].isin(valid_services)),
        ("RULE 5", "duplicate visit IDs are detected", ~visits["visit_id"].duplicated(keep=False)),
        (
            "RULE 6",
            "referral_required is logically consistent with outcome",
            ~(referrals & visits["outcome"].ne("Referred")),
        ),
        ("RULE 7", "satisfaction score is between 1 and 5", satisfaction.between(1, 5)),
        ("RULE 8", "visit date is valid and within 2024-2025", parsed_dates.between(config.START_DATE, config.END_DATE)),
        ("RULE 9", "follow-up flag matches follow-up outcomes", ~(visits["outcome"].eq("Follow-up Advised") & ~followups)),
    ]

    rows = []
    total = len(visits)
    for rule_id, description, mask in checks:
        passed = int(mask.fillna(False).sum())
        failed = total - passed
        rows.append(
            {
                "rule_id": rule_id,
                "business_rule": description,
                "total_rows": total,
                "passed_rows": passed,
                "failed_rows": failed,
                "pass_rate_pct": pct(passed / total if total else 0),
            }
        )

    if access is not None:
        capacity = calculate_capacity_utilization(visits, services)
        failed = int(capacity["capacity_utilization_pct"].gt(100).sum())
        rows.append(
            {
                "rule_id": "RULE 10",
                "business_rule": "capacity utilization above 100% is flagged for review",
                "total_rows": len(capacity),
                "passed_rows": len(capacity) - failed,
                "failed_rows": failed,
                "pass_rate_pct": pct((len(capacity) - failed) / len(capacity) if len(capacity) else 0),
            }
        )
    return pd.DataFrame(rows)


def clean_visits(visits: pd.DataFrame, students: pd.DataFrame, services: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cleaned = visits.copy()
    original_count = len(cleaned)
    service_aliases = {**config.CATEGORY_ALIASES}
    cleaned["service_category"] = cleaned["service_category"].replace(service_aliases)
    cleaned["visit_date"] = pd.to_datetime(cleaned["visit_date"], errors="coerce")
    cleaned["wait_time_minutes"] = pd.to_numeric(cleaned["wait_time_minutes"], errors="coerce")
    cleaned["consultation_duration"] = pd.to_numeric(cleaned["consultation_duration"], errors="coerce")
    cleaned["satisfaction_score"] = pd.to_numeric(cleaned["satisfaction_score"], errors="coerce")
    cleaned["follow_up_required"] = _normalize_bool(cleaned["follow_up_required"])
    cleaned["referral_required"] = _normalize_bool(cleaned["referral_required"])

    issue_log = []

    def drop_invalid(mask: pd.Series, issue: str) -> None:
        nonlocal cleaned
        count = int(mask.sum())
        if count:
            issue_log.append({"issue": issue, "rows_affected": count, "action": "Rows removed from cleaned visits"})
            cleaned = cleaned.loc[~mask].copy()

    dup_mask = cleaned["visit_id"].duplicated(keep="first")
    if int(dup_mask.sum()):
        issue_log.append(
            {"issue": "Duplicate visit IDs", "rows_affected": int(dup_mask.sum()), "action": "Kept first occurrence"}
        )
        cleaned = cleaned.loc[~dup_mask].copy()

    valid_students = set(students["student_id"])
    valid_services = set(services["service_category"])
    drop_invalid(cleaned["student_id"].isna(), "Missing student ID")
    drop_invalid(~cleaned["student_id"].isin(valid_students), "Invalid synthetic student ID")
    drop_invalid(cleaned["visit_date"].isna(), "Invalid visit date")
    drop_invalid(~cleaned["visit_date"].between(config.START_DATE, config.END_DATE), "Out-of-range visit date")
    drop_invalid(~cleaned["service_category"].isin(valid_services), "Invalid service category")
    drop_invalid(cleaned["wait_time_minutes"].isna() | cleaned["wait_time_minutes"].lt(0), "Negative or missing wait time")
    drop_invalid(
        cleaned["consultation_duration"].isna() | ~cleaned["consultation_duration"].between(1, 120),
        "Impossible consultation duration",
    )
    drop_invalid(cleaned["satisfaction_score"].isna() | ~cleaned["satisfaction_score"].between(1, 5), "Invalid satisfaction")

    referral_inconsistent = cleaned["referral_required"] & cleaned["outcome"].ne("Referred")
    if int(referral_inconsistent.sum()):
        issue_log.append(
            {
                "issue": "Referral flag inconsistent with outcome",
                "rows_affected": int(referral_inconsistent.sum()),
                "action": "Outcome corrected to Referred",
            }
        )
        cleaned.loc[referral_inconsistent, "outcome"] = "Referred"

    followup_inconsistent = cleaned["outcome"].eq("Follow-up Advised") & ~cleaned["follow_up_required"]
    if int(followup_inconsistent.sum()):
        issue_log.append(
            {
                "issue": "Follow-up outcome inconsistent with flag",
                "rows_affected": int(followup_inconsistent.sum()),
                "action": "Follow-up flag corrected to True",
            }
        )
        cleaned.loc[followup_inconsistent, "follow_up_required"] = True

    cleaned["visit_date"] = cleaned["visit_date"].dt.date.astype(str)
    parsed_dates = pd.to_datetime(cleaned["visit_date"])
    cleaned["month"] = parsed_dates.dt.month_name()
    cleaned["month_num"] = parsed_dates.dt.month
    cleaned["year"] = parsed_dates.dt.year
    cleaned["year_month"] = parsed_dates.dt.to_period("M").astype(str)
    cleaned["wait_time_minutes"] = cleaned["wait_time_minutes"].round().astype(int)
    cleaned["consultation_duration"] = cleaned["consultation_duration"].round().astype(int)
    cleaned["satisfaction_score"] = cleaned["satisfaction_score"].round(1)

    issue_log.append(
        {
            "issue": "Cleaned dataset row count",
            "rows_affected": original_count - len(cleaned),
            "action": f"{len(cleaned)} rows retained from {original_count}",
        }
    )

    return cleaned.sort_values(["visit_date", "visit_id"]).reset_index(drop=True), pd.DataFrame(issue_log)


def calculate_capacity_utilization(visits: pd.DataFrame, services: pd.DataFrame) -> pd.DataFrame:
    if "year_month" not in visits.columns:
        visits = visits.copy()
        parsed_dates = pd.to_datetime(visits["visit_date"], errors="coerce")
        visits = visits.loc[parsed_dates.notna()].copy()
        visits["year_month"] = parsed_dates.loc[parsed_dates.notna()].dt.to_period("M").astype(str)
    monthly = visits.groupby(["year_month", "service_category"]).size().reset_index(name="visit_count")
    monthly = monthly.merge(services[["service_category", "monthly_capacity", "target_wait_time"]], on="service_category", how="left")
    monthly["capacity_utilization_pct"] = (monthly["visit_count"] / monthly["monthly_capacity"] * 100).round(2)
    monthly["capacity_flag"] = monthly["capacity_utilization_pct"].gt(100)
    return monthly


def save_cleaned_data() -> dict[str, pd.DataFrame]:
    raw = load_raw_data()
    raw_rules = evaluate_business_rules(raw["visits"], raw["students"], raw["services"], raw["access"])
    cleaned_visits, issue_log = clean_visits(raw["visits"], raw["students"], raw["services"])
    cleaned_rules = evaluate_business_rules(cleaned_visits, raw["students"], raw["services"], raw["access"])
    capacity = calculate_capacity_utilization(cleaned_visits, raw["services"])

    for name in ["students", "staff", "services", "access"]:
        raw[name].to_csv(config.DATA_PROCESSED / f"{name}.csv", index=False)
    cleaned_visits.to_csv(config.DATA_PROCESSED / "visits_clean.csv", index=False)
    capacity.to_csv(config.DATA_PROCESSED / "capacity_utilization.csv", index=False)
    raw_rules.to_csv(config.REPORTS_DIR / "data_quality_raw.csv", index=False)
    cleaned_rules.to_csv(config.REPORTS_DIR / "data_quality_cleaned.csv", index=False)
    issue_log.to_csv(config.REPORTS_DIR / "cleaning_issue_log.csv", index=False)

    return {
        "students": raw["students"],
        "staff": raw["staff"],
        "services": raw["services"],
        "access": raw["access"],
        "visits": cleaned_visits,
        "capacity": capacity,
        "raw_rules": raw_rules,
        "cleaned_rules": cleaned_rules,
        "issue_log": issue_log,
    }


if __name__ == "__main__":
    result = save_cleaned_data()
    print(f"Cleaned visits: {len(result['visits']):,}")
    print(f"Data-quality reports written to {config.REPORTS_DIR}")
