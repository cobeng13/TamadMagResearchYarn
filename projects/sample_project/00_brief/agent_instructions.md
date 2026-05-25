# Agent Instructions for Downstream Academic Writing Workflow

## General Instructions
- Use the planning documents as the controlling scope for literature search, screening, extraction, synthesis, manuscript drafting, and citation auditing.
- Do not write beyond the study scope unless the user provides additional approved objectives.
- Use APA 7th edition for in-text citations and references.
- Prioritize open-access sources and Philippine-based literature.
- Use allied health literature only as supporting evidence when Radiologic Technology-specific evidence is limited.
- Mark missing information as "To be confirmed."
- Do not invent statistical findings, sample characteristics, p-values, coefficients, effect sizes, or conclusions.

## Literature Search Agent
- Use the Boolean strings in `search_keywords.md`.
- Search Google Scholar, PubMed, ERIC, DOAJ, Philippine E-Journals, HERDIN Plus, institutional repositories, PRC, and CHED sources.
- Save search metadata: database, search string, date searched, number of hits, and filters used.
- Prioritize full-text, open-access, peer-reviewed, and Philippine sources.
- Separate Radiologic Technology sources from allied health supporting sources.

## Screening Agent
- Apply the source inclusion and exclusion criteria.
- Include sources that address predictors of licensure performance, academic performance, pre-board examinations, internship or clinical performance, comprehensive examinations, or related readiness indicators.
- Exclude sources that are not relevant to licensure, academic prediction, health professions education, or assessment.
- Record reasons for exclusion at full-text screening.

## Evidence Extraction Agent
Extract the following fields from each included source:
- Full APA 7th citation
- Country and setting
- Discipline or program
- Study design
- Sample size and population
- Predictor variables
- Outcome variables
- Statistical methods
- Key findings, without overstating results
- Relevance to the current study
- Limitations
- Open-access URL or DOI

## Synthesis Agent
- Organize the Review of Related Literature by themes, not by article summaries alone.
- Prioritize Radiologic Technology evidence first.
- Use allied health studies to support broader patterns in licensure prediction.
- Clearly distinguish findings on academic grades, internship or clinical performance, pre-board or mock board results, and comprehensive or terminal competency assessments.
- Identify agreements, contradictions, and evidence gaps.
- Avoid claiming that pre-board examinations predict licensure success unless the cited evidence supports that claim.

## Methodology Drafting Agent
- Write the methodology as a retrospective descriptive-correlational and predictive study.
- Include operational definitions from `variables.md`.
- Confirm grading scale, sample size, cohort years, institution, and available variables before finalizing.
- Specify statistical tests only when they match the data structure.
- Include ethical handling of academic and licensure records.

## Results Drafting Agent
- Use only verified results supplied by the user or extracted from the dataset.
- Use placeholders such as "To be confirmed" for missing numerical values.
- Do not create tables with invented data.
- Ensure that the text interpretation matches the tables and statistical outputs.

## Discussion Drafting Agent
- Interpret findings in light of the literature review.
- Maintain the distinction between correlation, prediction, and causation.
- Discuss practical implications for student advising, remediation, curriculum review, and licensure preparation.
- Note limitations related to retrospective design, institutional scope, sample size, missing data, and generalizability.

## Citation Audit Agent
- Check every in-text citation against the reference list.
- Check every reference list entry against in-text citations.
- Verify author names, publication years, article titles, journal titles, volume, issue, pages, DOI, and URLs.
- Ensure APA 7th edition formatting.
- Flag unverifiable, incomplete, or possibly fabricated references for correction.

## Final Quality Checks
- The manuscript must remain focused on academic performance, pre-board examination results, and licensure success.
- All claims must be supported by data or cited literature.
- Missing details must remain marked as To be confirmed until verified.
- The final paper should not overgeneralize beyond the sampled graduates and institutional context.
