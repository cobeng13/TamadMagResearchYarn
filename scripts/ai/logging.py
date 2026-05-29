from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any


def _path_lines(label: str, paths: list[str | Path]) -> list[str]:
    lines = [f"{label}:"]
    if not paths:
        return lines + ["- none"]
    return lines + [f"- {Path(path)}" for path in paths]


def write_ai_run_log(
    log_path: str | Path,
    task_name: str,
    model: str,
    input_paths: list[str | Path],
    output_paths: list[str | Path],
    counts: dict[str, Any],
    errors: list[str] | None = None,
    prompt_version: str | None = None,
) -> None:
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# AI Run Log - {task_name}",
        "",
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Task: {task_name}",
        f"Model: {model}",
        f"Prompt: {prompt_version or 'unspecified'}",
        "",
        *_path_lines("Input paths", input_paths),
        "",
        *_path_lines("Output paths", output_paths),
        "",
        "Counts:",
    ]
    for key, value in counts.items():
        lines.append(f"- {key}: {value}")
    if errors:
        lines.extend(["", "Errors:"])
        lines.extend(f"- {str(error)[:500]}" for error in errors)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
