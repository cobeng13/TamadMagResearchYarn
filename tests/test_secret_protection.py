from __future__ import annotations

from pathlib import Path


def test_gitignore_protects_local_secret_files():
    ignored = set(Path(".gitignore").read_text(encoding="utf-8").splitlines())
    for pattern in [
        "scripts/paper_discovery/config.yaml",
        ".env",
        ".env.local",
        "*.key",
        "*.pem",
    ]:
        assert pattern in ignored

