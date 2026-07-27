"""CRUD for InvestmentAction. Usage:

  uv run python scripts/investment_actions.py create --id <uuid> --company-id <uuid> \\
      --action add --position-sizing-rationale "..." --next-research "..." \\
      [--related-thesis-ids <id1>,<id2>] [--related-strategy-recommendation-ids <id1>,<id2>] \\
      [--position-size-percent 3] [--bear-case "反対側の論証"] [--body "任意の本文"]
  uv run python scripts/investment_actions.py list --company-id <uuid>
"""
from __future__ import annotations

import argparse
import json
import sys

import index as idx
import vault

ACTIONS = ["entry", "add", "hold", "reduce", "exit"]


def fail(errors: list[str]) -> None:
    print(json.dumps({"errors": errors}, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)


def _split(value: str | None) -> list[str]:
    return [v.strip() for v in (value or "").split(",") if v.strip()]


def cmd_create(args: argparse.Namespace) -> None:
    related_thesis_ids = _split(args.related_thesis_ids)
    related_strategy_recommendation_ids = _split(args.related_strategy_recommendation_ids)

    errors = []
    if not args.position_sizing_rationale.strip():
        errors.append("positionSizingRationale must not be empty")
    if not args.next_research.strip():
        errors.append("nextResearch must not be empty")
    if errors:
        fail(errors)

    try:
        vault.read_entity("companies", args.company_id)
    except FileNotFoundError:
        fail([f"Company not found: {args.company_id}"])
        return

    for tid in related_thesis_ids:
        try:
            vault.read_entity("theses", tid)
        except FileNotFoundError:
            fail([f"Thesis not found: {tid}"])
            return
    for sid in related_strategy_recommendation_ids:
        try:
            vault.read_entity("strategy_recommendations", sid)
        except FileNotFoundError:
            fail([f"StrategyRecommendation not found: {sid}"])
            return

    warnings = []
    has_thesis = any(fm.get("companyId") == args.company_id for _, fm, _ in vault.list_entities("theses"))
    if not has_thesis:
        warnings.append(f"Company {args.company_id} has no Thesis yet — this action's basis is thin")

    now = vault.now_iso()
    frontmatter = {
        "id": args.id,
        "companyId": args.company_id,
        "relatedThesisIds": related_thesis_ids,
        "relatedStrategyRecommendationIds": related_strategy_recommendation_ids,
        "action": args.action,
        "positionSizingRationale": args.position_sizing_rationale,
        "positionSizePercent": args.position_size_percent,
        "nextResearch": args.next_research,
        "bearCase": args.bear_case or "",
        "createdAt": now,
        "updatedAt": now,
    }
    vault.write_entity("investment_actions", args.id, frontmatter, body=args.body or "")
    idx.upsert(
        "investment_actions",
        {k: frontmatter[k] for k in idx.TABLE_SCHEMAS["investment_actions"].names},
    )
    print(
        json.dumps(
            {**frontmatter, "redTeamPending": not frontmatter["bearCase"], "warnings": warnings},
            ensure_ascii=False,
        )
    )


def cmd_list(args: argparse.Namespace) -> None:
    rows = [r for r in idx.query_all("investment_actions") if r.get("companyId") == args.company_id]
    rows.sort(key=lambda r: r.get("createdAt") or "", reverse=True)
    for row in rows:
        row["redTeamPending"] = not row.get("bearCase")
    print(json.dumps(rows, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="InvestmentAction CRUD")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create")
    p_create.add_argument("--id", required=True)
    p_create.add_argument("--company-id", required=True)
    p_create.add_argument("--action", required=True, choices=ACTIONS)
    p_create.add_argument("--related-thesis-ids")
    p_create.add_argument("--related-strategy-recommendation-ids")
    p_create.add_argument("--position-sizing-rationale", required=True)
    p_create.add_argument("--position-size-percent", type=float)
    p_create.add_argument("--next-research", required=True)
    p_create.add_argument("--bear-case")
    p_create.add_argument("--body")
    p_create.set_defaults(func=cmd_create)

    p_list = sub.add_parser("list")
    p_list.add_argument("--company-id", required=True)
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
