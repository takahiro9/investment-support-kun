"""Vault I/O: read/write entities as YAML frontmatter + Markdown body.

Vault is the single source of truth (`data/vault/<entity>/<id>.md`). All
reads/writes must go through this module; hand-editing files under
data/vault/ is prohibited (see tech_context/architecture.md).
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

VAULT_ROOT = Path(__file__).resolve().parent.parent / "data" / "vault"

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def entity_dir(entity_type: str) -> Path:
    d = VAULT_ROOT / entity_type
    d.mkdir(parents=True, exist_ok=True)
    return d


def entity_path(entity_type: str, entity_id: str) -> Path:
    return entity_dir(entity_type) / f"{entity_id}.md"


def parse(content: str) -> tuple[dict, str]:
    m = _FRONTMATTER_RE.match(content)
    if not m:
        raise ValueError("invalid vault file: missing YAML frontmatter block")
    frontmatter = yaml.safe_load(m.group(1)) or {}
    body = m.group(2).lstrip("\n")
    return frontmatter, body


def render(frontmatter: dict, body: str = "") -> str:
    fm_yaml = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False)
    body = body.strip("\n")
    if body:
        return f"---\n{fm_yaml}---\n\n{body}\n"
    return f"---\n{fm_yaml}---\n"


def write_entity(entity_type: str, entity_id: str, frontmatter: dict, body: str = "") -> Path:
    path = entity_path(entity_type, entity_id)
    path.write_text(render(frontmatter, body), encoding="utf-8")
    return path


def read_entity(entity_type: str, entity_id: str) -> tuple[dict, str]:
    path = entity_path(entity_type, entity_id)
    if not path.exists():
        raise FileNotFoundError(f"{entity_type}/{entity_id} not found in vault")
    return parse(path.read_text(encoding="utf-8"))


def list_entities(entity_type: str) -> list[tuple[str, dict, str]]:
    """Return [(id, frontmatter, body), ...] for every entity file, sorted by id."""
    results = []
    for path in sorted(entity_dir(entity_type).glob("*.md")):
        frontmatter, body = parse(path.read_text(encoding="utf-8"))
        results.append((path.stem, frontmatter, body))
    return results
