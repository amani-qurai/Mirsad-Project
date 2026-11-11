"""domain/ imports nothing from api/ or repositories/ (CLAUDE.md, ADR-0001 §6).

ADR-0001 §8 asks for this to be enforced in CI rather than only in review.
This test is that enforcement: it reads every module under app/domain and
fails on any import of the HTTP or persistence layers.
"""

from __future__ import annotations

import ast
from pathlib import Path

DOMAIN = Path(__file__).resolve().parents[1] / "app" / "domain"
FORBIDDEN = ("app.api", "app.repositories", "app.pipeline")


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.append(node.module)
    return names


def test_domain_has_modules():
    assert list(DOMAIN.rglob("*.py"))


def test_domain_imports_no_outer_layer():
    offenders = [
        f"{path.relative_to(DOMAIN.parent)}: {name}"
        for path in DOMAIN.rglob("*.py")
        for name in _imports(path)
        if name.startswith(FORBIDDEN)
    ]
    assert offenders == []
