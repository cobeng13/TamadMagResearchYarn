# Results Interpretation Notes

Generated: 2026-05-30 00:54:10
Model: gpt-5-mini

## Completion Status

completed

## Inputs Used

- C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\input\statistical_results_compiled.md
- C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\input\statistical_results.md
- C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\input\statistical_results_manifest.csv
- C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\input\results_availability.md
- C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\input\human_confirmed_context.md
- C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\07_gap_analysis\problem_statement_refined.md
- C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\06_synthesis\synthesis_notes.md
- C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\07_gap_analysis\study_contribution.md
- C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\00_brief\research_questions.md
- C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\00_brief\variables.md
- C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\input\methodology_details.md
- C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\08_outline\results_outline.md
- C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\08_outline\outline_readiness_checklist.md
- C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\08_outline\discussion_outline.md

## Study Objectives / Research Questions

- 1. Describe the graduates' academic performance profile based on clustered grades.
- 2. Describe the graduates' pre-board examination performance per cluster.
- 3. Describe the graduates' RTLE outcomes in terms of board examination grades per cluster and pass/fail result.
- 4. Determine whether clustered academic grades are significantly related to RTLE performance.
- 5. Determine whether pre-board grades per cluster are significantly related to RTLE performance.
- 6. Determine whether clustered academic grades and pre-board grades per cluster significantly predict RTLE performance.
- 7. Determine whether clustered academic grades and pre-board grades per cluster significantly predict licensure success (pass/fail).
- 8. Identify which predictor or predictor set best explains variation in RTLE performance and licensure success.
- 9. Determine whether pre-board grades per cluster add predictive value beyond clustered academic grades in explaining RTLE performance and pass/fail outcome.
- 10. Compare academic performance, pre-board performance, RTLE performance, and licensure success across batches.

## Results Availability Summary

Complete set of aggregate/descriptive statistics (N=92) available (summary_stats.csv); ANOVA results across batches for multiple clustered academic and pre-board variables available (anova_results.csv); pairwise correlations between clustered academic/pre-board variables and RTLE subject outcomes present (correlations.csv); OLS regression summaries (CG-only, PB-only, Combined) for each RTLE subject (Subj01-Subj05) and GEN_AVE available (regression_summaries.txt); logistic regression results for pass/fail (CG-only, PB-only, Combined) and model-level classification accuracies provided (logit_accuracies.csv); pass/fail counts by batch and chi-square test available (passfail_by_batch.csv, passfail_chi2.csv). Psychometric/item-level analyses of pre-board instruments, VIF/multicollinearity diagnostics beyond condition-number notes, ROC AUC confidence intervals and calibration metrics, and item-level pre-board data are missing.

## Findings by Objective

### 1

* Available result(s): summary_stats.csv: cluster means, SDs, min/percentiles/max for CG1-CG5; regression_summaries.txt: sample size and model diagnostic notes (N=92)
* Statistical test/model: Descriptive statistics (means, SD, min, quartiles, max) from summary_stats.csv
* Key numerical findings: N = 92 (No. Observations reported in regression outputs and summary_stats.csv).; CG1 mean = 87.5963 (SD = 4.211); CG2 mean = 85.7464 (SD = 4.789); CG3 mean = 86.7114 (SD = 4.250); CG4 mean = 86.1893 (SD = 8.192); CG5 mean = 86.4135 (SD = 2.352)
* Significance status: not_tested
* Plain-language result: Clustered academic grades are available for all 5 clusters for 92 graduates; cluster means are in the mid-80s with CG4 showing larger spread (SD~8.2) and CG5 the narrowest spread (SD~2.35).
* Interpretation boundary: Descriptive only; no causal claims.
* To be confirmed: Clarify cluster definitions (which courses included per cluster) and grade scale direction (confirmed in methodology but cluster composition not listed).

### 2

* Available result(s): summary_stats.csv: pre-board cluster means and spread for PB1-PB5
* Statistical test/model: Descriptive statistics
* Key numerical findings: PB1 mean = 52.6848 (SD = 12.604); PB2 mean = 56.9348 (SD = 12.587); PB3 mean = 49.6304 (SD = 15.458); PB4 mean = 64.3804 (SD = 17.168); PB5 mean = 59.5543 (SD = 21.504)
* Significance status: not_tested
* Plain-language result: Pre-board cluster scores (PB1–PB5) vary by cluster; PB4 has the highest mean and PB3 the lowest mean; variability is substantial in some clusters (PB5 SD ~21.5, PB4 SD ~17.2).
* Interpretation boundary: Descriptive only.
* To be confirmed: Specification of pre-board score scaling (raw counts vs. percentage) and whether these represent single attempt or aggregated attempts.

