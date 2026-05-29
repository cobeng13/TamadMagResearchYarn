# Research Gap Analysis

Generated: 2026-05-29 16:18:43
Model: gpt-5-mini

## Completion Status

completed

## Current Study Focus

Relationship and predictive value of clustered academic grades and pre-board grades per cluster on Radiologic Technologist Licensure Examination (RTLE) performance and licensure success across batches among Bachelor of Science in Radiologic Technology graduates in the Philippines (retrospective descriptive-correlational and predictive design).

## Positioning Guidance

The study should be framed as an institution-level predictive validation study. The defensible focus is whether routinely collected institutional indicators - clustered academic grades and pre-board grades per cluster - are associated with and predict RTLE performance and licensure success across batches in the available local dataset.

This positioning supports screening, forecasting, early warning, targeted remediation, and review-planning uses. It should not be framed as a causal study of what determines RTLE success, a full curriculum evaluation, a teaching-effectiveness evaluation, or a claim that any model can guarantee passing.

Preferred working title for downstream outline and writing stages: "Predictive Value of Clustered Academic Grades and Pre-Board Cluster Grades for Radiologic Technologist Licensure Examination Performance and Licensure Success Across Batches."

## Inputs Used

See `projects/<project>/logs/ai_gap_analysis_log.md` for the input file list.

## What Is Already Known

- Institutional mock/pre-board examination scores have been shown, in several Philippine and radiography-related studies, to be positively associated with licensure or certification outcomes and can be modeled using correlation, logistic regression, or discriminant analyses (e.g., Rabinoa2025MockBoardExaminationResult; Garcia2026; ChristineGouveia2024PredictiveValidityHesiRadiography).
- Overall in-program academic performance and clustered academic grades are plausible predictors of licensure performance based on allied-health and some RT-adjacent evidence (Flores2024; Garcia2026; Wolden2019 meta-analysis).
- Periodic internal written assessments (e.g., monthly exams) can strongly predict institutional comprehensive/revalidation exam performance in single-institution RT samples (Ampaso2022), although transferability to national RTLE requires verification.
- Clinical/internship/practicum ratings show mixed or generally weaker predictive relationships with multiple-choice licensure outcomes; ceiling effects and restricted-range in practicum ratings are commonly reported (Garcia2026; Wolden2019).
- Assessment design and psychometric checks (blueprint alignment, item difficulty, correction-for-guessing, reliability/reproducibility) matter for using pre-board instruments as predictors (Bera2024).
- Institutional- and cohort-level contextual factors (cohort size, institutional passing rates, temporal disruptions such as missing exam years) influence institutional outcomes and argue for cohort-year or multi-level considerations when pooling data (Ibañez2025).
- Program-level policies (minimum pre-board score requirements, required preparatory activities) can be associated with higher pre-board scores and indirectly with better licensure outcomes (ChristineGouveia2024PredictiveValidityHesiRadiography) — but evidence is correlational and context-dependent.

## What Remains Unknown

- Whether commonly used institutional pre-board/mock examinations in Philippine RT programs have item-level psychometric validation (difficulty, discrimination, reliability) and alignment with the RTLE blueprint.
- Whether a multi-year, individual-level, multi-cohort Philippine RT dataset linking clustered academic grades, pre-board grades per cluster, batch/cohort, review participation if available, retaker/first-time status, RTLE board examination grades per cluster, and pass/fail status exists and can be assembled for robust predictive modeling.
- Optimal operationalization of pre-board scores for prediction in the Philippine RT context (e.g., raw vs correction-for-guessing adjusted scores; first/last/highest/average pre-board score) remains to be empirically determined for this population.
- How repeat examinees (retakers) are coded and whether inclusion/exclusion materially changes predictive estimates in Philippine RT datasets (reporting unclear in several local studies).
- Whether proposed remediation or enhancement programs (mock scheduling, peer mentoring, intensive review phases) actually improve RTLE outcomes when evaluated prospectively — existing local sources propose interventions but do not present evaluation data.
- Availability of RTLE board examination grades per cluster (rather than only overall pass/fail) in institutional/PRC-linked records for cluster-level prediction - To be confirmed.
- Exact institutional grading scales and directionality (e.g., whether higher numeric course grade indicates better performance) and mapping of institutional course lists to stable clustered academic grade constructs for use as predictors.

## Population or Context Gaps

