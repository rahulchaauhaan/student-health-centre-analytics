from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import config
from .utils import ensure_directories


@dataclass(frozen=True)
class GeneratedData:
    students: pd.DataFrame
    staff: pd.DataFrame
    services: pd.DataFrame
    visits_dirty: pd.DataFrame
    access: pd.DataFrame


def _choice(rng: np.random.Generator, values: list[str], probabilities: list[float], size: int) -> np.ndarray:
    return rng.choice(values, p=np.array(probabilities) / np.sum(probabilities), size=size)


def generate_students(rng: np.random.Generator, n_students: int = config.STUDENT_COUNT) -> pd.DataFrame:
    student_ids = [f"STU{i:04d}" for i in range(1, n_students + 1)]
    departments = _choice(rng, config.DEPARTMENTS, [0.20, 0.16, 0.14, 0.10, 0.12, 0.08, 0.10, 0.10], n_students)
    program_map = {
        "Business Administration": ["MBA", "B.Tech"],
        "Applied Sciences": ["B.Sc", "M.Sc", "B.Tech"],
        "Biotechnology": ["B.Tech", "M.Tech", "B.Sc"],
    }
    programs = []
    for dept in departments:
        options = program_map.get(dept, ["B.Tech", "M.Tech"])
        programs.append(rng.choice(options, p=np.ones(len(options)) / len(options)))

    hostels = _choice(rng, config.HOSTELS, [0.16, 0.15, 0.14, 0.13, 0.12, 0.30], n_students)
    years = rng.choice([1, 2, 3, 4], p=[0.29, 0.25, 0.24, 0.22], size=n_students)
    sports_flag = rng.random(n_students) < 0.12
    segments = []
    for hostel, year, sports in zip(hostels, years, sports_flag):
        if sports:
            segments.append("Sports Participant")
        elif year == 1:
            segments.append("First Year")
        elif year == 4:
            segments.append("Final Year")
        elif hostel == "Day Scholar":
            segments.append("Day Scholar")
        else:
            segments.append("Hostel Resident")

    return pd.DataFrame(
        {
            "student_id": student_ids,
            "department": departments,
            "program": programs,
            "year_of_study": years,
            "hostel": hostels,
            "student_segment": segments,
        }
    )


def generate_staff() -> pd.DataFrame:
    return pd.DataFrame(
        config.STAFF_ROWS,
        columns=["staff_id", "staff_role", "service_area", "assigned_shift", "monthly_target"],
    )


def generate_services() -> pd.DataFrame:
    return pd.DataFrame(
        config.SERVICES_ROWS,
        columns=["service_id", "service_name", "service_category", "monthly_capacity", "target_wait_time"],
    )


def _month_weight(date: pd.Timestamp) -> float:
    exam_months = {3, 4, 10, 11}
    respiratory_months = {1, 2, 8, 9, 12}
    preventive_months = {7}
    weight = 1.0
    if date.month in exam_months:
        weight += 0.40
    if date.month in respiratory_months:
        weight += 0.25
    if date.month in preventive_months:
        weight += 0.18
    if date.weekday() in (0, 1):
        weight += 0.10
    return weight


def _sample_visit_dates(rng: np.random.Generator, visit_count: int) -> pd.Series:
    dates = pd.date_range(config.START_DATE, config.END_DATE, freq="D")
    weights = np.array([_month_weight(d) for d in dates], dtype=float)
    weights = weights / weights.sum()
    return pd.Series(rng.choice(dates, p=weights, size=visit_count)).sort_values(ignore_index=True)


def _student_visit_probabilities(students: pd.DataFrame) -> np.ndarray:
    weights = np.ones(len(students))
    weights += students["hostel"].ne("Day Scholar").astype(float).to_numpy() * 0.22
    weights += students["student_segment"].eq("First Year").astype(float).to_numpy() * 0.18
    weights += students["student_segment"].eq("Sports Participant").astype(float).to_numpy() * 0.30
    weights += students["department"].isin(["Computer Science", "Mechanical", "Electronics"]).astype(float).to_numpy() * 0.10
    return weights / weights.sum()


def _service_probabilities_for_date(date: pd.Timestamp) -> list[float]:
    base = np.array([0.32, 0.13, 0.09, 0.08, 0.07, 0.10, 0.08, 0.07, 0.03, 0.03])
    if date.month in {1, 2, 8, 9, 12}:
        base[1] += 0.10
        base[0] -= 0.05
        base[6] -= 0.02
    if date.month in {3, 4, 10, 11}:
        base[0] += 0.06
        base[7] += 0.03
        base[6] -= 0.03
    if date.month == 7:
        base[6] += 0.10
        base[0] -= 0.05
    base = np.clip(base, 0.01, None)
    return (base / base.sum()).tolist()


