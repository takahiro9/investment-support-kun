"""CRUD for Company. Usage:

  uv run python scripts/companies.py register --id <uuid> --ticker 1234 \
      --market "東証プライム" --name "サンプル株式会社" --fiscal-year-end 03-31 \
      --sector-ids <uuid1>,<uuid2> --primary-sector-id <uuid1> \
      [--driver-tree '[...]'] [--body "任意の本文"]
  uv run python scripts/companies.py list [--sector-id <uuid>]
"""
from __future__ import annotations

import argparse
import copy
import json
import sys

import index as idx
import vault


def fail(errors: list[str]) -> None:
    print(json.dumps({"errors": errors}, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)


def cmd_register(args: argparse.Namespace) -> None:
    sector_ids = [s.strip() for s in args.sector_ids.split(",") if s.strip()]

    errors = []
    if not args.ticker.strip():
        errors.append("ticker must not be empty")
    if not sector_ids:
        errors.append("sectorIds must include at least one Sector")
    if args.primary_sector_id not in sector_ids:
        errors.append("primarySectorId must be one of sectorIds")
    if errors:
        fail(errors)

    if idx.find_by("companies", ticker=args.ticker):
        fail([f"a Company with ticker '{args.ticker}' is already registered"])

    try:
        primary_sector_fm, _ = vault.read_entity("sectors", args.primary_sector_id)
    except FileNotFoundError:
        fail([f"Sector not found: {args.primary_sector_id}"])
        return

    if args.driver_tree:
        driver_tree = json.loads(args.driver_tree)
    else:
        driver_tree = copy.deepcopy(primary_sector_fm.get("driverTreeTemplate") or [])

    now = vault.now_iso()
    frontmatter = {
        "id": args.id,
        "ticker": args.ticker,
        "market": args.market,
        "sectorIds": sector_ids,
        "primarySectorId": args.primary_sector_id,
        "name": args.name,
        "fiscalYearEnd": args.fiscal_year_end,
        "driverTree": driver_tree,
        "currentSnapshot": None,
        "createdAt": now,
        "updatedAt": now,
    }
    vault.write_entity("companies", args.id, frontmatter, body=args.body or "")
    idx.upsert(
        "companies",
        {
            "id": frontmatter["id"],
            "ticker": frontmatter["ticker"],
            "market": frontmatter["market"],
            "name": frontmatter["name"],
            "sectorIds": frontmatter["sectorIds"],
            "primarySectorId": frontmatter["primarySectorId"],
            "fiscalYearEnd": frontmatter["fiscalYearEnd"],
            "createdAt": frontmatter["createdAt"],
            "updatedAt": frontmatter["updatedAt"],
        },
    )
    _sync_sector_company_count(sector_ids)
    print(json.dumps(frontmatter, ensure_ascii=False))


def _sync_sector_company_count(sector_ids: list[str]) -> None:
    """Keep sectors.companyCount consistent after adding a Company."""
    for sector_id in set(sector_ids):
        matches = idx.find_by("sectors", id=sector_id)
        if not matches:
            continue
        record = matches[0]
        record["companyCount"] = record["companyCount"] + 1
        idx.upsert("sectors", record)


def cmd_list(args: argparse.Namespace) -> None:
    if args.sector_id:
        rows = [
            row
            for row in idx.query_all("companies")
            if args.sector_id in (row.get("sectorIds") or [])
        ]
    else:
        rows = idx.query_all("companies")
    print(json.dumps(rows, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Company CRUD")
    sub = parser.add_subparsers(dest="command", required=True)

    p_register = sub.add_parser("register")
    p_register.add_argument("--id", required=True)
    p_register.add_argument("--ticker", required=True)
    p_register.add_argument("--market", required=True)
    p_register.add_argument("--name", required=True)
    p_register.add_argument("--fiscal-year-end", required=True)
    p_register.add_argument("--sector-ids", required=True)
    p_register.add_argument("--primary-sector-id", required=True)
    p_register.add_argument("--driver-tree")
    p_register.add_argument("--body")
    p_register.set_defaults(func=cmd_register)

    p_list = sub.add_parser("list")
    p_list.add_argument("--sector-id")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
