# Prompt QC Report

## Overall Assessment
The prompt chain is usable for the local file-based workflow after the repair pass. The critical path from agent 00 through agent 16 is now mostly aligned: earlier outputs are named consistently in later prompts, stale filenames from the first QC pass have been removed from active prompts, and the RadTech board exam prediction focus is preserved where relevant.

The workflow still needs minor-to-major refinement before it is fully robust. The main remaining risks are not broken filenames, but workflow completeness and operational safeguards: there is no dedicated Methodology drafting step even though final assembly expects a Methodology section, some audit/final-stage prompts need clearer missing-input behavior, CSV escaping rules are not standardized, and final assembly may include incomplete references from `references_apa7.md` unless instructed otherwise.

## Workflow Map
1. `00_research_brief_agent.md` reads `input/study_notes.md` and creates the brief package in `00_brief/`.
2. `01_literature_search_agent.md` reads `00_brief/` and creates search planning files in `01_literature_search/`.
3. `02_source_collection_agent.md` reads the brief and search outputs, then creates source collection files in `02_sources/`.
4. `03_document_ingestion_agent.md` reads included sources and local source files, then creates raw/cleaned markdown and ingestion records in `03_markdown/`.
5. `04_citation_metadata_agent.md` reads included sources and cleaned markdown, then creates references and metadata files in `04_metadata/`.
6. `05_evidence_extraction_agent.md` reads the brief, cleaned markdown, and metadata, then creates evidence tables and paper summaries in `05_evidence_extraction/`.
7. `06_synthesis_matrix_agent.md` reads extracted evidence and creates synthesis files in `06_synthesis/`.
8. `07_gap_analysis_agent.md` reads the brief and synthesis files, then creates gap analysis files in `07_gap_analysis/`.
9. `08_outline_agent.md` reads the brief, synthesis, and gap files, then creates outline files in `08_outline/`.
10. `09_intro_rrl_writer_agent.md` reads current outline, synthesis, gap, and metadata files, then drafts Introduction and RRL files in `09_drafts/`.
11. `10_results_interpreter_agent.md` reads statistical results, raw tables, variables, and results outlines, then creates results interpretation notes in `09_drafts/results/`.
12. `11_results_writer_agent.md` reads verified results and results notes, then creates Results draft files in `09_drafts/results/`.
13. `12_discussion_writer_agent.md` reads Results outputs, synthesis, gap, outline, and metadata files, then creates Discussion-related drafts in `09_drafts/discussion/`.
14. `13_citation_audit_agent.md` reads drafts, metadata, evidence, and synthesis files, then creates citation audit files in `10_audit/citations/`.
15. `14_claim_audit_agent.md` reads drafts, evidence, synthesis, and statistical results, then creates claim audit files in `10_audit/claims/`.
16. `15_style_formatting_agent.md` reads drafts and audits, then creates style and formatting reports in `11_final/`.
17. `16_final_assembly_agent.md` reads drafts, APA references, audits, and style report, then creates the editable full manuscript draft and final revision notes in `11_final/`.

