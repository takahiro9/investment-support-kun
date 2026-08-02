"""CRUD for Source. Usage:

  uv run python scripts/sources.py register --id <uuid> \\
      --type disclosure_feed --layer company --company-id <uuid> \\
      --name "サンプル株式会社 適時開示" --url "https://..." \\
      [--description "任意のメモ"] [--force] [--body "任意の本文"]
  uv run python scripts/sources.py list [--layer <layer>] [--company-id <uuid>] \\
      [--sector-id <uuid>] [--theme-id <uuid>]
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from urllib.error import HTTPError, URLError

import index as idx
import vault

TYPES = ["rss_feed", "web_page", "youtube_channel", "disclosure_feed", "newsletter"]
LAYERS = ["company", "sector", "theme", "macro"]

# layer -> (frontmatter field, vault entity dir to check existence against, required)
LAYER_REF = {
    "company": ("companyId", "companies"),
    "sector": ("sectorId", "sectors"),
    "theme": ("themeId", "themes"),
    "macro": (None, None),
}


def fail(errors: list[str]) -> None:
    print(json.dumps({"errors": errors}, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)


def warn(message: str) -> None:
    print(json.dumps({"warning": message, "requiresForce": True}, ensure_ascii=False), file=sys.stderr)
    sys.exit(2)


def _request(url: str, method: str) -> None:
    req = urllib.request.Request(url, method=method, headers={"User-Agent": "curiospector-source-check/1.0"})
    with urllib.request.urlopen(req, timeout=5):
        pass


def _check_reachable(url: str) -> str | None:
    """Best-effort connectivity check. Returns an error message, or None if reachable."""
    try:
        _request(url, "HEAD")
        return None
    except HTTPError as e:
        if e.code == 405:
            # Some servers reject HEAD outright; retry with GET before giving up.
            try:
                _request(url, "GET")
                return None
            except HTTPError as e2:
                return f"HTTP {e2.code}"
            except URLError as e2:
                return str(e2.reason)
        return f"HTTP {e.code}"
    except URLError as e:
        return str(e.reason)
    except Exception as e:  # noqa: BLE001 - surfaced to the investor as a warning, not a crash
        return str(e)


def cmd_register(args: argparse.Namespace) -> None:
    errors = []
    if not args.name.strip():
        errors.append("name must not be empty")
    if not args.url.strip():
        errors.append("url must not be empty")

    ref_field, ref_entity = LAYER_REF[args.layer]
    ref_value = {"company": args.company_id, "sector": args.sector_id, "theme": args.theme_id}.get(args.layer)
    if ref_field and not ref_value:
        errors.append(f"layer '{args.layer}' requires {ref_field}")
    if errors:
        fail(errors)

    if ref_field and ref_entity:
        try:
            vault.read_entity(ref_entity, ref_value)
        except FileNotFoundError:
            label = {"companies": "Company", "sectors": "Sector", "themes": "Theme"}[ref_entity]
            fail([f"{label} not found: {ref_value}"])
            return

    if idx.find_by("sources", url=args.url):
        fail([f"a Source with url '{args.url}' is already registered"])

    if not args.force:
        problem = _check_reachable(args.url)
        if problem:
            warn(f"url may not be reachable ({problem}). Re-run with --force to register anyway.")
            return

    now = vault.now_iso()
    frontmatter = {
        "id": args.id,
        "type": args.type,
        "layer": args.layer,
        "companyId": args.company_id if args.layer == "company" else None,
        "sectorId": args.sector_id if args.layer == "sector" else None,
        "themeId": args.theme_id if args.layer == "theme" else None,
        "name": args.name,
        "url": args.url,
        "description": args.description or None,
        "status": "active",
        "lastFetchedAt": None,
        "createdAt": now,
        "updatedAt": now,
    }
    vault.write_entity("sources", args.id, frontmatter, body=args.body or "")
    idx.upsert("sources", {k: frontmatter[k] for k in idx.TABLE_SCHEMAS["sources"].names})
    print(json.dumps(frontmatter, ensure_ascii=False))


def cmd_list(args: argparse.Namespace) -> None:
    rows = idx.query_all("sources")
    if args.layer:
        rows = [r for r in rows if r.get("layer") == args.layer]
    if args.company_id:
        rows = [r for r in rows if r.get("companyId") == args.company_id]
    if args.sector_id:
        rows = [r for r in rows if r.get("sectorId") == args.sector_id]
    if args.theme_id:
        rows = [r for r in rows if r.get("themeId") == args.theme_id]
    print(json.dumps(rows, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Source CRUD")
    sub = parser.add_subparsers(dest="command", required=True)

    p_register = sub.add_parser("register")
    p_register.add_argument("--id", required=True)
    p_register.add_argument("--type", required=True, choices=TYPES)
    p_register.add_argument("--layer", required=True, choices=LAYERS)
    p_register.add_argument("--company-id")
    p_register.add_argument("--sector-id")
    p_register.add_argument("--theme-id")
    p_register.add_argument("--name", required=True)
    p_register.add_argument("--url", required=True)
    p_register.add_argument("--description")
    p_register.add_argument("--force", action="store_true", help="skip the connectivity check and register regardless")
    p_register.add_argument("--body")
    p_register.set_defaults(func=cmd_register)

    p_list = sub.add_parser("list")
    p_list.add_argument("--layer", choices=LAYERS)
    p_list.add_argument("--company-id")
    p_list.add_argument("--sector-id")
    p_list.add_argument("--theme-id")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
