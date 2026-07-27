"""CRUD for StrategyRecommendation. Usage:

  uv run python scripts/strategy_recommendations.py add --id <uuid> --company-id <uuid> \\
      --option "サブスク転換" --execution-evidence "..." --execution-probability high \\
      --impact-if-executed "..." --priced-in partially_priced \\
      [--related-thesis-ids <id1>,<id2>] [--body "評価の詳しい論証"]
  uv run python scripts/strategy_recommendations.py list --company-id <uuid>

Run `add` once per option surfaced by the evaluation (one StrategyRecommendation per option).
"""
from __future__ import annotations

import argparse
import json
import sys

import index as idx
import vault

EXECUTION_PROBABILITIES = ["low", "medium", "high"]
PRICED_IN_LEVELS = ["not_priced", "partially_priced", "fully_priced"]


def fail(errors: list[str]) -> None:
    print(json.dumps({"errors": errors}, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)


def _split(value: str | None) -> list[str]:
    return [v.strip() for v in (value or "").split(",") if v.strip()]


def cmd_add(args: argparse.Namespace) -> None:
    related_thesis_ids = _split(args.related_thesis_ids)

    errors = []
    if not args.option.strip():
        errors.append("option must not be empty")
    if not args.execution_evidence.strip():
        errors.append("executionEvidence must not be empty")
    if not args.impact_if_executed.strip():
        errors.append("impactIfExecuted must not be empty")
    if errors:
        fail(errors)

    try:
        vault.read_entity("companies", args.company_id)
    except FileNotFoundError:
        fail([f"Company not found: {args.company_id}"])
        return

    has_thesis = any(fm.get("companyId") == args.company_id for _, fm, _ in vault.list_entities("theses"))
    if not has_thesis:
        fail([f"Company {args.company_id} has no Thesis yet — create one first (create-thesis)"])
        return

    for tid in related_thesis_ids:
        try:
            vault.read_entity("theses", tid)
        except FileNotFoundError:
            fail([f"Thesis not found: {tid}"])
            return

    now = vault.now_iso()
    frontmatter = {
        "id": args.id,
        "companyId": args.company_id,
        "relatedThesisIds": related_thesis_ids,
        "option": args.option,
        "executionEvidence": args.execution_evidence,
        "executionProbability": args.execution_probability,
        "impactIfExecuted": args.impact_if_executed,
        "pricedIn": args.priced_in,
        "createdAt": now,
        "updatedAt": now,
    }
    vault.write_entity("strategy_recommendations", args.id, frontmatter, body=args.body or "")
    idx.upsert(
        "strategy_recommendations",
        {k: frontmatter[k] for k in idx.TABLE_SCHEMAS["strategy_recommendations"].names},
    )
    print(json.dumps(frontmatter, ensure_ascii=False))


def cmd_list(args: argparse.Namespace) -> None:
    rows = [r for r in idx.query_all("strategy_recommendations") if r.get("companyId") == args.company_id]
    rows.sort(key=lambda r: r.get("createdAt") or "", reverse=True)
    print(json.dumps(rows, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="StrategyRecommendation CRUD")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("--id", required=True)
    p_add.add_argument("--company-id", required=True)
    p_add.add_argument("--option", required=True)
    p_add.add_argument("--execution-evidence", required=True)
    p_add.add_argument("--execution-probability", required=True, choices=EXECUTION_PROBABILITIES)
    p_add.add_argument("--impact-if-executed", required=True)
    p_add.add_argument("--priced-in", required=True, choices=PRICED_IN_LEVELS)
    p_add.add_argument("--related-thesis-ids")
    p_add.add_argument("--body")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list")
    p_list.add_argument("--company-id", required=True)
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
