from pathlib import Path
import re

PROJECT_DIR = Path("projects/sample_project")
INPUT_FILE = PROJECT_DIR / "input" / "study_notes.md"
OUTPUT_DIR = PROJECT_DIR / "00_brief"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Missing input file: {INPUT_FILE}")

study_notes = INPUT_FILE.read_text(encoding="utf-8")

MASTER_PROMPT = f"""
You are a Research Brief Agent for an academic writing workflow.

Your task is to transform rough study notes into structured planning documents that will guide literature search, paper screening, evidence extraction, synthesis, writing, and citation auditing.

You must produce the following files:

1. research_brief.md
2. research_questions.md
3. variables.md
4. inclusion_exclusion_criteria.md
5. search_keywords.md
6. source_strategy.md
7. writing_scope.md
8. agent_instructions.md

Rules:
- Do not write the full manuscript yet.
- Do not invent specific statistical findings unless provided.
- If information is missing, mark it as "To be confirmed."
- Keep the scope narrow and researchable.
- Generate useful search keywords and Boolean search strings.
- Identify likely themes for the Review of Related Literature.
- Use clear academic language.
- Use APA 7th edition unless another style is specified.
- Prioritize open-access literature sources.
- Make the outputs useful for downstream agents.

Return your response using this exact format:

===== research_brief.md =====
[content]

===== research_questions.md =====
[content]

===== variables.md =====
[content]

===== inclusion_exclusion_criteria.md =====
[content]

===== search_keywords.md =====
[content]

===== source_strategy.md =====
[content]

===== writing_scope.md =====
[content]

===== agent_instructions.md =====
[content]

Here are the study notes:

{study_notes}
"""

PROMPT_FILE = OUTPUT_DIR / "_prompt_for_ai.md"
PROMPT_FILE.write_text(MASTER_PROMPT, encoding="utf-8")

print("Research Brief Agent v1")
print("-----------------------")
print(f"Input read from: {INPUT_FILE}")
print(f"Prompt written to: {PROMPT_FILE}")
print()
print("Next step:")
print("1. Open the file _prompt_for_ai.md")
print("2. Paste it into ChatGPT/Codex")
print("3. Copy the AI response")
print("4. Save it as projects/sample_project/00_brief/_ai_response.md")