### 3

* Available result(s): summary_stats.csv: Subj01–Subj05 and GEN_AVE means and SDs; passfail_by_batch.csv: pass/fail counts by batch; passfail_chi2.csv: chi-square test for pass/fail by batch
* Statistical test/model: Descriptive statistics; contingency table and chi-square test
* Key numerical findings: Subj01 mean = 68.4130 (SD = 10.956); Subj02 mean = 77.5109 (SD = 9.500); Subj03 mean = 73.0978 (SD = 12.029); Subj04 mean = 80.3152 (SD = 7.429); Subj05 mean = 75.9348 (SD = 13.111); GEN_AVE mean = 75.0543 (SD = 9.319); Pass/fail by batch (counts): 2022: FAILED=9, PASSED=19; 2023: FAILED=15, PASSED=17; 2024: FAILED=12, PASSED=20; Total (sum across batches) matches N=92 (Failed total = 36, Passed total = 56).; Chi-square test for pass/fail by batch: Chi2 = 1.4155, p = 0.4928 (df = 2) — no evidence of association between batch and pass/fail counts.
* Significance status: not_significant
* Plain-language result: Average RTLE subject and overall scores are reported; pass/fail counts vary numerically by batch but the chi-square test shows no statistically significant association between batch year and pass/fail status in this dataset.
* Interpretation boundary: Descriptive and cross-sectional association only.
* To be confirmed: Clarify whether subject scores are first-take only or include retakes; confirm official RTLE cluster labels and scaling.

### 4

* Available result(s): correlations.csv: pairwise r and p-values between CG1–CG5 and subject outcomes; regression_summaries.txt: OLS CG_only models for Subj01–Subj05 and GEN_AVE with coefficients, p-values, R²
* Statistical test/model: Pearson correlations; OLS multiple regressions (CG_only)
* Key numerical findings: correlations.csv shows one CG->subject significant correlation: CG5 vs Subj05 r = 0.2912, p = 0.00486.; In OLS CG_only models (regression_summaries.txt) CG5 has statistically significant positive coefficients for multiple outcomes: Subj01 coef = 1.6138 (p = 0.010), Subj02 coef = 1.2879 (p = 0.018), Subj03 coef = 1.4942 (p = 0.025), Subj04 coef = 1.0660 (p = 0.011), Subj05 coef = 2.4224 (p = 0.001), GEN_AVE coef = 1.5768 (p = 0.002).; CG_only model R-squared values are modest (e.g., Subj01 R² = 0.090; GEN_AVE R² = 0.139).
* Significance status: mixed
* Plain-language result: Cluster CG5 is consistently positively associated with several RTLE subject scores and overall GEN_AVE in multiple CG-only regression models and a CG5–Subj05 correlation is statistically significant. Other clustered grades showed weaker or non-significant associations in the supplied outputs.
* Interpretation boundary: Associations observed in this retrospective institutional dataset; do not infer causation.
* To be confirmed: Definition of CG5 cluster content (which courses) to support interpretation.; Multicollinearity diagnostics beyond the reported condition number (VIFs) to understand coefficient stability.

### 5

* Available result(s): correlations.csv: PBx vs Subj outcomes; regression_summaries.txt: OLS PB_only models
* Statistical test/model: Pearson correlations; OLS multiple regressions (PB_only)
* Key numerical findings: correlations.csv reports PB4 vs Subj04 r = 0.2136, p = 0.0409 (statistically significant at conventional levels).; correlations.csv also shows Preboard Mean vs GEN_AVE r = 0.2243, p = 0.0316 (statistically significant).; In PB_only OLS models, PB4 has statistically significant positive coefficients for Subj01 (coef = 0.2719, p = 0.042), Subj02 (coef = 0.2319, p = 0.048), and GEN_AVE (coef = 0.2244, p = 0.047). Other PB coefficients are generally non-significant in PB-only models.
* Significance status: mixed
* Plain-language result: Pre-board cluster PB4 shows a small-to-moderate positive association with Subj04 and contributes positively in several PB-only regression models; the pre-board overall mean correlates positively with overall GEN_AVE. Other pre-board clusters show weaker or non-significant associations in the supplied analyses.
* Interpretation boundary: Associational; needs caution due to possible measurement differences and multicollinearity in combined models.
* To be confirmed: Item-level psychometrics for pre-board instrument (reliability, item difficulties, discrimination) to assess measurement quality.; Clarify whether PB scores are percentages or raw item counts and whether they were standardized.

