-- name: 01_monthly_visit_volume
SELECT
    year_month,
    COUNT(*) AS total_visits,
    COUNT(DISTINCT student_id) AS unique_students,
    ROUND(AVG(wait_time_minutes), 2) AS avg_wait_time
FROM visits
GROUP BY year_month
ORDER BY year_month;

-- name: 02_service_utilization
SELECT
    v.service_category,
    s.service_name,
    COUNT(*) AS visits,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_of_total_visits
FROM visits v
JOIN services s ON v.service_category = s.service_category
GROUP BY v.service_category, s.service_name
ORDER BY visits DESC;

-- name: 03_average_waiting_time
SELECT
    service_category,
    ROUND(AVG(wait_time_minutes), 2) AS avg_wait_time,
    ROUND(AVG(CASE WHEN wait_time_minutes > 45 THEN 1.0 ELSE 0 END) * 100, 2) AS pct_over_45_minutes
FROM visits
GROUP BY service_category
HAVING COUNT(*) >= 100
ORDER BY avg_wait_time DESC;

-- name: 04_department_level_utilization
SELECT
    st.department,
    COUNT(v.visit_id) AS total_visits,
    COUNT(DISTINCT v.student_id) AS students_served,
    ROUND(COUNT(v.visit_id) * 1.0 / COUNT(DISTINCT v.student_id), 2) AS visits_per_served_student
FROM students st
LEFT JOIN visits v ON st.student_id = v.student_id
GROUP BY st.department
ORDER BY total_visits DESC;

-- name: 05_hostel_level_utilization
SELECT
    st.hostel,
    COUNT(v.visit_id) AS total_visits,
    COUNT(DISTINCT v.student_id) AS students_served,
    ROUND(AVG(v.wait_time_minutes), 2) AS avg_wait_time
FROM students st
LEFT JOIN visits v ON st.student_id = v.student_id
GROUP BY st.hostel
ORDER BY total_visits DESC;

-- name: 06_student_segment_analysis
SELECT
    st.student_segment,
    COUNT(v.visit_id) AS total_visits,
    COUNT(DISTINCT v.student_id) AS students_served,
    ROUND(AVG(v.wait_time_minutes), 2) AS avg_wait_time,
    ROUND(AVG(CASE WHEN v.referral_required = 1 THEN 1.0 ELSE 0 END) * 100, 2) AS referral_rate_pct
FROM students st
LEFT JOIN visits v ON st.student_id = v.student_id
GROUP BY st.student_segment
ORDER BY avg_wait_time DESC;

-- name: 07_referral_rate
SELECT
    service_category,
    COUNT(*) AS visits,
    SUM(CASE WHEN referral_required = 1 THEN 1 ELSE 0 END) AS referrals,
    ROUND(AVG(CASE WHEN referral_required = 1 THEN 1.0 ELSE 0 END) * 100, 2) AS referral_rate_pct
FROM visits
GROUP BY service_category
ORDER BY referral_rate_pct DESC;

-- name: 08_follow_up_rate
SELECT
    service_category,
    COUNT(*) AS visits,
    SUM(CASE WHEN follow_up_required = 1 THEN 1 ELSE 0 END) AS follow_ups,
    ROUND(AVG(CASE WHEN follow_up_required = 1 THEN 1.0 ELSE 0 END) * 100, 2) AS follow_up_rate_pct
FROM visits
GROUP BY service_category
ORDER BY follow_up_rate_pct DESC;

-- name: 09_satisfaction_trends
SELECT
    year_month,
    ROUND(AVG(satisfaction_score), 2) AS avg_satisfaction,
    ROUND(AVG(wait_time_minutes), 2) AS avg_wait_time
FROM visits
GROUP BY year_month
ORDER BY year_month;

-- name: 10_capacity_utilization
WITH ranked_pressure AS (
    SELECT
        year_month,
        service_category,
        visit_count,
        monthly_capacity,
        capacity_utilization_pct,
        RANK() OVER (PARTITION BY year_month ORDER BY capacity_utilization_pct DESC) AS pressure_rank
    FROM capacity_utilization
)
SELECT *
FROM ranked_pressure
WHERE pressure_rank <= 3
ORDER BY year_month, pressure_rank;

-- name: 11_access_restriction_rate
SELECT
    student_segment,
    COUNT(*) AS segment_service_combinations,
    ROUND(AVG(CASE WHEN access_status = 'Restricted' THEN 1.0 ELSE 0 END) * 100, 2) AS restricted_rate_pct,
    ROUND(AVG(CASE WHEN access_status = 'Delayed' THEN 1.0 ELSE 0 END) * 100, 2) AS delayed_rate_pct
FROM access
GROUP BY student_segment
ORDER BY restricted_rate_pct DESC, delayed_rate_pct DESC;

-- name: 12_access_barriers
SELECT
    service_category,
    access_barrier,
    COUNT(*) AS occurrences
FROM access
WHERE access_barrier <> 'None'
GROUP BY service_category, access_barrier
ORDER BY occurrences DESC, service_category;

-- name: 13_monthly_performance
WITH monthly AS (
    SELECT
        year_month,
        COUNT(*) AS total_visits,
        ROUND(AVG(wait_time_minutes), 2) AS avg_wait_time,
        ROUND(AVG(satisfaction_score), 2) AS avg_satisfaction,
        ROUND(AVG(CASE WHEN referral_required = 1 THEN 1.0 ELSE 0 END) * 100, 2) AS referral_rate_pct
    FROM visits
    GROUP BY year_month
)
SELECT
    year_month,
    total_visits,
    total_visits - LAG(total_visits) OVER (ORDER BY year_month) AS visit_change,
    avg_wait_time,
    avg_satisfaction,
    referral_rate_pct
FROM monthly
ORDER BY year_month;

-- name: 14_high_workload_periods
SELECT
    year_month,
    service_category,
    visit_count,
    monthly_capacity,
    capacity_utilization_pct
FROM capacity_utilization
WHERE capacity_utilization_pct >= 100
ORDER BY capacity_utilization_pct DESC;

-- name: 15_exception_identification
SELECT
    c.year_month,
    c.service_category,
    c.capacity_utilization_pct,
    ROUND(AVG(v.wait_time_minutes), 2) AS avg_wait_time,
    s.target_wait_time,
    CASE
        WHEN c.capacity_utilization_pct > 115 THEN 'Critical capacity pressure'
        WHEN c.capacity_utilization_pct > 100 THEN 'Capacity exceeded'
        WHEN AVG(v.wait_time_minutes) > s.target_wait_time * 1.5 THEN 'Wait-time exception'
        ELSE 'Monitor'
    END AS exception_type
FROM capacity_utilization c
JOIN services s ON c.service_category = s.service_category
JOIN visits v ON c.year_month = v.year_month AND c.service_category = v.service_category
GROUP BY c.year_month, c.service_category, c.capacity_utilization_pct, s.target_wait_time
HAVING c.capacity_utilization_pct > 100 OR AVG(v.wait_time_minutes) > s.target_wait_time * 1.5
ORDER BY c.year_month, c.capacity_utilization_pct DESC;