## Cross-Agent Dependency Check
| Agent | Inputs It Expects | Outputs It Creates | Later Agents That Depend on Outputs | Mismatch Found |
|---|---|---|---|---|
| 00 Research Brief | `input/study_notes.md` | `research_brief.md`, `research_questions.md`, `variables.md`, `inclusion_exclusion_criteria.md`, `search_keywords.md`, `source_strategy.md`, `writing_scope.md`, `agent_instructions.md` | 01, 02, 05, 06, 07, 08, 09, 10, 11 | No filename mismatch. |
| 01 Literature Search | `00_brief/` | `literature_search_plan.md`, `search_queries.md`, `candidate_papers.csv`, `search_log.md` | 02 | No filename mismatch. |
| 02 Source Collection | `00_brief/`, `search_queries.md`, `candidate_papers.csv`, `search_log.md`, source folders | `source_collection_plan.md`, `included_sources.csv`, `excluded_sources.csv`, `download_queue.csv`, `source_notes.md` | 03, 04 | No filename mismatch. |
| 03 Document Ingestion | `included_sources.csv`, `pdf/`, `html/`, `other/` | `raw_md/`, `cleaned_md/`, `ingestion_manifest.csv`, `ingestion_log.md` | 04, 05 | No filename mismatch. |
| 04 Citation Metadata | `included_sources.csv`, `cleaned_md/`, `ingestion_manifest.csv` | `references.bib`, `references_apa7.md`, `metadata_table.csv`, `citation_key_map.csv`, `metadata_issues.md` | 05, 09, 12, 13, 16 | Mostly aligned; final assembly needs clearer handling of incomplete references under `## Metadata To Confirm`. |
| 05 Evidence Extraction | `00_brief/`, `cleaned_md/`, `metadata_table.csv`, `citation_key_map.csv` | `evidence_table.csv`, `paper_summaries/`, `extraction_log.md` | 06, 13, 14 | No filename mismatch. |
| 06 Synthesis Matrix | `00_brief/`, `evidence_table.csv`, `paper_summaries/` | `synthesis_matrix.csv`, `theme_matrix.md`, `literature_map.md`, `synthesis_notes.md` | 07, 08, 09, 12, 13, 14 | No filename mismatch. |
| 07 Gap Analysis | `00_brief/`, `06_synthesis/` | `research_gap_analysis.md`, `study_contribution.md`, `problem_statement_refined.md` | 08, 09, 12 | No filename mismatch. |
| 08 Outline | `00_brief/`, `06_synthesis/`, `07_gap_analysis/` | `manuscript_outline.md`, `introduction_outline.md`, `rrl_outline.md`, `results_outline.md`, `discussion_outline.md` | 09, 10, 11, 12, 16 | No filename mismatch; no dedicated methodology outline or methodology draft path. |
| 09 Intro/RRL Writer | Current brief, outline, synthesis, gap, and metadata files | `introduction_draft.md`, `rrl_draft.md`, `rrl_citation_notes.md` | 13, 14, 15, 16 | No filename mismatch. |
| 10 Results Interpreter | `statistical_results.md`, `raw_tables/`, variables, `results_outline.md`, `manuscript_outline.md` | `results_interpretation_notes.md`, `results_table_notes.md`, `missing_results_to_confirm.md` | 11, 12, 14, 16 | No filename mismatch. |
| 11 Results Writer | `statistical_results.md`, `raw_tables/`, `results_outline.md`, results notes, research questions | `results_draft.md`, `results_tables_draft.md`, `results_queries.md` | 12, 13, 14, 15, 16 | Output folder creation behavior is less explicit than other prompts. |
| 12 Discussion Writer | Results draft/notes, `discussion_outline.md`, synthesis, gap, metadata | `discussion_draft.md`, `conclusion_recommendations_notes.md`, `limitations_notes.md` | 13, 14, 15, 16 | No filename mismatch. |
| 13 Citation Audit | `09_drafts/`, `04_metadata/`, `05_evidence_extraction/`, `06_synthesis/` | `citation_audit.md`, `unsupported_citations.csv`, `missing_citations.csv` | 15, 16 | Needs clearer behavior if drafts or metadata are missing. |
| 14 Claim Audit | `09_drafts/`, `05_evidence_extraction/`, `06_synthesis/`, `statistical_results.md` | `claim_audit.md`, `claim_table.csv` | 15, 16 | Needs clearer behavior if drafts are missing. |
| 15 Style Formatting | `09_drafts/`, `10_audit/` | `style_report.md`, `formatting_checklist.md` | 16 | Needs clearer behavior if audits are missing. |
| 16 Final Assembly | `09_drafts/`, `references_apa7.md`, `10_audit/`, `style_report.md` | `full_manuscript_draft.md`, `final_revision_notes.md` | Final review | Needs clearer exclusion of non-final references and missing-style-report behavior. |

## Issues Found
### ISSUE-001
- Severity: Major
- Prompt file affected: `08_outline_agent.md`, `16_final_assembly_agent.md`
- Problem: The workflow plans and assembles a Methodology section, but there is no dedicated Methodology Writer Agent or standard Methodology draft file.
- Why it matters: Final assembly may produce a manuscript with a placeholder Methodology section even if the workflow is otherwise complete.
- Recommended fix: Either add a dedicated Methodology Writer Agent and output path such as `projects/sample_project/09_drafts/methodology/methodology_draft.md`, or explicitly define Methodology as manually drafted outside this agent chain.

