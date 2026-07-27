"""Rebuild data/index/ from scratch by rescanning data/vault/.

The index is a derived artifact; dropping and rebuilding it is always safe.
Run: uv run python scripts/rebuild_index.py
"""
from __future__ import annotations

import json

import index as idx
import vault


def rebuild() -> dict:
    db = idx.connect()
    for name in idx.table_names(db):
        db.drop_table(name)

    sectors = vault.list_entities("sectors")
    companies = vault.list_entities("companies")

    company_count_by_sector: dict[str, int] = {}
    for _, fm, _ in companies:
        for sector_id in fm.get("sectorIds") or []:
            company_count_by_sector[sector_id] = company_count_by_sector.get(sector_id, 0) + 1

    sector_rows = [
        {
            "id": fm["id"],
            "name": fm["name"],
            "driverTreeTemplateCount": len(fm.get("driverTreeTemplate") or []),
            "companyCount": company_count_by_sector.get(fm["id"], 0),
            "createdAt": fm["createdAt"],
        }
        for _, fm, _ in sectors
    ]
    company_rows = [
        {
            "id": fm["id"],
            "ticker": fm["ticker"],
            "market": fm["market"],
            "name": fm["name"],
            "sectorIds": fm.get("sectorIds") or [],
            "primarySectorId": fm.get("primarySectorId"),
            "fiscalYearEnd": fm.get("fiscalYearEnd"),
            "createdAt": fm.get("createdAt"),
            "updatedAt": fm.get("updatedAt"),
        }
        for _, fm, _ in companies
    ]

    source_rows = [
        {k: fm.get(k) for k in idx.TABLE_SCHEMAS["sources"].names}
        for _, fm, _ in vault.list_entities("sources")
    ]
    finding_rows = [
        {k: fm.get(k) for k in idx.TABLE_SCHEMAS["findings"].names if k != "tags"}
        | {"tags": fm.get("tags") or []}
        for _, fm, _ in vault.list_entities("findings")
    ]
    thought_rows = [
        {
            "id": fm["id"],
            "findingIds": fm.get("findingIds") or [],
            "companyIds": fm.get("companyIds") or [],
            "sectorIds": fm.get("sectorIds") or [],
            "themeIds": fm.get("themeIds") or [],
            "driverNodeIds": fm.get("driverNodeIds") or [],
            "type": fm.get("type"),
            "createdAt": fm.get("createdAt"),
            "tags": fm.get("tags") or [],
        }
        for _, fm, _ in vault.list_entities("thoughts")
    ]

    if sector_rows:
        idx.get_table(db, "sectors").add(sector_rows)
    if company_rows:
        idx.get_table(db, "companies").add(company_rows)
    if source_rows:
        idx.get_table(db, "sources").add(source_rows)
    if finding_rows:
        idx.get_table(db, "findings").add(finding_rows)
    if thought_rows:
        idx.get_table(db, "thoughts").add(thought_rows)

    return {
        "sectors": len(sector_rows),
        "companies": len(company_rows),
        "sources": len(source_rows),
        "findings": len(finding_rows),
        "thoughts": len(thought_rows),
    }


if __name__ == "__main__":
    print(json.dumps(rebuild(), ensure_ascii=False))
