"""CRUD for Company. Usage:

  uv run python scripts/companies.py register --id <uuid> --ticker 1234 \
      --market "東証プライム" --name "サンプル株式会社" --fiscal-year-end 03-31 \
      --sector-ids <uuid1>,<uuid2> --primary-sector-id <uuid1> \
      [--driver-tree '[...]'] [--body "任意の本文"]
  uv run python scripts/companies.py list [--sector-id <uuid>]
  uv run python scripts/companies.py view --id <uuid>
  uv run python scripts/companies.py snapshot-context --id <uuid>
  uv run python scripts/companies.py update-snapshot --id <uuid> --as-of 2024-06-01 --summary "..."
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
    idx.upsert("companies", _company_index_row(frontmatter))
    _sync_sector_company_count(sector_ids)
    print(json.dumps(frontmatter, ensure_ascii=False))


def _company_index_row(fm: dict) -> dict:
    return {k: fm[k] for k in idx.TABLE_SCHEMAS["companies"].names}


def _sync_sector_company_count(sector_ids: list[str]) -> None:
    """Keep sectors.companyCount consistent after adding a Company.

    Recomputes the count from the Vault directly (rather than patching a
    possibly-absent or stale index row) so this stays correct even if the
    index was deleted/rebuilt out of band.
    """
    for sector_id in set(sector_ids):
        try:
            sector_fm, _ = vault.read_entity("sectors", sector_id)
        except FileNotFoundError:
            continue
        count = sum(
            1
            for _, cfm, _ in vault.list_entities("companies")
            if sector_id in (cfm.get("sectorIds") or [])
        )
        idx.upsert(
            "sectors",
            {
                "id": sector_fm["id"],
                "name": sector_fm["name"],
                "driverTreeTemplateCount": len(sector_fm.get("driverTreeTemplate") or []),
                "companyCount": count,
                "createdAt": sector_fm["createdAt"],
            },
        )


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


def _company_thoughts(company_id: str) -> list[tuple[str, dict, str]]:
    return [
        (tid, tfm, tbody)
        for tid, tfm, tbody in vault.list_entities("thoughts")
        if company_id in (tfm.get("companyIds") or [])
    ]


def _findings_for(finding_ids: set[str]) -> list[dict]:
    findings = []
    for fid in finding_ids:
        try:
            ffm, _ = vault.read_entity("findings", fid)
        except FileNotFoundError:
            continue
        findings.append(
            {
                "id": ffm["id"],
                "type": ffm.get("type"),
                "title": ffm.get("title"),
                "url": ffm.get("url"),
                "evidenceTier": ffm.get("evidenceTier"),
                "savedAt": ffm.get("savedAt"),
            }
        )
    findings.sort(key=lambda f: f.get("savedAt") or "", reverse=True)
    return findings


def cmd_view(args: argparse.Namespace) -> None:
    try:
        fm, body = vault.read_entity("companies", args.id)
    except FileNotFoundError:
        fail([f"Company not found: {args.id}"])
        return

    thoughts = _company_thoughts(args.id)
    filled_node_ids = {n for _, tfm, _ in thoughts for n in (tfm.get("driverNodeIds") or [])}
    driver_tree = [
        {**node, "filled": node["id"] in filled_node_ids}
        for node in (fm.get("driverTree") or [])
    ]

    all_finding_ids = {fid for _, tfm, _ in thoughts for fid in (tfm.get("findingIds") or [])}
    findings = _findings_for(all_finding_ids)

    theses = [
        {"id": tid, "statement": tfm.get("statement"), "status": tfm.get("status"), "updatedAt": tfm.get("updatedAt")}
        for tid, tfm, _ in vault.list_entities("theses")
        if tfm.get("companyId") == args.id
    ]
    theses.sort(key=lambda t: t.get("updatedAt") or "", reverse=True)

    print(
        json.dumps(
            {
                "company": {**fm, "body": body},
                "driverTree": driver_tree,
                "findings": findings,
                "theses": theses,
            },
            ensure_ascii=False,
        )
    )


def cmd_snapshot_context(args: argparse.Namespace) -> None:
    try:
        fm, _ = vault.read_entity("companies", args.id)
    except FileNotFoundError:
        fail([f"Company not found: {args.id}"])
        return

    previous_snapshot = fm.get("currentSnapshot")
    previous_as_of = previous_snapshot["asOf"] if previous_snapshot else None

    thoughts = [
        {
            "id": tid,
            "type": tfm.get("type"),
            "findingIds": tfm.get("findingIds") or [],
            "driverNodeIds": tfm.get("driverNodeIds") or [],
            "createdAt": tfm.get("createdAt"),
            "body": tbody,
        }
        for tid, tfm, tbody in _company_thoughts(args.id)
        if previous_as_of is None or (tfm.get("createdAt") or "") > previous_as_of
    ]
    finding_ids = {fid for t in thoughts for fid in t["findingIds"]}

    print(
        json.dumps(
            {
                "previousSnapshot": previous_snapshot,
                "thoughts": thoughts,
                "findings": _findings_for(finding_ids),
            },
            ensure_ascii=False,
        )
    )


def cmd_update_snapshot(args: argparse.Namespace) -> None:
    errors = []
    if not args.summary.strip():
        errors.append("summary must not be empty")
    if not vault.is_valid_date(args.as_of):
        errors.append("asOf must be a date in YYYY-MM-DD format")
    if errors:
        fail(errors)

    try:
        fm, body = vault.read_entity("companies", args.id)
    except FileNotFoundError:
        fail([f"Company not found: {args.id}"])
        return

    fm["currentSnapshot"] = {"asOf": args.as_of, "summary": args.summary}
    fm["updatedAt"] = vault.now_iso()
    vault.write_entity("companies", args.id, fm, body=body)
    idx.upsert("companies", _company_index_row(fm))

    print(json.dumps(fm, ensure_ascii=False))


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

    p_view = sub.add_parser("view")
    p_view.add_argument("--id", required=True)
    p_view.set_defaults(func=cmd_view)

    p_snapshot_context = sub.add_parser("snapshot-context")
    p_snapshot_context.add_argument("--id", required=True)
    p_snapshot_context.set_defaults(func=cmd_snapshot_context)

    p_update_snapshot = sub.add_parser("update-snapshot")
    p_update_snapshot.add_argument("--id", required=True)
    p_update_snapshot.add_argument("--as-of", required=True)
    p_update_snapshot.add_argument("--summary", required=True)
    p_update_snapshot.set_defaults(func=cmd_update_snapshot)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