### ISSUE-002
- Severity: Major
- Prompt file affected: `16_final_assembly_agent.md`
- Problem: `references_apa7.md` may contain a `## Metadata To Confirm` section with incomplete, not-final-ready references, but final assembly says to copy references from `references_apa7.md`.
- Why it matters: Incomplete or provisional references could be included in the assembled manuscript reference list.
- Recommended fix: Instruct final assembly to include only references outside `## Metadata To Confirm`, and list incomplete references in `final_revision_notes.md` instead of the manuscript References section.

### ISSUE-003
- Severity: Major
- Prompt file affected: `13_citation_audit_agent.md`, `14_claim_audit_agent.md`, `15_style_formatting_agent.md`
- Problem: These audit-stage prompts do not fully specify fallback behavior when no draft files exist.
- Why it matters: If run early, the agents may create ambiguous reports rather than clear blocked/template outputs.
- Recommended fix: Add explicit fallback instructions: if no draft files exist, create output files stating the audit is blocked until drafts are available.

### ISSUE-004
- Severity: Major
- Prompt file affected: `16_final_assembly_agent.md`
- Problem: The final assembly prompt depends on `style_report.md`, but does not explicitly say what to do if style reporting has not been run.
- Why it matters: Final assembly may proceed without the style-readiness gate.
- Recommended fix: Add missing-input behavior: if `style_report.md` is missing, assemble only a provisional draft and flag style review as a blocker in `final_revision_notes.md`.

### ISSUE-005
- Severity: Minor
- Prompt file affected: `11_results_writer_agent.md`
- Problem: Unlike nearby prompts, it does not explicitly say to create the output folder if it does not exist.
- Why it matters: A run may fail when `projects/sample_project/09_drafts/results/` has not already been created.
- Recommended fix: Add "Create the output folder if it does not exist."

### ISSUE-006
- Severity: Minor
- Prompt file affected: `05_evidence_extraction_agent.md`
- Problem: Anti-hallucination wording repeats "findings" in the same sentence.
- Why it matters: This is harmless but slightly unpolished.
- Recommended fix: Remove the duplicate word.

### ISSUE-007
- Severity: Minor
- Prompt file affected: `04_citation_metadata_agent.md`
- Problem: It allows partial references in `citation_key_map.csv`, while writer prompts allow citation keys from `citation_key_map.csv`.
- Why it matters: A writer could cite a not-final-ready source unless `metadata_status` is checked.
- Recommended fix: In writer prompts, require citation keys to have a final-ready or verified metadata status, or require not-final-ready citations to be marked `To be confirmed.`

### ISSUE-008
- Severity: Minor
- Prompt file affected: `01_literature_search_agent.md`
- Problem: The anti-hallucination rules prohibit fake papers, DOIs, citations, URLs, hit counts, and findings, but do not explicitly mention statistics.
- Why it matters: Consistency rule asks prompts to prohibit invented statistics where relevant.
- Recommended fix: Add "statistics" to the no-invention list.

### ISSUE-009
- Severity: Suggestion
- Prompt file affected: All CSV-producing prompts
- Problem: CSV escaping rules are not standardized.
- Why it matters: Fields such as titles, APA references, claims, and notes may contain commas, quotation marks, or line breaks.
- Recommended fix: Add a shared CSV rule: quote fields containing commas, quotes, or line breaks, and escape internal quotes by doubling them.

### ISSUE-010
- Severity: Suggestion
- Prompt file affected: All prompts
- Problem: Prompts hard-code `projects/sample_project/`.
- Why it matters: Reusing the workflow for future projects requires manual path edits across all prompts.
- Recommended fix: Introduce a project variable convention such as `{PROJECT_DIR}`, with `projects/sample_project/` as the default example.

### ISSUE-011
- Severity: Suggestion
- Prompt file affected: `13_citation_audit_agent.md`, `14_claim_audit_agent.md`
- Problem: The boundary between citation-source fit and claim-support classification is improved but still has some overlap.
- Why it matters: Some duplicated findings may appear in citation and claim audit outputs.
- Recommended fix: Add a short coordination note: citation audit should record citation-source fit, while claim audit is authoritative for final claim support classification.

