from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import requests


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
TRANSIENT_STATUS_CODES = {429, 500, 502, 503, 504}


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip().strip('"').strip("'")


def get_env_model(var_name: str, default: str) -> str:
    return os.getenv(var_name, default).strip() or default


def require_api_key(dry_run: bool = False) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key:
        return api_key
    if dry_run:
        return None
    raise RuntimeError("Missing OPENAI_API_KEY. Set it in the shell or in a local ignored .env file.")


def extract_output_text(response_json: dict[str, Any]) -> str:
    if response_json.get("output_text"):
        return str(response_json["output_text"])
    parts: list[str] = []
    for item in response_json.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                parts.append(str(content["text"]))
    return "\n".join(parts)


class AIClient:
    def __init__(self, api_key: str | None = None, default_model: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else require_api_key(dry_run=False)
        self.default_model = default_model

    def responses_json(
        self,
        *,
        instructions: str,
        input_data: Any,
        schema: dict[str, Any],
        schema_name: str,
        model: str | None = None,
        timeout: int = 120,
        retries: int = 2,
    ) -> dict[str, Any]:
        payload = self.build_payload(
            model=model,
            instructions=instructions,
            input_data=input_data,
            schema=schema,
            schema_name=schema_name,
        )
        response_json = self._post(payload, timeout=timeout, retries=retries)
        return dict(json.loads(extract_output_text(response_json)))

    def responses_text(
        self,
        *,
        instructions: str,
        input_text: str,
        model: str | None = None,
        timeout: int = 120,
        retries: int = 2,
    ) -> str:
        payload = self.build_payload(model=model, instructions=instructions, input_data=input_text)
        return extract_output_text(self._post(payload, timeout=timeout, retries=retries))

    def build_payload(
        self,
        *,
        model: str | None,
        instructions: str,
        input_data: Any,
        schema: dict[str, Any] | None = None,
        schema_name: str | None = None,
    ) -> dict[str, Any]:
        selected_model = model or self.default_model
        if not selected_model:
            raise ValueError("A model must be provided explicitly or as AIClient.default_model.")
        text = input_data if isinstance(input_data, str) else json.dumps(input_data, ensure_ascii=False)
        payload: dict[str, Any] = {
            "model": selected_model,
            "instructions": instructions,
            "input": [
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": text}],
                }
            ],
        }
        if schema is not None:
            payload["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": schema_name or "structured_response",
                    "schema": schema,
                    "strict": True,
                }
            }
        return payload

    def _post(self, payload: dict[str, Any], timeout: int, retries: int) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        last_error: Exception | None = None
        for attempt in range(retries + 1):
            try:
                response = requests.post(OPENAI_RESPONSES_URL, headers=headers, json=payload, timeout=timeout)
                if response.status_code in TRANSIENT_STATUS_CODES and attempt < retries:
                    time.sleep(2**attempt)
                    continue
                response.raise_for_status()
                return dict(response.json())
            except Exception as exc:
                last_error = exc
                if attempt < retries:
                    time.sleep(2**attempt)
                    continue
        raise RuntimeError(f"OpenAI Responses API request failed: {last_error}")

