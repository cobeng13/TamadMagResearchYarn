# Missing Results To Confirm

Generated: 2026-05-30 00:54:10
Model: gpt-5-mini

## Required Before Results Drafting

- Specification of cluster definitions (courses included in CG1–CG5 and PB1–PB5) for substantive interpretation.
- Clarify PB score scaling and whether PB scores represent percentages or raw counts.
- Confirm whether RTLE subject and overall scores are first-take only or include retakes.

## Required Before Discussion Drafting

- Item-level psychometric analysis of pre-board instruments (item difficulties, discrimination, reliability).
- Multicollinearity diagnostics (VIF) and remedial model runs (e.g., models using principal components or penalized regression) to verify robustness of predictor effects.
- Post-hoc pairwise ANOVA comparisons to identify which batches differ for each significant variable.

## Missing by Objective

- Objective 2: item-level pre-board psychometrics missing.
- Objective 6/9: formal nested-model test statistics with CIs and cross-validated predictive performance missing.
- Objective 7: ROC AUC with CIs, sensitivity/specificity, calibration metrics missing.
- Objective 10: post-hoc pairwise ANOVA results missing.

## Missing Tables/Figures

- ROC curves and AUC CIs for logistic models.
- Post-hoc multiple comparison table for ANOVA across batches.
- Collinearity diagnostics table (VIF) for regression predictors.
- Item-level psychometric table for pre-board instrument.

## Missing Statistical Details

- Method used for correlation coefficient calculation (Pearson vs Spearman) is not explicitly stated in correlations.csv.
- Exact coding of PassBinary in logistic models (which value = pass?) — assume PassBinary denotes pass = 1 but confirm.
- Information on whether continuous predictors were mean-centered or standardized prior to regression (not indicated).
- Residual diagnostics plots and normality tests beyond omnibus/Jarque-Bera numbers for OLS residuals are not supplied.

## Human/Statistician Follow-up Questions

- Please provide the mapping/list of courses that define each CG cluster and PB cluster (CG1–CG5, PB1–PB5).
- Confirm the measurement scale and units for PB variables (percentage, raw score, or other) and whether PB scores were transformed or standardized prior to modeling.
- Provide raw individual-level analytic dataset or predicted probabilities and labels for logistic models to compute ROC/AUC, confusion matrices, and cross-validated performance.
- Do you want formal VIFs and a remediation plan (PCA, ridge/LASSO) to address the large condition numbers noted in Combined models?
- Should post-hoc pairwise batch comparisons (Tukey HSD) be added for ANOVA-significant variables?