## Missing Safeguards
- Final assembly should exclude not-final-ready references from the manuscript References section.
- Audit agents should explicitly block or template their reports when drafts are absent.
- Writer prompts should account for `metadata_status` before using citation keys from `citation_key_map.csv`.
- CSV-producing prompts should standardize escaping rules.
- A standard Methodology drafting path is missing.
- Results and final assembly prompts should consistently treat missing prerequisite files as blockers or provisional states.

## Naming and Path Consistency
The main file naming contract is now consistent across active agent prompts. The previous obsolete references to these filenames were not found in active prompts:
- `synthesis_matrix.md`
- `theme_summary.md`
- `research_gap.md`
- `apa_references_draft.md`
- `tables_and_figures_plan.md`
- `source_metadata.csv`
- `evidence_table.md`
- `citation_audit_report.md`
- `claim_audit_report.md`
- `style_formatting_report.md`
- `manuscript_full_draft.md`

The remaining naming issue is not a mismatch, but an omission: no standard `methodology_draft.md` or Methodology Writer Agent exists.

## Recommended Standard File Contract
| Folder | Standard Contents |
|---|---|
| `projects/sample_project/input/` | `study_notes.md`, `statistical_results.md`, `raw_tables/` |
| `projects/sample_project/00_brief/` | `research_brief.md`, `research_questions.md`, `variables.md`, `inclusion_exclusion_criteria.md`, `search_keywords.md`, `source_strategy.md`, `writing_scope.md`, `agent_instructions.md` |
| `projects/sample_project/01_literature_search/` | `literature_search_plan.md`, `search_queries.md`, `candidate_papers.csv`, `search_log.md` |
| `projects/sample_project/02_sources/` | `source_collection_plan.md`, `included_sources.csv`, `excluded_sources.csv`, `download_queue.csv`, `source_notes.md`, `pdf/`, `html/`, `other/` |
| `projects/sample_project/03_markdown/` | `raw_md/`, `cleaned_md/`, `ingestion_manifest.csv`, `ingestion_log.md` |
| `projects/sample_project/04_metadata/` | `references.bib`, `references_apa7.md`, `metadata_table.csv`, `citation_key_map.csv`, `metadata_issues.md` |
| `projects/sample_project/05_evidence_extraction/` | `evidence_table.csv`, `paper_summaries/`, `extraction_log.md` |
| `projects/sample_project/06_synthesis/` | `synthesis_matrix.csv`, `theme_matrix.md`, `literature_map.md`, `synthesis_notes.md` |
| `projects/sample_project/07_gap_analysis/` | `research_gap_analysis.md`, `study_contribution.md`, `problem_statement_refined.md` |
| `projects/sample_project/08_outline/` | `manuscript_outline.md`, `introduction_outline.md`, `rrl_outline.md`, `results_outline.md`, `discussion_outline.md` |
| `projects/sample_project/09_drafts/introduction/` | `introduction_draft.md` |
| `projects/sample_project/09_drafts/rrl/` | `rrl_draft.md`, `rrl_citation_notes.md` |
| `projects/sample_project/09_drafts/results/` | `results_interpretation_notes.md`, `results_table_notes.md`, `missing_results_to_confirm.md`, `results_draft.md`, `results_tables_draft.md`, `results_queries.md` |
| `projects/sample_project/09_drafts/discussion/` | `discussion_draft.md`, `conclusion_recommendations_notes.md`, `limitations_notes.md` |
| `projects/sample_project/09_drafts/methodology/` | Recommended addition: `methodology_draft.md` |
| `projects/sample_project/10_audit/citations/` | `citation_audit.md`, `unsupported_citations.csv`, `missing_citations.csv` |
| `projects/sample_project/10_audit/claims/` | `claim_audit.md`, `claim_table.csv` |
| `projects/sample_project/11_final/` | `style_report.md`, `formatting_checklist.md`, `full_manuscript_draft.md`, `final_revision_notes.md` |

## Ready-to-Run Verdict
The workflow is ready to run agent-by-agent through literature planning, source preparation, ingestion, metadata, evidence extraction, synthesis, gap analysis, outlining, and the existing draft agents.

Before relying on final assembly for a complete manuscript, revise the remaining issues around Methodology drafting, incomplete reference handling, and missing audit/style prerequisites. These are not current filename-breakers, but they are likely failure points in an end-to-end academic manuscript workflow.
