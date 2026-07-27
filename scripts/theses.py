"""CRUD for Thesis. Usage:

  uv run python scripts/theses.py register --id <uuid> --company-id <uuid> \\
      --statement "..." --consensus-view "..." --variant "..." --why-mispriced "..." \\
      --invalidation "..." --confirmation "..." --thought-ids <id1>,<id2> --body "論証本文" \\
      [--horizon 2027-03-31] [--probability 0.6] [--tags tag1,tag2]
  uv run python scripts/theses.py list [--company-id <uuid>] [--status <status>]
  uv run python scripts/theses.py view --id <uuid>
  uv run python scripts/theses.py update-status --id <uuid> --status <status> \\
      [--note "遷移理由"] [--confirm]
"""
from __future__ import annotations

import argparse
import json
import sys

import index as idx
import vault

STATUSES = ["seed", "developing", "established", "challenged", "dropped"]


def fail(errors: list[str]) -> None:
    print(json.dumps({"errors": errors}, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)


def warn(message: str) -> None:
    print(json.dumps({"warning": message, "requiresConfirm": True}, ensure_ascii=False), file=sys.stderr)
    sys.exit(2)


def _split(value: str | None) -> list[str]:
    return [v.strip() for v in (value or "").split(",") if v.strip()]


REQUIRED_TEXT_FIELDS = [
    ("statement", "statement"),
    ("consensus_view", "consensusView"),
    ("variant", "variant"),
    ("why_mispriced", "whyMispriced"),
    ("invalidation", "invalidation"),
    ("confirmation", "confirmation"),
]


def cmd_register(args: argparse.Namespace) -> None:
    thought_ids = _split(args.thought_ids)

    errors = []
    for attr, field in REQUIRED_TEXT_FIELDS:
        if not getattr(args, attr).strip():
            errors.append(f"{field} must not be empty")
    if not (args.body or "").strip():
        errors.append("body must not be empty")
    if not thought_ids:
        errors.append("thoughtIds must include at least one Thought")
    if len(thought_ids) != len(set(thought_ids)):
        errors.append("thoughtIds must not contain duplicates")
    if args.probability is not None and not (0 <= args.probability <= 1):
        errors.append("probability must be between 0 and 1")
    if args.horizon and not vault.is_valid_date(args.horizon):
        errors.append("horizon must be a date in YYYY-MM-DD format")
    if errors:
        fail(errors)

    try:
        vault.read_entity("companies", args.company_id)
    except FileNotFoundError:
        fail([f"Company not found: {args.company_id}"])
        return

    for tid in thought_ids:
        try:
            vault.read_entity("thoughts", tid)
        except FileNotFoundError:
            fail([f"Thought not found: {tid}"])
            return

    now = vault.now_iso()
    tags = _split(args.tags)
    frontmatter = {
        "id": args.id,
        "companyId": args.company_id,
        "statement": args.statement,
        "consensusView": args.consensus_view,
        "variant": args.variant,
        "whyMispriced": args.why_mispriced,
        "invalidation": args.invalidation,
        "confirmation": args.confirmation,
        "horizon": args.horizon or None,
        "probability": args.probability,
        "status": "seed",
        "thoughtIds": thought_ids,
        "createdAt": now,
        "updatedAt": now,
        "tags": tags,
    }
    vault.write_entity("theses", args.id, frontmatter, body=args.body)
    idx.upsert("theses", {k: frontmatter[k] for k in idx.TABLE_SCHEMAS["theses"].names})
    print(json.dumps({**frontmatter, "body": args.body}, ensure_ascii=False))


def cmd_list(args: argparse.Namespace) -> None:
    rows = idx.query_all("theses")
    if args.company_id:
        rows = [r for r in rows if r.get("companyId") == args.company_id]
    if args.status:
        rows = [r for r in rows if r.get("status") == args.status]
    else:
        rows = [r for r in rows if r.get("status") != "dropped"]
    rows.sort(key=lambda r: r.get("updatedAt") or "", reverse=True)
    print(json.dumps(rows, ensure_ascii=False))


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
        fm, body = vault.read_entity("theses", args.id)
    except FileNotFoundError:
        fail([f"Thesis not found: {args.id}"])
        return

    thoughts = []
    for tid in fm.get("thoughtIds") or []:
        try:
            tfm, tbody = vault.read_entity("thoughts", tid)
        except FileNotFoundError:
            continue
        thoughts.append(
            {
                "id": tid,
                "type": tfm.get("type"),
                "body": tbody,
                "findings": _findings_for(set(tfm.get("findingIds") or [])),
            }
        )

    signals = [
        {
            "id": sid,
            "category": sfm.get("category"),
            "metric": sfm.get("metric"),
            "period": sfm.get("period"),
            "value": sfm.get("value"),
            "unit": sfm.get("unit"),
            "validatesAssumption": sfm.get("validatesAssumption"),
        }
        for sid, sfm, _ in vault.list_entities("signals")
        if sfm.get("validatesThesisId") == args.id
    ]
    predictions = [
        {
            "id": pid,
            "statement": pfm.get("statement"),
            "horizon": pfm.get("horizon"),
            "probability": pfm.get("probability"),
            "outcome": pfm.get("outcome"),
            "resolvedAt": pfm.get("resolvedAt"),
        }
        for pid, pfm, _ in vault.list_entities("predictions")
        if pfm.get("thesisId") == args.id
    ]

    print(
        json.dumps(
            {
                "thesis": {**fm, "body": body},
                "thoughts": thoughts,
                "signals": signals,
                "predictions": predictions,
            },
            ensure_ascii=False,
        )
    )


def cmd_update_status(args: argparse.Namespace) -> None:
    try:
        fm, body = vault.read_entity("theses", args.id)
    except FileNotFoundError:
        fail([f"Thesis not found: {args.id}"])
        return

    current_status = fm["status"]
    if args.status == "dropped" and not args.confirm:
        via = "" if current_status == "challenged" else "（'challenged' を経ずに直接 dropped へ遷移しようとしています）"
        warn(f"'dropped' への遷移には確認が必要です{via}。--confirm を付けて再実行してください。")
        return

    now = vault.now_iso()
    new_body = body
    if args.note and args.note.strip():
        new_body = f"{body}\n\n---\n**status: {current_status} → {args.status}** ({now})\n\n{args.note.strip()}\n"

    fm["status"] = args.status
    fm["updatedAt"] = now
    vault.write_entity("theses", args.id, fm, body=new_body)
    idx.upsert("theses", {k: fm[k] for k in idx.TABLE_SCHEMAS["theses"].names})

    print(json.dumps(fm, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Thesis CRUD")
    sub = parser.add_subparsers(dest="command", required=True)

    p_register = sub.add_parser("register")
    p_register.add_argument("--id", required=True)
    p_register.add_argument("--company-id", required=True)
    p_register.add_argument("--statement", required=True)
    p_register.add_argument("--consensus-view", required=True)
    p_register.add_argument("--variant", required=True)
    p_register.add_argument("--why-mispriced", required=True)
    p_register.add_argument("--invalidation", required=True)
    p_register.add_argument("--confirmation", required=True)
    p_register.add_argument("--thought-ids", required=True)
    p_register.add_argument("--horizon")
    p_register.add_argument("--probability", type=float)
    p_register.add_argument("--body", required=True)
    p_register.add_argument("--tags")
    p_register.set_defaults(func=cmd_register)

    p_list = sub.add_parser("list")
    p_list.add_argument("--company-id")
    p_list.add_argument("--status", choices=STATUSES)
    p_list.set_defaults(func=cmd_list)

    p_view = sub.add_parser("view")
    p_view.add_argument("--id", required=True)
    p_view.set_defaults(func=cmd_view)

    p_update_status = sub.add_parser("update-status")
    p_update_status.add_argument("--id", required=True)
    p_update_status.add_argument("--status", required=True, choices=STATUSES)
    p_update_status.add_argument("--note")
    p_update_status.add_argument("--confirm", action="store_true")
    p_update_status.set_defaults(func=cmd_update_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
