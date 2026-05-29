# Results Table Notes

Generated: 2026-05-30 00:54:10
Model: gpt-5-mini

## Recommended Tables

### Table 1. Table 1 — Participant and score descriptors (N, means, SDs, min/25/50/75/max) for CG1–CG5, PB1–PB5, Subj01–Subj05, GEN_AVE

Purpose:
Provide baseline descriptive statistics for all predictors and outcomes.

Source result files:
- summary_stats.csv

Required columns:
- Variable
- N
- Mean
- SD
- Min
- 25%
- 50%
- 75%
- Max

Available:
- All required descriptive fields are present in summary_stats.csv.

Missing:
- To be confirmed.

Notes:
Include N = 92 and clarify units/scaling for PB variables.

### Table 2. Table 2 — Pairwise correlations between clustered academic/pre-board variables and RTLE subject outcomes

Purpose:
Summarize bivariate associations and p-values to address RQ4–RQ5.

Source result files:
- correlations.csv

Required columns:
- Cluster/Variable
- Outcome
- r
- p_value

Available:
- correlations.csv provides r and p_value for listed pairs.

Missing:
- To be confirmed.

Notes:
Report which correlation method used (file indicates r but not explicit Pearson/Spearman—assume Pearson only if confirmed by analyst).

### Table 3. Table 3 — OLS regression summaries for each outcome: CG-only, PB-only, Combined

Purpose:
Report coefficients, SEs, p-values, R²/Adj R², model diagnostics for Subj01–Subj05 and GEN_AVE.

Source result files:
- regression_summaries.txt

Required columns:
- Outcome
- Model
- Predictor
- coef
- std err
- t or z
- p-value
- 95% CI
- R-squared / Adj. R-squared
- Model diagnostics (No. Observations, condition number)

Available:
- Coefficients, standard errors, t-statistics, p-values, 95% CI, R², and condition-number notes are present in regression_summaries.txt.

Missing:
- VIFs and formal collinearity diagnostics.

Notes:
When placing Combined model results, include condition-number warnings and recommend caution.

### Table 4. Table 4 — Logistic regression summaries for pass/fail (CG-only, PB-only, Combined) and model-level classification accuracy

Purpose:
Present coefficients, p-values, pseudo R², LLR p-values, and reported in-sample accuracies.

Source result files:
- regression_summaries.txt
- logit_accuracies.csv

Required columns:
- Model
- Predictor
- coef
- std err
- z
- p-value
- Pseudo R²
- LLR p-value
- In-sample accuracy

Available:
- Logit coefficients, standard errors, z-statistics, p-values, pseudo R², LLR p-values in regression_summaries.txt; accuracies in logit_accuracies.csv.

Missing:
- ROC AUC and CIs, confusion matrices, sensitivity/specificity, calibration metrics.

Notes:
Label accuracies as in-sample and request ROC/AUC calculations for final draft.

### Table 5. Table 5 — Batch comparisons: ANOVA F and p-values for CG and PB variables; pass/fail counts and chi-square test

Purpose:
Document which continuous variables differ across batches and whether pass/fail rates differ by batch.

Source result files:
- anova_results.csv
- passfail_by_batch.csv
- passfail_chi2.csv

Required columns:
- Variable
- F
- p_value
- PassCount_by_batch
- FailCount_by_batch
- Chi2
- Chi2_p_value

Available:
- ANOVA F and p-values in anova_results.csv, pass/fail counts by batch in passfail_by_batch.csv, chi-square result in passfail_chi2.csv.

Missing:
- Post-hoc pairwise comparisons identifying specific batch differences per variable.

Notes:
Recommend adding post-hoc tests (Tukey) if pairwise batch interpretation is required.

## Recommended Figures

### Figure 1. Figure 1 — Density/histogram plots of CG1–CG5 and PB1–PB5 distributions

Purpose: Visualize score distributions and spread across clusters to support descriptive statements.

### Figure 2. Figure 2 — Scatterplots of CG5 vs Subj05 (and regression line) and PB4 vs Subj04

Purpose: Illustrate the strongest observed bivariate associations (CG5–Subj05, PB4–Subj04) seen in correlations/OLS outputs.

### Figure 3. Figure 3 — ROC curves for logistic models (CG-only, PB-only, Combined)

Purpose: Compare classification performance and calibration for pass/fail prediction.

### Figure 4. Figure 4 — Bar chart of pass/fail counts by batch

Purpose: Visualize pass/fail distribution across batches alongside chi-square result.

## Tables/Figures Not Yet Ready

- Item-level pre-board data and psychometric analyses (item difficulty/discrimination, Cronbach's alpha).
- VIFs and other collinearity diagnostics for regression predictors.
- ROC AUC with 95% CIs and sensitivity/specificity/confusion matrices for logistic models.
- Cross-validation or holdout validation results for predictive models to assess overfitting.
- Post-hoc pairwise batch comparisons (Tukey or similar) following significant ANOVAs.
- Detailed mapping of cluster definitions (which courses belong to CG5, PB4, etc.) to support substantive interpretation.

## Formatting Notes

- Do not create final tables unless all values are supplied.
- Do not invent table values.
