from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import requests

from scripts.paper_discovery.models import Paper

LOGGER = logging.getLogger(__name__)


@dataclass
class RateLimit:
    min_interval_seconds: float = 1.0
    last_request_at: float = 0.0

    def wait(self, sleeper: Any = time.sleep, clock: Any = time.monotonic) -> None:
        elapsed = clock() - self.last_request_at
        remaining = self.min_interval_seconds - elapsed
        if remaining > 0:
            sleeper(remaining)
        self.last_request_at = clock()


class BaseProvider:
    name = "base"
    timeout = 30
    retry_statuses = {429, 500, 502, 503, 504}

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        session: requests.Session | None = None,
        sleeper: Any = time.sleep,
    ) -> None:
        self.config = config or {}
        self.session = session or requests.Session()
        self.rate_limit = RateLimit(self.default_min_interval())
        self.sleeper = sleeper
        self.logger = logging.getLogger(f"{__name__}.{self.name}")

    def default_min_interval(self) -> float:
        return float(self.config.get("request_delay_seconds") or 1.0)

    def search(
        self,
        query: str,
        limit: int = 20,
        year_from: int | None = None,
        year_to: int | None = None,
        **kwargs: Any,
    ) -> list[Paper]:
        raise NotImplementedError

    def get_by_doi(self, doi: str) -> Paper | None:
        return None

    def get_by_id(self, identifier: str) -> Paper | None:
        return None

    def request_json(self, method: str, url: str, **kwargs: Any) -> Any:
        response = self.request(method, url, **kwargs)
        return response.json()

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        retries = int(self.config.get("max_retries") or 3)
        backoff = float(self.config.get("retry_backoff_seconds") or 1.0)
        last_response: requests.Response | None = None
        for attempt in range(retries + 1):
            self.rate_limit.wait(self.sleeper)
            response = self.session.request(method, url, **kwargs)
            if response.status_code not in self.retry_statuses:
                response.raise_for_status()
                return response
            last_response = response
            retry_after = response.headers.get("Retry-After")
            wait_seconds = float(retry_after) if retry_after and retry_after.isdigit() else backoff * (2**attempt)
            self.logger.info("Retryable response from %s: status=%s attempt=%s", url, response.status_code, attempt + 1)
            self.sleeper(wait_seconds)
        assert last_response is not None
        last_response.raise_for_status()
        return last_response


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def parse_int(value: Any) -> int | None:
    try:
        if value in (None, ""):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def listify(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [clean_text(v) for v in value if clean_text(v)]
    if isinstance(value, str):
        return [clean_text(part) for part in value.replace(";", ",").split(",") if clean_text(part)]
    return [clean_text(value)] if clean_text(value) else []
