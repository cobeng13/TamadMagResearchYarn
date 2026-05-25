# Prompt Repair Log

## Files Edited
- `agents/prompts/01_literature_search_agent.md`
- `agents/prompts/02_source_collection_agent.md`
- `agents/prompts/03_document_ingestion_agent.md`
- `agents/prompts/04_citation_metadata_agent.md`
- `agents/prompts/05_evidence_extraction_agent.md`
- `agents/prompts/06_synthesis_matrix_agent.md`
- `agents/prompts/08_outline_agent.md`
- `agents/prompts/09_intro_rrl_writer_agent.md`
- `agents/prompts/11_results_writer_agent.md`
- `agents/prompts/12_discussion_writer_agent.md`
- `agents/prompts/13_citation_audit_agent.md`
- `agents/prompts/14_claim_audit_agent.md`
- `agents/prompts/15_style_formatting_agent.md`
- `agents/prompts/16_final_assembly_agent.md`

## Issues Fixed
- `ISSUE-001` fixed: `08_outline_agent.md` now creates `methodology_outline.md` and defines the standard manual methodology draft path as `projects/sample_project/09_drafts/methodology/methodology_draft.md`. `16_final_assembly_agent.md` now reads that methodology draft if present and otherwise flags the Methodology section as `To be confirmed.`
- `ISSUE-002` fixed: `16_final_assembly_agent.md` now includes only final-ready references from `references_apa7.md` and excludes references under `## Metadata To Confirm` from the manuscript References section.
- `ISSUE-003` fixed: `13_citation_audit_agent.md`, `14_claim_audit_agent.md`, and `15_style_formatting_agent.md` now create blocked/template outputs when required draft files are missing.
- `ISSUE-004` fixed: `16_final_assembly_agent.md` now treats a missing `style_report.md` as a provisional-assembly blocker and records it in `final_revision_notes.md`.
- `ISSUE-005` fixed: `11_results_writer_agent.md` now tells the agent to create the results output folder if it does not exist.
- `ISSUE-006` fixed: duplicate wording in `05_evidence_extraction_agent.md` anti-hallucination rules was removed.
- `ISSUE-007` fixed: `09_intro_rrl_writer_agent.md` and `12_discussion_writer_agent.md` now require citation keys to have verified or final-ready metadata status; incomplete/not-final-ready sources must be marked `To be confirmed.`
- `ISSUE-008` fixed: `01_literature_search_agent.md` now explicitly prohibits invented statistics.
- `ISSUE-009` fixed for current CSV-producing prompts: CSV escaping rules were added to source collection, citation metadata, evidence extraction, synthesis matrix, citation audit, and claim audit prompts.
- `ISSUE-011` fixed: citation audit and claim audit now include coordination notes clarifying that citation audit handles citation-source fit while claim audit is authoritative for final claim support classification.

## Additional Consistency Repairs
- Strengthened anti-hallucination language in multiple prompts to explicitly prohibit inventing sources, citations, statistics, DOIs, URLs, and findings.
- Standardized Methodology handling without creating manuscript content or modifying project output folders.
- Preserved local file-based behavior and RadTech board exam prediction alignment.

## Issues Not Fixed
- `ISSUE-010` not fixed: prompts still use the concrete path `projects/sample_project/` rather than a `{PROJECT_DIR}` variable. This was left unchanged because the current project structure and user instructions consistently target `projects/sample_project/`. Introducing `{PROJECT_DIR}` should be handled as a dedicated future convention change across all prompts and README documentation.

## Recommended Manual Review Items
- Decide whether to add a dedicated Methodology Writer Agent in a future workflow expansion.
- Run another Prompt QC pass to confirm the current issue table is resolved or reduced to suggestions.
- If the workflow will be reused across many projects, introduce a `{PROJECT_DIR}` prompt variable and update all prompts consistently.
