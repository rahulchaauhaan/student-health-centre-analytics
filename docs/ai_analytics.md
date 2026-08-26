# Responsible AI Considerations

This project uses synthetic academic data only. AI can support analytics communication, but it must not diagnose students, make medical decisions, make treatment recommendations, or replace human review.

## Where AI Can Help

- Summarize monthly KPI changes after Python and SQL calculations are complete.
- Draft concise management summaries from validated dashboard findings.
- Identify unusual operational trends such as wait-time spikes or capacity exceptions.
- Suggest analytical follow-up questions for the health-centre operations team.
- Convert technical findings into stakeholder-friendly language.

## Required Controls

- AI output must be checked against SQL results, Python outputs, and source tables.
- AI summaries should cite the KPI or table they are based on.
- AI should describe uncertainty where trends are weak or synthetic assumptions drive the result.
- AI should not infer sensitive personal information from student-level records.
- AI should not generate clinical advice from symptom categories.

## What AI Must Never Do

- Diagnose a student.
- Recommend treatment.
- Decide referral urgency.
- Predict an individual student's health condition.
- Replace qualified health-centre staff.
- Process real health records without privacy, consent, security, and governance controls.

## Appropriate Use In This Project

AI is framed as a productivity aid for operational analytics: summarizing validated KPIs, drafting recurring report language, and helping analysts decide which trend to inspect next.

## Project Scope

This repository does not include an integrated AI feature or medical chatbot. AI is documented only as a future responsible-analytics consideration.
