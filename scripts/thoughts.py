"""CRUD for Thought. Usage:

  uv run python scripts/thoughts.py add --id <uuid> \\
      --finding-ids <uuid1>,<uuid2> --type note --body "考察本文..." \\
      [--company-ids <uuid>,...] [--sector-ids <uuid>,...] [--theme-ids <uuid>,...] \\
      [--driver-node-ids <nodeId>,...] [--tags tag1,tag2]
"""
from __future__ import annotations

import argparse
import json
import sys

import index as idx
import vault

TYPES = ["note", "question", "prediction"]


def fail(errors: list[str]) -> None:
    print(json.dumps({"errors": errors}, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)


def _split(value: str | None) -> list[str]:
    return [v.strip() for v in (value or "").split(",") if v.strip()]


def cmd_add(args: argparse.Namespace) -> None:
    finding_ids = _split(args.finding_ids)
    company_ids = _split(args.company_ids)
    sector_ids = _split(args.sector_ids)
    theme_ids = _split(args.theme_ids)
    driver_node_ids = _split(args.driver_node_ids)
    tags = _split(args.tags)

    errors = []
    if not finding_ids:
        errors.append("findingIds must include at least one Finding")
    if not (args.body or "").strip():
        errors.append("body must not be empty")
    if driver_node_ids and not company_ids:
        errors.append("driverNodeIds requires at least one companyId")
    if errors:
        fail(errors)

    for fid in finding_ids:
        try:
            vault.read_entity("findings", fid)
        except FileNotFoundError:
            fail([f"Finding not found: {fid}"])
            return
    for cid in company_ids:
        try:
            vault.read_entity("companies", cid)
        except FileNotFoundError:
            fail([f"Company not found: {cid}"])
            return
    for sid in sector_ids:
        try:
            vault.read_entity("sectors", sid)
        except FileNotFoundError:
            fail([f"Sector not found: {sid}"])
            return
    # Theme not implemented yet (Phase 4) — themeIds are accepted as opaque references.

    if driver_node_ids:
        known_node_ids: set[str] = set()
        for cid in company_ids:
            company_fm, _ = vault.read_entity("companies", cid)
            known_node_ids |= {node["id"] for node in (company_fm.get("driverTree") or [])}
        missing = [n for n in driver_node_ids if n not in known_node_ids]
        if missing:
            fail([f"driverNodeId(s) not found in the given companies' driverTree: {', '.join(missing)}"])
            return

    frontmatter = {
        "id": args.id,
        "findingIds": finding_ids,
        "companyIds": company_ids,
        "sectorIds": sector_ids,
        "themeIds": theme_ids,
        "driverNodeIds": driver_node_ids,
        "type": args.type,
        "createdAt": vault.now_iso(),
        "tags": tags,
    }
    vault.write_entity("thoughts", args.id, frontmatter, body=args.body)
    idx.upsert("thoughts", {k: frontmatter[k] for k in idx.TABLE_SCHEMAS["thoughts"].names})
    print(json.dumps({**frontmatter, "body": args.body}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Thought CRUD")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("--id", required=True)
    p_add.add_argument("--finding-ids", required=True)
    p_add.add_argument("--company-ids")
    p_add.add_argument("--sector-ids")
    p_add.add_argument("--theme-ids")
    p_add.add_argument("--driver-node-ids")
    p_add.add_argument("--type", required=True, choices=TYPES)
    p_add.add_argument("--body", required=True)
    p_add.add_argument("--tags")
    p_add.set_defaults(func=cmd_add)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
