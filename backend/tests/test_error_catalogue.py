"""NN-6: every error code has a severity and a message in both locales."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.errors import SEVERITY, ErrorCode, MirsadError

MESSAGES = Path(__file__).resolve().parents[2] / "frontend" / "messages"


@pytest.mark.parametrize("locale", ["ar", "en"])
def test_every_code_has_a_message(locale: str) -> None:
    messages = json.loads((MESSAGES / f"{locale}.json").read_text(encoding="utf-8"))["errors"]
    missing = [code.value for code in ErrorCode if not messages.get(code.value, "").strip()]
    assert missing == []


def test_every_code_has_a_severity() -> None:
    assert set(SEVERITY) == set(ErrorCode)


def test_error_serialises_as_code_and_context_only() -> None:
    error = MirsadError(ErrorCode.FILE_EMPTY, {"file": "x.csv"})
    assert error.to_dict() == {"error": {"code": "FILE_EMPTY", "context": {"file": "x.csv"}}}
