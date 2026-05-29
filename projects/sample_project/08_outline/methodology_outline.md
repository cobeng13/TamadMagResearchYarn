# Methodology Outline

Generated: 2026-05-29 20:38:42
Model: gpt-5-mini

## Research Design

Retrospective descriptive-correlational and predictive validation using existing institutional academic records, pre-board/mock exam records, and linked RTLE outcomes. Emphasize psychometric preprocessing of pre-board instruments before predictive modeling.

## Study Setting

Host BSRT program(s) in the Philippines — specify institution name(s) and campus(es) or mark 'To be confirmed' if not yet finalized. Note cohort years included and any missing exam years (e.g., COVID-19 disruptions). [To be confirmed]

## Population and Sampling

All BSRT graduates in the selected cohort years who have institutional academic records and verifiable RTLE outcomes. Pre-specify inclusion/exclusion: exclude non-graduates, decide on retaker handling (exclude retakers or analyze sensitivity), exclude records missing key predictors if missing-data methods cannot recover them.

## Variables

- Predictors: clustered academic grades; pre-board grades per cluster; batch/cohort; optional covariates only if available and ethically usable. Cluster definitions, included courses, pre-board cluster mapping, and weighting schemes are To be confirmed.
- Outcomes: Preferred: continuous RTLE numeric rating (To be confirmed); Alternate/secondary: RTLE pass/fail (binary); Subject-area RTLE scores (To be confirmed).
- Covariates: cohort year, first-time vs retaker status, time between graduation and exam, review participation/center attendance, demographic variables if available and ethically permissible.

## Data Sources

- Registrar and academic records used to compute clustered academic grades.
- Departmental records documenting cluster definitions, included courses, and weighting rules.
- Pre-board records with grades or scores per cluster.
- Internship/practicum assessment records and rubrics.
- Pre-board/mock exam records (raw scores, item metadata) from institutional exam administration or review-center partners.
- PRC/RTLE official outcomes (linked per student; access permissions To be confirmed).
- Administrative metadata (cohort year, retaker flag, review participation).

## Measures and Operational Definitions

- Clustered academic grades: define included courses, cluster membership, numerator/denominator, grade-scale orientation, weighting, and transformations used.
- Pre-board grades per cluster: define cluster labels, item/content coverage, scoring rules, and alignment with RTLE board examination clusters.
- Pre-board scores: raw percent-correct, correction-for-guessing adjusted score (specify formula per Şenel or other referenced method), cognitive-level composition; identify whether multiple pre-board attempts exist and how to operationalize (first, last, highest, average). [@Bera2024AssessingPerformanceMultimodalChatgpt4]
- Internship/practicum ratings: rubric items, scoring range, and rater training; note potential ceiling effects and plan distributional checks.
- RTLE outcome coding: confirm whether PRC provides an overall numeric rating and subject scores; document coding of pass/fail and ensure correct directionality.

## Statistical Analysis Plan

- Descriptive statistics for all variables (central tendency, dispersion, distribution checks).
- Psychometric analyses for pre-board instrument(s): item difficulty, item-total correlations, discrimination indices, Cronbach's alpha (or other appropriate reliability coefficient), reproducibility checks if repeated administrations exist; produce raw and adjusted pre-board scores.
- Bivariate analysis: correlation matrix (Spearman/Pearson as appropriate) between predictors and RTLE outcomes; visualization of relationships.
- Predictive modeling: regression or comparable models for RTLE board examination grades per cluster; logistic regression or comparable classification for pass/fail licensure success; nested-model testing to measure incremental predictive value of pre-board grades per cluster beyond clustered academic grades.
- Classification and validation: if sample size permits, apply cross-validation (k-fold) or holdout validation; report sensitivity, specificity, positive predictive value, negative predictive value, calibration (e.g., calibration plots), and AUC.
- Alternative models: discriminant analysis or other supervised classification per precedent (Garcia2026) if assumptions are met and sample supports it.
- Sensitivity analyses: raw vs corrected pre-board cluster scoring; first/last/highest/average pre-board cluster operationalizations; inclusion/exclusion of retakers; alternative academic cluster definitions; batch-adjusted or multi-level models if pooling batches/institutions.
- Missing-data approach: document extent and mechanism of missingness; apply multiple imputation or complete-case analysis with sensitivity tests as appropriate.

## Ethical Considerations

Data de-identification and secure storage; institutional ethical approval and data-use agreements for PRC linkage if required; minimization of reporting that could re-identify individuals; obtain necessary approvals and follow data-protection rules (To be confirmed).

## Limitations of Method

- Retrospective, observational design limits causal inference.
- Potential selection biases if retakers or certain cohorts excluded.
- Measurement quality of pre-board instruments may vary and affect inference if item-level data are absent.
- Sample-size constraints may limit multivariable model complexity and external generalizability.

## To Be Confirmed

- Institution name(s) and cohort years included.
- Availability of PRC/RTLE continuous rating and subject scores and legal/ethical permissions to access them.
- Availability of pre-board item-level data to perform psychometric analyses.
- Exact grading scales, cluster definitions, course lists, and weighting rules used to compute clustered academic grades and pre-board grades per cluster.
- Presence and coding of retaker/first-time taker variable in administrative records.