### 6

* Available result(s): regression_summaries.txt: Combined OLS models per subject and for GEN_AVE (CG + PB predictors); reported R-squared values for CG-only, PB-only, and Combined models
* Statistical test/model: OLS multiple regression (Combined models reported)
* Key numerical findings: Combined OLS models produce modest R-squared values (example: Subj01 Combined R² = 0.129; Subj03 Combined R² = 0.184; GEN_AVE Combined R² = 0.177).; In Combined models many individual CG and PB coefficients become non-significant despite some being significant in single-predictor-block models. Example for Subj01 Combined: CG5 coef = 1.4044 (p = 0.163); PB4 coef = 0.1996 (p = 0.177).; Regression diagnostics note large condition numbers in several Combined models (e.g., condition number = 1.14e+04 for several Combined models), indicating potential multicollinearity or numerical instability.
* Significance status: mixed
* Plain-language result: When clustered academic grades and pre-board grades are entered together, models explain a modest proportion of variation in RTLE subject scores and overall GEN_AVE; however, many individual predictors are not statistically significant in the Combined models, and multicollinearity warnings suggest caution interpreting individual coefficient significance.
* Interpretation boundary: Predictive associations within this sample only; not causal.
* To be confirmed: Collinearity diagnostics (VIF) and variable-selection or penalized regression diagnostics to address multicollinearity.; Model validation metrics (cross-validation or out-of-sample performance) beyond in-sample R².

### 7

* Available result(s): regression_summaries.txt: logistic regression outputs (CG_only, PB_only, Combined) with coefficients, p-values, pseudo R² and LLR p-values; logit_accuracies.csv: classification accuracies for CG_only, PB_only, Combined; passfail_by_batch.csv and passfail_chi2.csv
* Statistical test/model: Logistic regression models; model-level classification accuracy
* Key numerical findings: CG_only logistic model: pseudo R² = 0.1365; LLR p-value = 0.004868 (model-level), CG5 coefficient = 0.4297, p = 0.003 (statistically significant).; PB_only logistic model: pseudo R² = 0.07425; LLR p-value = 0.1035 (model-level not significant at conventional alpha); PB4 coefficient shows p = 0.072 (trend).; Combined logistic model: pseudo R² = 0.1716; LLR p-value = 0.02019 (model-level significant); individual coefficients in Combined model are generally not statistically significant at conventional alpha (example: CG5 p = 0.147).; Classification accuracies reported: CG_only = 0.7283, PB_only = 0.5761, Combined = 0.7717 (from logit_accuracies.csv).
* Significance status: mixed
* Plain-language result: Clustered academic variables (notably CG5) are associated with and contribute to logistic models of pass/fail in this dataset; a CG-only logistic model shows a significant CG5 coefficient and reasonable in-sample classification accuracy. Pre-board-only models show weaker model-level evidence; combined models improve overall model-level fit and in-sample accuracy compared with PB-only, but many individual coefficients are non-significant when both predictor blocks are included.
* Interpretation boundary: Predictive/associational within-sample results only; avoid causal claims. Accuracy metrics are in-sample; external validity not assessed.
* To be confirmed: ROC AUC values with CIs, sensitivity/specificity, confusion matrices and calibration statistics for logistic models.; Cross-validated or holdout classification performance to assess overfitting.

### 8

* Available result(s): comparison of R²/pseudo R² across CG-only, PB-only, Combined models in regression_summaries.txt and logit_accuracies.csv; per-variable coefficient significance reported
* Statistical test/model: Model fit comparisons (R²/pseudo R²) and classification accuracies
* Key numerical findings: CG-only models often explain more variation than PB-only models for several RTLE subject outcomes (examples: Subj01 CG_only R² = 0.090 vs PB_only R² = 0.081; GEN_AVE CG_only R² = 0.139 vs PB_only R² = 0.096).; Combined models increase R² modestly relative to CG-only in some outcomes (example GEN_AVE Combined R² = 0.177 vs CG_only R² = 0.139).; In logistic classification, combined model accuracy (0.7717) > CG_only (0.7283) > PB_only (0.5761).; Individually, CG5 is the most consistently statistically significant single predictor across multiple subject OLS models and the CG-only logistic model.
* Significance status: mixed
* Plain-language result: Clustered academic predictors (especially CG5) explain more variation and have stronger associations with RTLE scores and pass/fail than pre-board predictors alone in these analyses; adding pre-board predictors to academic predictors yields modest improvements in explained variance and classification accuracy in-sample, but combined-model coefficient instability and multicollinearity warrant cautious interpretation.
* Interpretation boundary: Results reflect relative explanatory power within this dataset; do not generalize without external validation.
* To be confirmed: Formal statistical tests for incremental value (e.g., nested-model LRT statistics with effect size and CIs for incremental improvement) beyond reported R²/pseudo R² and accuracy numbers.; Model comparison metrics with information criteria (AIC/BIC differences) consolidated into a table.

