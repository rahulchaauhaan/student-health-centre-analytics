DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS staff;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS visits;
DROP TABLE IF EXISTS access;
DROP TABLE IF EXISTS capacity_utilization;

CREATE TABLE students (
    student_id TEXT PRIMARY KEY,
    department TEXT NOT NULL,
    program TEXT NOT NULL,
    year_of_study INTEGER NOT NULL,
    hostel TEXT NOT NULL,
    student_segment TEXT NOT NULL,
    population_group TEXT NOT NULL DEFAULT 'Student'
);

CREATE TABLE staff (
    staff_id TEXT PRIMARY KEY,
    staff_role TEXT NOT NULL,
    service_area TEXT NOT NULL,
    assigned_shift TEXT NOT NULL,
    monthly_target INTEGER NOT NULL
);

CREATE TABLE services (
    service_id TEXT PRIMARY KEY,
    service_name TEXT NOT NULL,
    service_category TEXT UNIQUE NOT NULL,
    monthly_capacity INTEGER NOT NULL,
    target_wait_time INTEGER NOT NULL
);

CREATE TABLE visits (
    visit_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    visit_date TEXT NOT NULL,
    month TEXT NOT NULL,
    year INTEGER NOT NULL,
    service_category TEXT NOT NULL,
    visit_category TEXT NOT NULL,
    symptom_category TEXT NOT NULL,
    priority TEXT NOT NULL,
    wait_time_minutes INTEGER NOT NULL,
    consultation_duration INTEGER NOT NULL,
    outcome TEXT NOT NULL,
    follow_up_required INTEGER NOT NULL,
    referral_required INTEGER NOT NULL,
    satisfaction_score REAL NOT NULL,
    month_num INTEGER NOT NULL,
    year_month TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (service_category) REFERENCES services(service_category)
);

CREATE TABLE access (
    student_segment TEXT NOT NULL,
    service_category TEXT NOT NULL,
    access_status TEXT NOT NULL,
    access_barrier TEXT NOT NULL,
    expected_wait_time INTEGER NOT NULL
);

CREATE TABLE capacity_utilization (
    year_month TEXT NOT NULL,
    service_category TEXT NOT NULL,
    visit_count INTEGER NOT NULL,
    monthly_capacity INTEGER NOT NULL,
    target_wait_time INTEGER NOT NULL,
    capacity_utilization_pct REAL NOT NULL,
    capacity_flag INTEGER NOT NULL
);