- Few large-sample, multi-institutional Philippine RT studies at the individual-record level exist; most RT evidence is single-site, review-center samples, or multisector but not RT-specific (limits generalizability to other Philippine RT programs).
- Heterogeneity across institutions in assessment practices, cohort sizes, and program policies (and missing-year disruptions like 2020) reduces confidence in simple pooled estimates without multi-level controls.
- Local RT studies often lack evaluated programmatic interventions; recommendations for remediation or review-strengthening are frequently prescriptive and unevaluated.

## Local / Philippine Context Gaps

- Item-level psychometric validation and publicly reported reliability metrics for institutional pre-board/mock exams used in Philippine RT programs are largely absent in the supplied evidence.
- Clear documentation of how local studies handled repeat examinees, missing cohort years (e.g., 2020), and linkage approaches to PRC outcomes is often missing or incomplete (To be confirmed in source datasets).
- Mapping of RT curriculum course lists to standardized clustered academic grade measures appropriate for cross-batch comparison is not established for the Philippine RT context.

## Methodological Gaps

- Many RT-specific studies have small sample sizes and single-site designs that reduce statistical power and increase risk of biased effect-size estimates; larger individual-level datasets are needed.
- Pre-board instrument measurement choices (raw vs corrected scores; inclusion of higher- vs lower-order items; item-level scoring) are inconsistently applied and often unreported; psychometric preprocessing is required before using these scores as predictors.
- When combining institutions or cohorts, multi-level modeling or inclusion of cohort-year and institutional covariates is necessary but seldom implemented in the local RT studies.
- Sensitivity analyses for operationalizations of pre-board scores (first vs last vs average; corrected vs raw) and for inclusion/exclusion of retakers are needed but not widely reported.
- Reporting conventions (e.g., direction of pass/fail coding, grade-scale orientation) are sometimes ambiguous in supplied studies and must be clarified to avoid analytic misinterpretation (Flores2024 example where correlation sign required interpretation).

## Variable or Measurement Gaps

- Availability and format of pre-board data: item-level responses, numeric raw scores, percent-correct, corrected-for-guessing scores, or categorical pass/fail needs confirmation.
- Availability of RTLE board examination grades per cluster for cluster-level prediction versus only overall pass/fail or single numeric rating.
- Clinical/internship rating scales, rubrics, and score distributions (potential ceiling effects) must be examined prior to modeling.
- Academic cluster definitions, course membership, and weighting used to compute clustered academic grades must be confirmed and standardized across batches.
- Pre-board cluster definitions and their alignment with RTLE board examination clusters must be confirmed before modeling.
- Presence and format of covariates: first-time vs retaker indicator, review center participation, time between graduation and board exam, admission-test scores, and demographic variables — availability must be confirmed.

## Evidence Limitations

- Several relevant studies are single-site or small-sample (n < 50) RT or allied-health samples, limiting external validity.
- Some supportive allied-health evidence comes from other disciplines (dentistry, physical therapy) or other jurisdictions (U.S. radiography HESI → ARRT) and may not transfer directly to Philippine RT without local validation.
- Pre-board/mock instruments frequently lack publicly reported psychometric properties, raising measurement-quality concerns when used as predictors.
- Aggregated institutional analyses (counts by year) cannot substitute for individual-level predictive modeling; ecological inference risk exists if aggregated findings are over-interpreted.

## Direct vs Indirect Evidence Balance

Direct Philippine RT evidence supports that pre-board/mock scores can predict licensure outcomes in some local samples (e.g., Rabinoa2025MockBoardExaminationResult), but much of the strongest predictive operational-method evidence derives from allied radiography and multi-program datasets (ChristineGouveia2024PredictiveValidityHesiRadiography; Garcia2026). Several allied-health sources (Flores2024) show mixed/null findings, implying heterogeneity by instrument alignment, timing, and sample composition. Overall, there is a moderate balance of direct local evidence for pre-board predictive value and stronger indirect methodological support for careful instrument construction and operationalization.

## Safe Gap Statement

There is plausible, context-relevant evidence that academic performance and aligned pre-board/mock exam scores can predict licensure outcomes, but important measurement, sampling, and contextual gaps remain in Philippine RT literature. For this study, the applied gap is the local predictive validity of clustered academic grades and pre-board grades per cluster for RTLE board examination grades per cluster and pass/fail licensure success across batches. This study can address several of these gaps at the institution(s) under study if unresolved data items are confirmed and appropriate analytic procedures are applied.

