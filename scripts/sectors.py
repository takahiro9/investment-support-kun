"""CRUD for Sector. Usage:

  uv run python scripts/sectors.py register --id <uuid> --name "半導体製造装置" \
      [--driver-tree-template '[{"id": "revenue.segmentA.volume", "label": "...", "parentId": null, "formula": null}]'] \
      [--body "任意の本文"]
  uv run python scripts/sectors.py list
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


def cmd_register(args: argparse.Namespace) -> None:
    errors = []
    if not args.name.strip():
        errors.append("name must not be empty")
    if errors:
        fail(errors)

    if idx.find_by("sectors", name=args.name):
        fail([f"a Sector named '{args.name}' is already registered"])

    driver_tree_template = json.loads(args.driver_tree_template) if args.driver_tree_template else []

    frontmatter = {
        "id": args.id,
        "name": args.name,
        "driverTreeTemplate": driver_tree_template,
        "createdAt": vault.now_iso(),
    }
    vault.write_entity("sectors", args.id, frontmatter, body=args.body or "")
    idx.upsert(
        "sectors",
        {
            "id": frontmatter["id"],
            "name": frontmatter["name"],
            "driverTreeTemplateCount": len(driver_tree_template),
            "companyCount": 0,
            "createdAt": frontmatter["createdAt"],
        },
    )
    print(json.dumps(frontmatter, ensure_ascii=False))


def cmd_list(args: argparse.Namespace) -> None:
    print(json.dumps(idx.query_all("sectors"), ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Sector CRUD")
    sub = parser.add_subparsers(dest="command", required=True)

    p_register = sub.add_parser("register")
    p_register.add_argument("--id", required=True)
    p_register.add_argument("--name", required=True)
    p_register.add_argument("--driver-tree-template")
    p_register.add_argument("--body")
    p_register.set_defaults(func=cmd_register)

    p_list = sub.add_parser("list")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