def generate_visits(
    rng: np.random.Generator,
    students: pd.DataFrame,
    services: pd.DataFrame,
    visit_count: int = config.VISIT_COUNT,
) -> pd.DataFrame:
    service_capacity = services.set_index("service_category")["monthly_capacity"].to_dict()
    target_wait = services.set_index("service_category")["target_wait_time"].to_dict()
    dates = _sample_visit_dates(rng, visit_count)
    student_ids = rng.choice(students["student_id"], p=_student_visit_probabilities(students), size=visit_count)
    student_lookup = students.set_index("student_id")

    rows = []
    categories = config.SERVICE_CATEGORIES
    priority_map = {"Low": 0.18, "Routine": 0.68, "Urgent": 0.14}

    temp = pd.DataFrame({"visit_date": dates})
    month_counts = temp.assign(month=temp["visit_date"].dt.to_period("M").astype(str)).groupby("month").size().to_dict()
    service_month_counter: dict[tuple[str, str], int] = {}

    for i, (visit_date, student_id) in enumerate(zip(dates, student_ids), start=1):
        category = rng.choice(categories, p=_service_probabilities_for_date(visit_date))
        month_key = visit_date.to_period("M").strftime("%Y-%m")
        key = (month_key, category)
        service_month_counter[key] = service_month_counter.get(key, 0) + 1

        student = student_lookup.loc[student_id]
        segment = student["student_segment"]
        hostel = student["hostel"]
        month_pressure = month_counts[month_key] / (visit_count / 24)
        utilization_pressure = service_month_counter[key] / max(service_capacity[category], 1)
        base_wait = target_wait[category] * rng.normal(0.92, 0.18)
        wait = base_wait + 14 * max(month_pressure - 1, 0) + 26 * max(utilization_pressure - 0.85, 0)
        if segment in {"First Year", "Hostel Resident"}:
            wait += rng.normal(4, 2)
        if hostel in {"Hostel D", "Hostel E"}:
            wait += rng.normal(5, 2)
        priority = rng.choice(list(priority_map), p=list(priority_map.values()))
        if priority == "Urgent":
            wait *= 0.65
        elif priority == "Low":
            wait *= 1.12
        wait = int(max(0, round(wait + rng.normal(0, 8))))

        duration_mean = {
            "General Consultation": 13,
            "Respiratory": 14,
            "Gastrointestinal": 15,
            "Musculoskeletal": 18,
            "Skin": 12,
            "Injury": 20,
            "Preventive Care": 10,
            "Follow-up": 11,
            "Referral Coordination": 9,
            "Other": 10,
        }[category]
        duration = int(max(4, round(rng.normal(duration_mean, 4))))

        referral_rate = {
            "General Consultation": 0.04,
            "Respiratory": 0.06,
            "Gastrointestinal": 0.05,
            "Musculoskeletal": 0.11,
            "Skin": 0.07,
            "Injury": 0.14,
            "Preventive Care": 0.02,
            "Follow-up": 0.06,
            "Referral Coordination": 0.42,
            "Other": 0.03,
        }[category]
        referral = rng.random() < referral_rate
        follow_up = referral or (rng.random() < (0.12 + (0.08 if category in {"Injury", "Musculoskeletal"} else 0)))
        if referral:
            outcome = "Referred"
        elif follow_up:
            outcome = "Follow-up Advised"
        else:
            outcome = rng.choice(["Resolved", "Observation", "Information Provided"], p=[0.72, 0.18, 0.10])

        satisfaction = np.clip(5.0 - (wait / 55) + rng.normal(0, 0.55), 1, 5)
        visit_category = "Emergency Support" if priority == "Urgent" else rng.choice(config.VISIT_CATEGORIES, p=[0.60, 0.18, 0.02, 0.20])
        if follow_up and rng.random() < 0.55:
            visit_category = "Follow-up"

        rows.append(
            {
                "visit_id": f"VIS{i:06d}",
                "student_id": student_id,
                "visit_date": visit_date.strftime("%Y-%m-%d"),
                "month": visit_date.strftime("%B"),
                "year": int(visit_date.year),
                "service_category": category,
                "visit_category": visit_category,
                "symptom_category": category,
                "priority": priority,
                "wait_time_minutes": wait,
                "consultation_duration": duration,
                "outcome": outcome,
                "follow_up_required": bool(follow_up),
                "referral_required": bool(referral),
                "satisfaction_score": round(float(satisfaction), 1),
            }
        )

    return pd.DataFrame(rows)