## Gap Claims Requiring Caution

- Avoid claiming that pre-board/mock examinations universally predict RTLE outcomes across Philippine programs — predictive validity depends on local instrument alignment and psychometric quality (Flores2024 counterexample).
- Avoid causal language that program policies or remediation interventions cause higher RTLE pass rates unless supported by prospective or quasi-experimental evaluation (existing evidence is largely correlational).
- Avoid overgeneralizing single-institution findings to the national level without multi-site replication or multi-level adjustment for cohort/institution effects.
- Avoid interpreting high practicum ratings as evidence of strong predictive power for RTLE scores without checking for restricted range and rater leniency (Garcia2026; Wolden2019).

## To Be Confirmed

- Exact institutional setting(s) and whether the dataset will be single-site or multi-site.
- Cohort years to be included and whether RTLE data are available for those years (noting possible missing years such as 2020).
- Whether the RTLE outcome(s) available are board examination grades per cluster, binary pass/fail status, overall licensure rating, or some combination.
- Whether institutional pre-board/mock exam item-level data and psychometric metadata (item IDs, item content, cognitive-level coding) are available.
- Whether internship/practicum rubrics and detailed ratings (domain-level) are accessible and their score scaling direction.
- Whether retaker/first-time taker status is recorded and how repeat attempts should be handled per study inclusion criteria.
- Exact grading scale and directionality used for clustered academic grades and pre-board cluster grades (e.g., numeric system where higher is better vs inverted).
- Availability of review-participation data (review center attendance, mandatory/optional mock participation) and program-policy indicators.
- Whether PRC/RTLE board examination grades per cluster (not just pass/fail) can be legally and ethically accessed and linked to institutional records.

## Recommended Next Step

Assemble and clean an individual-level dataset for the chosen institution(s) that links clustered academic grades, pre-board grades per cluster, batch/cohort, and PRC RTLE outcomes including board examination grades per cluster and pass/fail result. Before modeling, confirm cluster definitions and, if item-level data are available, perform psychometric analyses on the pre-board instrument(s) (item difficulty, discrimination, reliability; consider correction-for-guessing and cognitive-level composition). Pre-specify inclusion/exclusion (first-taker vs retaker), missing-data handling, and sensitivity analyses (raw vs adjusted pre-board cluster grades; first vs last vs average pre-board cluster grade). Then run descriptive profiling, correlation matrices, univariate screening, multivariable prediction models for RTLE cluster performance, logistic regression or comparable classification for pass/fail, incremental-value tests for pre-board cluster grades beyond clustered academic grades, and across-batch comparisons. Explicitly mark unresolved data items as 'To be confirmed' and avoid causal claims; frame programmatic recommendations as conditional and institution-specific.

## Positioning Addendum From Topic Review

The safest applied gap for this project is narrower than a broad literature-novelty claim: the institution already collects clustered academic grades, pre-board grades per cluster, board examination grades per cluster, pass/fail outcomes, and batch data, but the local predictive validity, incremental usefulness, and across-batch patterns of these indicators have not yet been confirmed for the target cohorts.

Additional cautions:

- Avoid saying that grades or pre-board scores cause RTLE success. Use association, prediction, predictive validity, or readiness-indicator language.
- Avoid presenting the model as a guarantee that a student will pass or fail. Use elevated risk, likely readiness indicator, or support-planning language.
- Confirm whether clustered academic grade definitions can be constructed consistently across curriculum years and batches.
- Confirm whether pre-board grades per cluster are available as first, last, highest, or average scores; this affects predictive modeling.
- Test whether pre-board grades per cluster add predictive value beyond clustered academic grades if sample size and data quality allow.
- Compare academic performance, pre-board performance, RTLE performance, and licensure success across batches.

Refined next step: assemble and clean an individual-level institutional dataset linking clustered academic grades, pre-board grades per cluster, batch, RTLE board examination grades per cluster, and pass/fail outcomes. Treat RTLE cluster grades as the primary performance outcomes if available, with pass/fail as the licensure success outcome. Test bivariate relationships, multivariable prediction, incremental pre-board value, and across-batch differences. Use psychometric checks for pre-board instruments if item-level data are available. Keep recommendations conditional and institution-specific.
