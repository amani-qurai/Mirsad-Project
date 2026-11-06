#!/usr/bin/env python3
"""Fail if ar.json and en.json do not carry exactly the same keys.

Non-negotiable 1: every user-visible string goes through t(), with keys in
ar.json AND en.json, added together in the same commit.

A key added to en.json alone does not fail visibly in English, so it ships.
It fails in Arabic -- the locale the client's accountant actually uses. This
check turns that from a habit into a build gate.

Usage:
    python scripts/check_locale_parity.py
    python scripts/check_locale_parity.py path/to/messages

Exit codes:
    0  locales agree (or the locale files do not exist yet)
    1  keys differ, or a value is empty
    2  a file could not be read or parsed
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

LOCALES = ("ar", "en")
DEFAULT_SEARCH_DIRS = (
    "frontend/messages",
    "frontend/src/messages",
    "frontend/locales",
    "messages",
)


def flatten(obj: object, prefix: str = "") -> dict[str, object]:
    """Flatten nested message objects into dotted keys.

    Only dicts are traversed. A list is a leaf: ICU messages are strings, and
    an array of strings is a single translatable unit, not a set of keys.
    """
    flat: dict[str, object] = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(value, dict):
                flat.update(flatten(value, path))
            else:
                flat[path] = value
    else:
        flat[prefix] = obj
    return flat


def find_messages_dir(explicit: str | None) -> Path | None:
    """Locate the directory holding the locale files."""
    if explicit:
        candidate = Path(explicit)
        return candidate if candidate.is_dir() else None

    for relative in DEFAULT_SEARCH_DIRS:
        candidate = Path(relative)
        if candidate.is_dir() and any(
            (candidate / f"{locale}.json").exists() for locale in LOCALES
        ):
            return candidate
    return None


def load(path: Path) -> dict[str, object]:
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as error:
        print(f"error: {path} is not valid JSON -- {error}", file=sys.stderr)
        raise SystemExit(2) from error
    except OSError as error:
        print(f"error: could not read {path} -- {error}", file=sys.stderr)
        raise SystemExit(2) from error

    if not isinstance(data, dict):
        print(f"error: {path} must contain an object at the top level", file=sys.stderr)
        raise SystemExit(2)

    return flatten(data)


def report(title: str, keys: list[str], limit: int = 25) -> None:
    # Everything in a failure goes to stderr, so the header, the detail and the
    # closing note stay in order when a CI log merges the two streams.
    print(f"\n{title} ({len(keys)}):", file=sys.stderr)
    for key in sorted(keys)[:limit]:
        print(f"  - {key}", file=sys.stderr)
    if len(keys) > limit:
        print(f"  ... and {len(keys) - limit} more", file=sys.stderr)


def main(argv: list[str]) -> int:
    messages_dir = find_messages_dir(argv[1] if len(argv) > 1 else None)

    if messages_dir is None:
        # The frontend may not exist yet. Passing keeps this check wired into
        # CI from the first commit, so it is already in place when it matters.
        print("check_locale_parity: no messages directory found yet -- skipping")
        return 0

    paths = {locale: messages_dir / f"{locale}.json" for locale in LOCALES}
    missing_files = [str(path) for path in paths.values() if not path.exists()]
    if missing_files:
        print(
            "error: both locales are required, missing: " + ", ".join(missing_files),
            file=sys.stderr,
        )
        return 1

    messages = {locale: load(path) for locale, path in paths.items()}
    ar_keys, en_keys = set(messages["ar"]), set(messages["en"])

    missing_in_ar = sorted(en_keys - ar_keys)
    missing_in_en = sorted(ar_keys - en_keys)

    # A key present but blank is an untranslated string wearing a translation's
    # clothes -- it passes a key-set comparison and renders as nothing on screen.
    blank = [
        f"{locale}.json: {key}"
        for locale in LOCALES
        for key, value in messages[locale].items()
        if isinstance(value, str) and not value.strip()
    ]

    if not (missing_in_ar or missing_in_en or blank):
        print(
            f"check_locale_parity: ok -- {len(ar_keys)} keys match "
            f"across {', '.join(f'{l}.json' for l in LOCALES)}"
        )
        return 0

    print(f"check_locale_parity: FAILED in {messages_dir}", file=sys.stderr)
    if missing_in_ar:
        report("Present in en.json, missing from ar.json", missing_in_ar)
    if missing_in_en:
        report("Present in ar.json, missing from en.json", missing_in_en)
    if blank:
        report("Present but empty", blank)

    print(
        "\nNon-negotiable 1: locale keys ship in the same commit as the string\n"
        "that uses them. Add the missing keys and commit them together.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
