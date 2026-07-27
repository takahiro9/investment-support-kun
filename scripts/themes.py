"""CRUD for Theme. Usage:

  uv run python scripts/themes.py register --id <uuid> --name "半導体サプライチェーン再編" \\
      [--description "..."] [--sector-ids <id1>,<id2>] [--body "任意の本文"]
  uv run python scripts/themes.py list
"""
from __future__ import annotations

import argparse
import json
import sys

import index as idx
import vault


def fail(errors: list[str]) -> None:
    print(json.dumps({"errors": errors}, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)


def _split(value: str | None) -> list[str]:
    return [v.strip() for v in (value or "").split(",") if v.strip()]


def cmd_register(args: argparse.Namespace) -> None:
    sector_ids = _split(args.sector_ids)

    errors = []
    if not args.name.strip():
        errors.append("name must not be empty")
    if len(sector_ids) != len(set(sector_ids)):
        errors.append("sectorIds must not contain duplicates")
    if errors:
        fail(errors)

    for sid in sector_ids:
        try:
            vault.read_entity("sectors", sid)
        except FileNotFoundError:
            fail([f"Sector not found: {sid}"])
            return

    frontmatter = {
        "id": args.id,
        "name": args.name,
        "description": args.description or None,
        "sectorIds": sector_ids,
        "createdAt": vault.now_iso(),
    }
    vault.write_entity("themes", args.id, frontmatter, body=args.body or "")
    idx.upsert("themes", {k: frontmatter[k] for k in idx.TABLE_SCHEMAS["themes"].names})
    print(json.dumps(frontmatter, ensure_ascii=False))


def cmd_list(args: argparse.Namespace) -> None:
    rows = idx.query_all("themes")
    theme_finding_ids: dict[str, set[str]] = {row["id"]: set() for row in rows}
    for _, tfm, _ in vault.list_entities("thoughts"):
        for theme_id in tfm.get("themeIds") or []:
            if theme_id in theme_finding_ids:
                theme_finding_ids[theme_id].update(tfm.get("findingIds") or [])
    for row in rows:
        row["findingCount"] = len(theme_finding_ids.get(row["id"], set()))
    print(json.dumps(rows, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Theme CRUD")
    sub = parser.add_subparsers(dest="command", required=True)

    p_register = sub.add_parser("register")
    p_register.add_argument("--id", required=True)
    p_register.add_argument("--name", required=True)
    p_register.add_argument("--description")
    p_register.add_argument("--sector-ids")
    p_register.add_argument("--body")
    p_register.set_defaults(func=cmd_register)

    p_list = sub.add_parser("list")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