### 9

* Available result(s): regression_summaries.txt: CG_only vs Combined R² comparisons; logit_accuracies.csv shows CG_only and Combined accuracies; logistic-model LLR p-values reported
* Statistical test/model: Nested model comparisons (informal via R²/pseudo R² and LLR p-values) and classification accuracy comparison
* Key numerical findings: GEN_AVE: CG_only R² = 0.139; Combined R² = 0.177 (modest increase when PB included).; Subj01: CG_only R² = 0.090; Combined R² = 0.129 (increase).; Logistic models: CG_only pseudo R² = 0.1365; Combined pseudo R² = 0.1716; Combined LLR p-value = 0.02019 (model-level improvement reported).; Classification accuracy increased from CG_only 0.7283 to Combined 0.7717.
* Significance status: mixed
* Plain-language result: Adding pre-board predictors to clustered academic predictors yields modest improvements in explained variance and in-sample classification accuracy; however, individual pre-board predictors rarely reach statistical significance in Combined models and multicollinearity/instability concerns limit firm conclusions about the incremental value of specific pre-board clusters.
* Interpretation boundary: Evidence of modest incremental value in-sample; requires confirmation with validation and formal nested-model statistics (with CIs) and attention to collinearity.
* To be confirmed: Formal nested-model test statistics for each outcome with effect sizes and CIs (e.g., likelihood-ratio tests, delta-AIC/BIC presented in a consolidated table).; Cross-validated comparison of predictive performance to assess whether Combined-model improvement holds out-of-sample.

### 10

* Available result(s): anova_results.csv: ANOVA F and p-values per variable (interpreted as tests across batches), passfail_by_batch.csv, passfail_chi2.csv
* Statistical test/model: ANOVA across batches for continuous variables; contingency table chi-square for pass/fail by batch
* Key numerical findings: ANOVA results report statistically significant differences across batches for multiple variables (examples): CG1 F = 8.8375, p = 0.000316; CG2 F = 9.6699, p = 0.000158; CG3 F = 46.4003, p = 1.57e-14; CG4 F = 3.8658, p = 0.02455; CG_mean F = 5.2052, p = 0.00728.; Several pre-board clusters show extremely small p-values across batches (examples): PB2 p = 1.70e-10; PB3 p = 5.10e-15; PB4 p = 9.36e-22; PB5 p = 1.10e-39; PB_mean p = 5.05e-17.; Despite these continuous-variable differences across batches, pass/fail counts by batch do not differ statistically (chi-square p = 0.4928).
* Significance status: mixed
* Plain-language result: Clustered academic grades and pre-board cluster scores show statistically significant differences across batches for many clusters (strong p-values reported), but pass/fail rates do not show a statistically significant difference across batches in the supplied chi-square test.
* Interpretation boundary: ANOVA indicates between-batch differences in continuous scores in this dataset; pass/fail outcome differences were not significant. Do not infer causation or policy implications without further checks (e.g., measurement or cohort composition changes).
* To be confirmed: Post-hoc pairwise comparisons identifying which batches differ for each variable (Tukey or pairwise tests) are not supplied.; Contextual metadata explaining batch-level differences (e.g., curricular or assessment changes, cohort-size differences) to interpret ANOVA results.

## Overall Results Pattern

In this institutional dataset (N=92), clustered academic measures—particularly CG5—show the most consistent positive associations with RTLE subject scores and overall GEN_AVE. Some pre-board cluster scores (notably PB4 and preboard mean) show statistically significant but smaller associations with particular RTLE outcomes. Combined models (CG + PB) yield modest increases in explained variance and in-sample classification accuracy relative to single-block models, but multicollinearity/numerical-stability warnings and loss of per-variable significance in Combined models limit strong claims about which specific pre-board clusters add robust incremental predictive value. Batch-level analyses show significant differences in many continuous cluster scores across batches, but pass/fail counts by batch are not significantly different.

