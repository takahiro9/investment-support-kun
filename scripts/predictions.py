"""CRUD for Prediction. Usage:

  uv run python scripts/predictions.py add --id <uuid> --thesis-id <uuid> \\
      --source-thought-id <uuid> --statement "..." --horizon 2027-09-30 --probability 0.6 \\
      --observable-text "決算短信の営業利益率" \\
      [--signal-metric operating_margin --comparator ">" --threshold 12 [--observable-unit "%"]] \\
      [--body "予測の背景"]
  uv run python scripts/predictions.py list [--company-id <uuid>] [--thesis-id <uuid>] \\
      [--outcome hit|miss|ambiguous|unresolved]
  uv run python scripts/predictions.py resolution-context --id <uuid>
  uv run python scripts/predictions.py resolve --id <uuid> --outcome hit|miss|ambiguous \\
      [--postmortem "..."]
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys

import index as idx
import vault

COMPARATORS = [">", ">=", "<", "<=", "="]
OUTCOMES = ["hit", "miss", "ambiguous"]


def fail(errors: list[str]) -> None:
    print(json.dumps({"errors": errors}, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)


def _compare(value: float, comparator: str, threshold: float) -> bool:
    return {
        ">": value > threshold,
        ">=": value >= threshold,
        "<": value < threshold,
        "<=": value <= threshold,
        "=": value == threshold,
    }[comparator]


def cmd_add(args: argparse.Namespace) -> None:
    errors = []
    if not args.statement.strip():
        errors.append("statement must not be empty")
    if not args.observable_text.strip():
        errors.append("observableText must not be empty")
    if not (0 <= args.probability <= 1):
        errors.append("probability must be between 0 and 1")
    observable_parts = [args.signal_metric, args.comparator, args.threshold]
    if any(p is not None for p in observable_parts) and not all(p is not None for p in observable_parts):
        errors.append("signal-metric/comparator/threshold must all be given together for observableRef")
    if errors:
        fail(errors)

    try:
        vault.read_entity("theses", args.thesis_id)
    except FileNotFoundError:
        fail([f"Thesis not found: {args.thesis_id}"])
        return

    try:
        thought_fm, _ = vault.read_entity("thoughts", args.source_thought_id)
    except FileNotFoundError:
        fail([f"Thought not found: {args.source_thought_id}"])
        return
    if thought_fm.get("type") != "prediction":
        fail([f"Thought {args.source_thought_id} is not type=prediction"])
        return

    observable_ref = None
    if args.signal_metric is not None:
        observable_ref = {
            "signalMetric": args.signal_metric,
            "comparator": args.comparator,
            "threshold": args.threshold,
            "unit": args.observable_unit or None,
        }

    frontmatter = {
        "id": args.id,
        "thesisId": args.thesis_id,
        "sourceThoughtId": args.source_thought_id,
        "statement": args.statement,
        "horizon": args.horizon,
        "probability": args.probability,
        "observableText": args.observable_text,
        "observableRef": observable_ref,
        "resolvedAt": None,
        "outcome": None,
        "postmortem": None,
        "createdAt": vault.now_iso(),
    }
    vault.write_entity("predictions", args.id, frontmatter, body=args.body or "")
    idx.upsert("predictions", _index_row(frontmatter))
    print(json.dumps(frontmatter, ensure_ascii=False))


def _index_row(fm: dict) -> dict:
    ref = fm.get("observableRef") or {}
    return {
        "id": fm["id"],
        "thesisId": fm["thesisId"],
        "sourceThoughtId": fm.get("sourceThoughtId"),
        "statement": fm["statement"],
        "horizon": fm["horizon"],
        "probability": fm["probability"],
        "observableText": fm["observableText"],
        "observableSignalMetric": ref.get("signalMetric"),
        "observableComparator": ref.get("comparator"),
        "observableThreshold": ref.get("threshold"),
        "observableUnit": ref.get("unit"),
        "resolvedAt": fm.get("resolvedAt"),
        "outcome": fm.get("outcome"),
        "postmortem": fm.get("postmortem"),
        "createdAt": fm["createdAt"],
    }


def cmd_list(args: argparse.Namespace) -> None:
    rows = idx.query_all("predictions")
    if args.thesis_id:
        rows = [r for r in rows if r.get("thesisId") == args.thesis_id]
    if args.company_id:
        company_thesis_ids = {
            t["id"] for t in idx.query_all("theses") if t.get("companyId") == args.company_id
        }
        rows = [r for r in rows if r.get("thesisId") in company_thesis_ids]
    if args.outcome == "unresolved":
        rows = [r for r in rows if not r.get("resolvedAt")]
    elif args.outcome:
        rows = [r for r in rows if r.get("outcome") == args.outcome]

    today = datetime.date.today().isoformat()
    for row in rows:
        row["awaitingResolution"] = not row.get("resolvedAt") and (row.get("horizon") or "") < today
    rows.sort(key=lambda r: r.get("horizon") or "")

    stats = {"hit": 0, "miss": 0, "ambiguous": 0, "unresolved": 0}
    for row in rows:
        if row.get("resolvedAt") and row.get("outcome") in stats:
            stats[row["outcome"]] += 1
        elif not row.get("resolvedAt"):
            stats["unresolved"] += 1
    print(json.dumps({"predictions": rows, "stats": stats}, ensure_ascii=False))


def cmd_resolution_context(args: argparse.Namespace) -> None:
    try:
        fm, body = vault.read_entity("predictions", args.id)
    except FileNotFoundError:
        fail([f"Prediction not found: {args.id}"])
        return

    thesis_fm, _ = vault.read_entity("theses", fm["thesisId"])
    company_id = thesis_fm.get("companyId")

    candidates = []
    ref = fm.get("observableRef")
    if ref:
        for sid, sfm, _ in vault.list_entities("signals"):
            if sfm.get("companyId") != company_id or sfm.get("metric") != ref["signalMetric"]:
                continue
            suggested = "hit" if _compare(sfm["value"], ref["comparator"], ref["threshold"]) else "miss"
            candidates.append(
                {
                    "signalId": sid,
                    "period": sfm.get("period"),
                    "value": sfm.get("value"),
                    "unit": sfm.get("unit"),
                    "suggestedOutcome": suggested,
                }
            )
        candidates.sort(key=lambda c: c.get("period") or "", reverse=True)

    print(
        json.dumps(
            {"prediction": {**fm, "body": body}, "alreadyResolved": bool(fm.get("resolvedAt")), "candidates": candidates},
            ensure_ascii=False,
        )
    )


def cmd_resolve(args: argparse.Namespace) -> None:
    try:
        fm, body = vault.read_entity("predictions", args.id)
    except FileNotFoundError:
        fail([f"Prediction not found: {args.id}"])
        return

    if fm.get("resolvedAt"):
        fail([f"Prediction {args.id} is already resolved"])
        return
    if args.outcome in ("miss", "ambiguous") and not (args.postmortem or "").strip():
        fail(["postmortem is required when outcome is 'miss' or 'ambiguous'"])
        return

    fm["resolvedAt"] = vault.now_iso()
    fm["outcome"] = args.outcome
    fm["postmortem"] = args.postmortem or None
    vault.write_entity("predictions", args.id, fm, body=body)

    matches = idx.find_by("predictions", id=args.id)
    if matches:
        record = matches[0]
        record["resolvedAt"] = fm["resolvedAt"]
        record["outcome"] = fm["outcome"]
        record["postmortem"] = fm["postmortem"]
        idx.upsert("predictions", record)

    print(json.dumps(fm, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Prediction CRUD")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("--id", required=True)
    p_add.add_argument("--thesis-id", required=True)
    p_add.add_argument("--source-thought-id", required=True)
    p_add.add_argument("--statement", required=True)
    p_add.add_argument("--horizon", required=True)
    p_add.add_argument("--probability", required=True, type=float)
    p_add.add_argument("--observable-text", required=True)
    p_add.add_argument("--signal-metric")
    p_add.add_argument("--comparator", choices=COMPARATORS)
    p_add.add_argument("--threshold", type=float)
    p_add.add_argument("--observable-unit")
    p_add.add_argument("--body")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list")
    p_list.add_argument("--company-id")
    p_list.add_argument("--thesis-id")
    p_list.add_argument("--outcome", choices=OUTCOMES + ["unresolved"])
    p_list.set_defaults(func=cmd_list)

    p_resolution_context = sub.add_parser("resolution-context")
    p_resolution_context.add_argument("--id", required=True)
    p_resolution_context.set_defaults(func=cmd_resolution_context)

    p_resolve = sub.add_parser("resolve")
    p_resolve.add_argument("--id", required=True)
    p_resolve.add_argument("--outcome", required=True, choices=OUTCOMES)
    p_resolve.add_argument("--postmortem")
    p_resolve.set_defaults(func=cmd_resolve)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
