"""CRUD for Signal. Usage:

  uv run python scripts/signals.py record --id <uuid> --company-id <uuid> \\
      --category operational --metric "operating_margin" --period "2027Q2" --value 12.3 \\
      --validates-thesis-id <uuid> --validates-assumption "..." \\
      [--unit "%"] [--source-finding-id <uuid>]
  uv run python scripts/signals.py list --thesis-id <uuid> [--category <category>]
"""
from __future__ import annotations

import argparse
import json
import sys

import index as idx
import vault

CATEGORIES = ["financial", "operational", "leading", "market"]


def fail(errors: list[str]) -> None:
    print(json.dumps({"errors": errors}, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)


def cmd_record(args: argparse.Namespace) -> None:
    errors = []
    if not args.validates_assumption.strip():
        errors.append("validatesAssumption must not be empty")
    if errors:
        fail(errors)

    try:
        vault.read_entity("companies", args.company_id)
    except FileNotFoundError:
        fail([f"Company not found: {args.company_id}"])
        return

    try:
        thesis_fm, _ = vault.read_entity("theses", args.validates_thesis_id)
    except FileNotFoundError:
        fail([f"Thesis not found: {args.validates_thesis_id}"])
        return
    if thesis_fm.get("companyId") != args.company_id:
        fail([f"Thesis {args.validates_thesis_id} does not belong to Company {args.company_id}"])
        return

    if args.source_finding_id:
        try:
            vault.read_entity("findings", args.source_finding_id)
        except FileNotFoundError:
            fail([f"Finding not found: {args.source_finding_id}"])
            return

    frontmatter = {
        "id": args.id,
        "companyId": args.company_id,
        "category": args.category,
        "metric": args.metric,
        "period": args.period,
        "value": args.value,
        "unit": args.unit or None,
        "sourceFindingId": args.source_finding_id or None,
        "extractionMethod": "manual",
        "validatesThesisId": args.validates_thesis_id,
        "validatesAssumption": args.validates_assumption,
        "createdAt": vault.now_iso(),
    }
    vault.write_entity("signals", args.id, frontmatter)
    idx.upsert("signals", {k: frontmatter[k] for k in idx.TABLE_SCHEMAS["signals"].names})
    print(json.dumps(frontmatter, ensure_ascii=False))


def cmd_list(args: argparse.Namespace) -> None:
    rows = [r for r in idx.query_all("signals") if r.get("validatesThesisId") == args.thesis_id]
    if args.category:
        rows = [r for r in rows if r.get("category") == args.category]
    rows.sort(key=lambda r: (r.get("metric") or "", r.get("period") or ""))
    print(json.dumps(rows, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Signal CRUD")
    sub = parser.add_subparsers(dest="command", required=True)

    p_record = sub.add_parser("record")
    p_record.add_argument("--id", required=True)
    p_record.add_argument("--company-id", required=True)
    p_record.add_argument("--category", required=True, choices=CATEGORIES)
    p_record.add_argument("--metric", required=True)
    p_record.add_argument("--period", required=True)
    p_record.add_argument("--value", required=True, type=float)
    p_record.add_argument("--unit")
    p_record.add_argument("--source-finding-id")
    p_record.add_argument("--validates-thesis-id", required=True)
    p_record.add_argument("--validates-assumption", required=True)
    p_record.set_defaults(func=cmd_record)

    p_list = sub.add_parser("list")
    p_list.add_argument("--thesis-id", required=True)
    p_list.add_argument("--category", choices=CATEGORIES)
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
