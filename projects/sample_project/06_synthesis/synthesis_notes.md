# Synthesis Notes

## Completion Status

completed

## Inputs Used

- Project: C:\MEGASync\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project
- Stage 05 evidence table and available paper summaries.

## Main Themes

- Pre-board / mock examination performance as predictor of licensure success
- Overall academic performance and professional-course grades as predictors
- Clinical / internship / practicum performance
- Non-cognitive, attitudinal, and readiness measures
- Assessment design, psychometrics, and measurement issues
- Institutional and cohort/contextual predictors (aggregate-level effects)
- Program policies, remediation, and review practices

## Strongest Evidence

- Institutional mock/pre-board exam scores are often positively associated with licensure or certification outcomes in radiography and RT samples (e.g., Rabinoa2025MockBoardExaminationResult; ChristineGouveia2024PredictiveValidityHesiRadiography).
- Overall in-program academic performance (GWA/professional-course averages) is a plausible predictor of licensure exam performance based on allied-health evidence and RT operational precedents (Flores2024; Wolden2019; Garcia2026).
- Periodic institutional written assessments (monthly exams) can strongly predict institutional comprehensive exam outcomes within single-institution RT samples (Ampaso2022), but transferability to national RTLE requires confirmation.
- Assessment instrument design and psychometric evaluation (blueprint alignment, difficulty ratings, reliability, correction-for-guessing) are important prerequisites before using pre-board scores as predictive inputs (Bera2024).

## Weakest or Most Uncertain Evidence

- Evidence rows (107) exceed batch-size (20); using one bounded request with all selected rows.
- Large multi-institutional, individual-level Philippine RT datasets linking GWA, detailed professional-course grades, pre-board item-level scores, clinical/practicum ratings, review center participation, first-time vs retaker status, and PRC RTLE subject-area scores.
- Psychometric validation (item analyses, reliability coefficients) of commonly used institutional pre-board/mock exams in Philippine RT programs and demonstrated alignment with RTLE content/blueprint.
- Clear reporting on inclusion/exclusion of repeat examinees, handling of missing cohorts/years (e.g., 2020), and coding conventions for licensure outcomes (directionality of pass/fail coding) in several local studies (To be confirmed).
- Evaluated (pre-post or controlled) studies of programmatic interventions (mock exam schedules, remediation programs) demonstrating impact on RTLE outcomes.

## Claims Safe to Use Later

- Institutional mock/pre-board exam scores are often positively associated with licensure or certification outcomes in radiography and RT samples (e.g., Rabinoa2025MockBoardExaminationResult; ChristineGouveia2024PredictiveValidityHesiRadiography).
- Overall in-program academic performance (GWA/professional-course averages) is a plausible predictor of licensure exam performance based on allied-health evidence and RT operational precedents (Flores2024; Wolden2019; Garcia2026).
- Periodic institutional written assessments (monthly exams) can strongly predict institutional comprehensive exam outcomes within single-institution RT samples (Ampaso2022), but transferability to national RTLE requires confirmation.
- Assessment instrument design and psychometric evaluation (blueprint alignment, difficulty ratings, reliability, correction-for-guessing) are important prerequisites before using pre-board scores as predictive inputs (Bera2024).

## Claims Requiring Caution

- Do not assume pre-board exams universally predict national licensure outcomes — predictive validity depends on instrument alignment, timing, psychometric quality, and sample composition (Flores2024 counterexample; Ampaso2022 caveat regarding case-study scores).
- Clinical/internship ratings may show weak predictive relationships with multiple-choice licensure exams, particularly when ratings show restricted range or ceiling effects (Wolden2019; Garcia2026), so interpret small or null effects cautiously.
- Aggregated institutional-level models (counts of failed examinees) cannot be used to infer individual-level predictors without appropriate multi-level modeling or individual-level data (Ibañez2025).
- Associations reported in included studies (cross-sectional, retrospective) are correlational; causal claims about interventions improving RTLE outcomes require prospective or experimental evaluation (policy mediation in ChristineGouveia2024PredictiveValidityHesiRadiography is indirect evidence, not causal proof).

## Missing Evidence / To be confirmed

- Evidence rows (107) exceed batch-size (20); using one bounded request with all selected rows.
- Large multi-institutional, individual-level Philippine RT datasets linking GWA, detailed professional-course grades, pre-board item-level scores, clinical/practicum ratings, review center participation, first-time vs retaker status, and PRC RTLE subject-area scores.
- Psychometric validation (item analyses, reliability coefficients) of commonly used institutional pre-board/mock exams in Philippine RT programs and demonstrated alignment with RTLE content/blueprint.
- Clear reporting on inclusion/exclusion of repeat examinees, handling of missing cohorts/years (e.g., 2020), and coding conventions for licensure outcomes (directionality of pass/fail coding) in several local studies (To be confirmed).
- Evaluated (pre-post or controlled) studies of programmatic interventions (mock exam schedules, remediation programs) demonstrating impact on RTLE outcomes.

## Recommended Next Step

Assemble an individual-level dataset for the target institution(s) linking GWA, professional-course grades, clinical/internship ratings, pre-board/mock exam raw and (if available) item-level scores, review participation, cohort year, and RTLE outcomes (continuous rating and pass/fail). Before modeling, perform psychometric checks on pre-board instruments (item difficulty, discrimination, reliability, consider correction-for-guessing). Then run staged analyses: descriptive profiling, correlation matrices, univariate screening, multivariable logistic regression for pass/fail with cross-validation, and sensitivity analyses across operationalizations (raw vs corrected pre-board scores; inclusion/exclusion of repeaters). If pooling across institutions, consider multi-level models to account for institution/cohort-level effects. Mark any unresolved data issues explicitly as 'To be confirmed' (cohort years, inclusion of repeaters, exact grade scales, and availability of subject-area RTLE scores).