def generate_access(students: pd.DataFrame, visits: pd.DataFrame, services: pd.DataFrame) -> pd.DataFrame:
    service_targets = services.set_index("service_category")["target_wait_time"].to_dict()
    service_cap = services.set_index("service_category")["monthly_capacity"].to_dict()
    student_segments = students["student_segment"].drop_duplicates().sort_values().tolist()
    rows = []

    utilization = visits.groupby(["service_category", "year", "month"]).size().groupby("service_category").mean()
    for segment in student_segments:
        for service in config.SERVICE_CATEGORIES:
            pressure = utilization.get(service, 0) / service_cap.get(service, 1)
            barrier = "None"
            status = "Available"
            if pressure > 1.02:
                status, barrier = "Delayed", "Capacity"
            if pressure > 1.18:
                status, barrier = "Restricted", "Waiting Time"
            if service == "Referral Coordination":
                status, barrier = "Referred", "Referral"
            if segment in {"First Year", "Hostel Resident"} and status == "Available" and pressure > 0.88:
                status, barrier = "Delayed", "Scheduling"
            if segment == "Day Scholar" and service in {"Follow-up", "Preventive Care"}:
                barrier = "Scheduling" if status == "Available" else barrier
            expected_wait = int(round(service_targets.get(service, 25) * (1 + max(pressure - 0.8, 0))))
            rows.append(
                {
                    "student_segment": segment,
                    "service_category": service,
                    "access_status": status,
                    "access_barrier": barrier,
                    "expected_wait_time": expected_wait,
                }
            )
    return pd.DataFrame(rows)


def introduce_quality_issues(rng: np.random.Generator, visits: pd.DataFrame) -> pd.DataFrame:
    dirty = visits.copy()
    n = len(dirty)

    duplicate_indices = rng.choice(dirty.index, size=80, replace=False)
    duplicate_rows = dirty.loc[duplicate_indices].copy()
    dirty = pd.concat([dirty, duplicate_rows], ignore_index=True)

    dirty.loc[rng.choice(dirty.index, size=120, replace=False), "student_id"] = np.nan
    dirty.loc[rng.choice(dirty.index, size=90, replace=False), "wait_time_minutes"] = -rng.integers(1, 25, size=90)
    dirty.loc[rng.choice(dirty.index, size=75, replace=False), "consultation_duration"] = rng.choice([0, -5, 240], size=75)
    dirty.loc[rng.choice(dirty.index, size=80, replace=False), "satisfaction_score"] = rng.choice([0, 6, 7], size=80)
    dirty.loc[rng.choice(dirty.index, size=90, replace=False), "service_category"] = rng.choice(
        list(config.CATEGORY_ALIASES.keys()), size=90
    )
    dirty.loc[rng.choice(dirty.index, size=40, replace=False), "service_category"] = "Dental Surgery"
    dirty.loc[rng.choice(dirty.index, size=40, replace=False), "visit_date"] = "2027-15-99"
    dirty.loc[rng.choice(dirty.index, size=65, replace=False), "outcome"] = "Resolved"
    dirty.loc[dirty.tail(65).index, "referral_required"] = True

    invalid_student_idx = rng.choice(dirty.index[:n], size=45, replace=False)
    dirty.loc[invalid_student_idx, "student_id"] = [f"STUX{i:04d}" for i in range(45)]
    return dirty.sample(frac=1, random_state=config.RANDOM_SEED).reset_index(drop=True)


def generate_all() -> GeneratedData:
    rng = np.random.default_rng(config.RANDOM_SEED)
    ensure_directories([config.DATA_RAW, config.DATA_PROCESSED, config.DATABASE_DIR, config.REPORTS_DIR, config.CHARTS_DIR])
    students = generate_students(rng)
    staff = generate_staff()
    services = generate_services()
    visits = generate_visits(rng, students, services)
    access = generate_access(students, visits, services)
    visits_dirty = introduce_quality_issues(rng, visits)
    return GeneratedData(students=students, staff=staff, services=services, visits_dirty=visits_dirty, access=access)


def save_generated_data(data: GeneratedData) -> None:
    data.students.to_csv(config.DATA_RAW / "students.csv", index=False)
    data.staff.to_csv(config.DATA_RAW / "staff.csv", index=False)
    data.services.to_csv(config.DATA_RAW / "services.csv", index=False)
    data.visits_dirty.to_csv(config.DATA_RAW / "visits_dirty.csv", index=False)
    data.access.to_csv(config.DATA_RAW / "access.csv", index=False)


if __name__ == "__main__":
    save_generated_data(generate_all())
    print(f"Synthetic raw data written to {config.DATA_RAW}")
