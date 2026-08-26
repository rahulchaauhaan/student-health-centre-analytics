# Business Questions

All findings use synthetic college health-centre data generated for this academic course project.

| # | Business question | KPI | SQL/Python method | Result | Interpretation | Recommendation |
|---|---|---|---|---|---|---|
| 1 | What are the busiest health-centre periods? | Monthly visit volume | SQL GROUP BY year_month and Python trend chart | 2025-03 had the highest activity with 2,499 visits. | Demand rises during exam and respiratory-pressure periods in the synthetic pattern. | Pre-plan staffing and registration support for peak months. |
| 2 | Which services have the highest demand? | Service visit count | SQL JOIN visits to services and rank by count | General Consultation was the highest-demand service with 15,633 visits. | General access is the main workload driver. | Protect core consultation capacity before adding new services. |
| 3 | Which services experience capacity pressure? | Capacity utilization | SQL CTE ranks service-month utilization | Respiratory reached the highest monthly capacity pressure at 203.8% in 2025-01. | Some service-month combinations exceed planned monthly capacity. | Use temporary capacity, better appointment spacing, or triage during pressure months. |
| 4 | Which departments/hostels generate the most visits? | Department and hostel utilization | SQL LEFT JOIN students to visits | Computer Science had 10,957 visits; Day Scholar had 13,985. | Utilization differs by academic and residence groups. | Share targeted preventive communication with high-use groups. |
| 5 | Which services have the longest waiting times? | Average wait time | SQL GROUP BY service_category with HAVING threshold | Musculoskeletal averaged 35.99 minutes. | Higher complexity and pressure raise waits. | Monitor queue design and staff allocation for these services. |
| 6 | What proportion of visits require referral? | Referral rate | SQL CASE WHEN referral_required = 1 | Overall referral rate was 7.27%; highest was Referral Coordination at 42.92%. | Referrals are concentrated in specific service categories. | Review referral coordination workload separately from basic visit counts. |
| 7 | Which student segments experience greater access delays? | Delayed/restricted access rate | SQL grouped access-status matrix | First Year had the most delayed or restricted access combinations in the synthetic access matrix. | Access pressure is not evenly distributed across segments. | Use student-segment reporting to spot scheduling and access barriers. |
| 8 | Is higher utilization associated with longer waiting time? | Utilization-wait correlation | Python correlation between service-month utilization and average wait | Utilization and wait time correlation was 0.61, indicating measurable operational coupling. | The synthetic data shows measurable coupling between capacity use and wait time. | Treat wait time as an early signal of capacity pressure. |
| 9 | Where are the largest operational execution gaps? | Exception count and gap | SQL exception query with CASE WHEN | Top exception: Respiratory in 2024-01 at 178.85% utilization. | Execution gaps appear where demand exceeds practical service capacity. | Prioritize peak-month service-area staffing and follow-up coordination. |
| 10 | What operational improvements should management consider? | Combined KPI layer | Python KPI layer, SQL exceptions, dashboard views | 77 capacity exceptions flagged across the dataset. | Recurring reporting can convert manual record review into measurable operations management. | Automate monthly KPI review, monitor exceptions, and validate data quality before decision-making. |

## Stakeholder Scenario

The health centre wants a better understanding of historical utilization, workload, waiting times and access barriers so that it can improve recurring reporting and allocate operational capacity more effectively.

Business question -> requirements -> structured dataset -> data validation -> SQL -> Python -> dashboard -> insight -> recommendation.
