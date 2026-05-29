from __future__ import annotations

import json

import pytest

from scripts.ai import client


class FakeResponse:
    def __init__(self, status_code: int, payload: dict[str, object]) -> None:
        self.status_code = status_code
        self.payload = payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self) -> dict[str, object]:
        return self.payload


def test_require_api_key_allows_dry_run_without_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert client.require_api_key(dry_run=True) is None
    with pytest.raises(RuntimeError, match="Missing OPENAI_API_KEY"):
        client.require_api_key(dry_run=False)


def test_responses_json_uses_mocked_post_and_parses_output(monkeypatch: pytest.MonkeyPatch):
    calls: list[dict[str, object]] = []

    def fake_post(url: str, headers: dict[str, str], json: dict[str, object], timeout: int) -> FakeResponse:
        calls.append({"url": url, "headers": headers, "json": json, "timeout": timeout})
        return FakeResponse(200, {"output_text": '{"records":[{"row_index":0}]}'})

    monkeypatch.setattr(client.requests, "post", fake_post)
    ai = client.AIClient(api_key="test-key", default_model="gpt-5-nano")

    parsed = ai.responses_json(
        instructions="Use only local evidence.",
        input_data={"records": [{"markdown": "local text"}]},
        schema={"type": "object", "properties": {"records": {"type": "array"}}, "required": ["records"]},
        schema_name="test_schema",
        timeout=5,
        retries=0,
    )

    assert parsed == {"records": [{"row_index": 0}]}
    payload = calls[0]["json"]
    assert isinstance(payload, dict)
    assert payload["model"] == "gpt-5-nano"
    assert payload["text"]["format"]["type"] == "json_schema"  # type: ignore[index]
    encoded = payload["input"][0]["content"][0]["text"]  # type: ignore[index]
    assert json.loads(encoded)["records"][0]["markdown"] == "local text"


def test_get_env_model_uses_default_for_missing_or_blank(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("AI_TEST_MODEL", raising=False)
    assert client.get_env_model("AI_TEST_MODEL", "gpt-5-nano") == "gpt-5-nano"
    monkeypatch.setenv("AI_TEST_MODEL", " ")
    assert client.get_env_model("AI_TEST_MODEL", "gpt-5-nano") == "gpt-5-nano"
    monkeypatch.setenv("AI_TEST_MODEL", "gpt-5-mini")
    assert client.get_env_model("AI_TEST_MODEL", "gpt-5-nano") == "gpt-5-mini"

