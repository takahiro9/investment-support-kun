"""CRUD for Finding. Usage:

  uv run python scripts/findings.py add --id <uuid> --type memo \\
      --title "決算メモ" --evidence-tier company_issued --body "本文..." \\
      [--url <url>] [--source-url <url>] [--content-updated-at <iso8601>] \\
      [--tags tag1,tag2]
  uv run python scripts/findings.py view --id <uuid>
  uv run python scripts/findings.py list [--type <type>] [--evidence-tier <tier>]
"""
from __future__ import annotations

import argparse
import json
import sys

import index as idx
import vault

TYPES = ["web_article", "memo", "pdf", "youtube", "image", "disclosure", "market_data", "link"]
EVIDENCE_TIERS = ["primary_disclosure", "company_issued", "third_party", "inference"]
URL_REQUIRED_TYPES = {"web_article", "youtube", "disclosure", "link"}


def fail(errors: list[str]) -> None:
    print(json.dumps({"errors": errors}, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)


def cmd_add(args: argparse.Namespace) -> None:
    errors = []
    if not args.title.strip():
        errors.append("title must not be empty")
    if args.type in URL_REQUIRED_TYPES and not (args.url or "").strip():
        errors.append(f"type '{args.type}' requires --url")
    if args.type == "memo" and not (args.body or "").strip():
        errors.append("type 'memo' requires --body")
    if errors:
        fail(errors)

    if args.url and idx.find_by("findings", url=args.url):
        fail([f"a Finding with url '{args.url}' is already registered"])

    tags = [t.strip() for t in (args.tags or "").split(",") if t.strip()]
    frontmatter = {
        "id": args.id,
        "type": args.type,
        "title": args.title,
        "url": args.url or None,
        "sourceUrl": args.source_url or None,
        "evidenceTier": args.evidence_tier,
        "savedAt": vault.now_iso(),
        "contentUpdatedAt": args.content_updated_at or None,
        "tags": tags,
    }
    vault.write_entity("findings", args.id, frontmatter, body=args.body or "")
    idx.upsert("findings", {k: frontmatter[k] for k in idx.TABLE_SCHEMAS["findings"].names})
    print(json.dumps(frontmatter, ensure_ascii=False))


def cmd_view(args: argparse.Namespace) -> None:
    try:
        fm, body = vault.read_entity("findings", args.id)
    except FileNotFoundError:
        fail([f"Finding not found: {args.id}"])
        return

    thoughts = [
        {
            "id": tid,
            "findingIds": tfm.get("findingIds") or [],
            "companyIds": tfm.get("companyIds") or [],
            "sectorIds": tfm.get("sectorIds") or [],
            "themeIds": tfm.get("themeIds") or [],
            "driverNodeIds": tfm.get("driverNodeIds") or [],
            "type": tfm.get("type"),
            "createdAt": tfm.get("createdAt"),
            "tags": tfm.get("tags") or [],
            "body": tbody,
        }
        for tid, tfm, tbody in vault.list_entities("thoughts")
        if args.id in (tfm.get("findingIds") or [])
    ]
    print(json.dumps({"finding": {**fm, "body": body}, "thoughts": thoughts}, ensure_ascii=False))


def cmd_list(args: argparse.Namespace) -> None:
    rows = idx.query_all("findings")
    if args.type:
        rows = [r for r in rows if r.get("type") == args.type]
    if args.evidence_tier:
        rows = [r for r in rows if r.get("evidenceTier") == args.evidence_tier]
    rows.sort(key=lambda r: r.get("savedAt") or "", reverse=True)
    print(json.dumps(rows, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Finding CRUD")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("--id", required=True)
    p_add.add_argument("--type", required=True, choices=TYPES)
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--url")
    p_add.add_argument("--source-url")
    p_add.add_argument("--evidence-tier", required=True, choices=EVIDENCE_TIERS)
    p_add.add_argument("--content-updated-at")
    p_add.add_argument("--tags")
    p_add.add_argument("--body")
    p_add.set_defaults(func=cmd_add)

    p_view = sub.add_parser("view")
    p_view.add_argument("--id", required=True)
    p_view.set_defaults(func=cmd_view)

    p_list = sub.add_parser("list")
    p_list.add_argument("--type", choices=TYPES)
    p_list.add_argument("--evidence-tier", choices=EVIDENCE_TIERS)
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