## Results That Are Ready to Write

- Descriptive table of clustered academic grades (CG1–CG5) and pre-board grades (PB1–PB5) with means, SDs, min/percentiles/max (summary_stats.csv).
- Table of RTLE subject means and GEN_AVE and pass/fail counts by batch (summary_stats.csv; passfail_by_batch.csv).
- Correlation table for selected CG/PB predictors vs RTLE subject outcomes (correlations.csv).
- OLS regression summary tables for CG-only, PB-only, and Combined models for Subj01–Subj05 and GEN_AVE (regression_summaries.txt) — include coefficients, standard errors, p-values, R², and model diagnostic notes as supplied.
- Logistic regression summary tables for pass/fail (CG-only, PB-only, Combined) reporting coefficients, p-values, pseudo R², and LLR p-values (regression_summaries.txt).
- Model-level classification accuracy table showing CG_only, PB_only, and Combined accuracies (logit_accuracies.csv).
- ANOVA table summarizing F and p-values across batches for CG and PB variables (anova_results.csv).
- Pass/fail chi-square table (passfail_chi2.csv).

## Results That Are Partial

- Narrative interpretation of incremental predictive value (formal nested-model test statistics with CIs and delta-AIC/BIC not consolidated).
- Calibration and ROC AUC (with confidence intervals) for logistic models (missing).
- Cross-validated or external validation performance measures for regression and classification models (missing).
- Post-hoc pairwise batch comparisons for ANOVA (missing).
- Collinearity diagnostics (VIF) and remedial analyses (e.g., PCA, penalized regression) to address condition-number warnings (missing).
- Psychometric (item-level) analyses for pre-board instruments (missing).

## Results That Are Missing

- Item-level pre-board data and psychometric analyses (item difficulty/discrimination, Cronbach's alpha).
- VIFs and other collinearity diagnostics for regression predictors.
- ROC AUC with 95% CIs and sensitivity/specificity/confusion matrices for logistic models.
- Cross-validation or holdout validation results for predictive models to assess overfitting.
- Post-hoc pairwise batch comparisons (Tukey or similar) following significant ANOVAs.
- Detailed mapping of cluster definitions (which courses belong to CG5, PB4, etc.) to support substantive interpretation.

## Statistical Claims Allowed

- CG5 is positively associated with multiple RTLE subject scores and overall GEN_AVE in CG-only OLS models (coefficients and p-values are supplied in regression_summaries.txt).
- PB4 and preboard mean show statistically significant positive associations with some RTLE outcomes in correlations and PB-only OLS models (examples: PB4 vs Subj04 correlation p = 0.0409; PB4 coefficient p-values reported in PB-only regressions).
- Combined CG+PB models explain a modestly larger share of in-sample variance for some outcomes compared with CG-only or PB-only models (R²/pseudo R² numbers supplied).
- Pass/fail logistic models show that CG-only and Combined models have higher in-sample classification accuracy than PB-only in this dataset (logit_accuracies.csv).
- ANOVA indicates statistically significant differences across batches on many continuous cluster scores (ANOVA F and p-values supplied).
- Chi-square test shows no statistically significant association between batch and pass/fail counts in this dataset (p = 0.4928).

## Statistical Claims Not Allowed

- Causal statements claiming that clustered academic grades or pre-board grades cause RTLE performance or pass/fail outcomes.
- Claims that the model guarantees who will pass or fail the RTLE.
- Statements generalizing findings beyond the studied institution/cohorts without external validation.
- Claims about pre-board instrument reliability or measurement quality without item-level psychometric evidence.

## Notes for Results Writer

- Use exact reported coefficients, p-values, R² and pseudo R² from regression_summaries.txt and avoid re-scaling or re-interpreting coefficients without the variable units.
- When describing CG5 and PB4 effects, quote the exact coefficient and p-value and explicitly state the model (CG-only, PB-only, Combined) and outcome (e.g., Subj05, GEN_AVE).
- Report sample size N = 92 explicitly in Methods/Results and indicate that all models used the same N unless otherwise noted.
- Include model diagnostic notes exactly as reported (e.g., condition number warnings) and recommend caution and follow-up analyses (VIF, PCA, penalized regression) before strong predictor-specific claims.
- When reporting ANOVA results, state that tests were performed across batches and include the ANOVA F and p-value per variable; request post-hoc comparisons if the writer wants pairwise batch differences.
- For logistic results, report model-level statistics (LLR p-value, pseudo R²) and classification accuracies, and explicitly label accuracies as in-sample.
