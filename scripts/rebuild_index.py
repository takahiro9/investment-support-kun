"""Rebuild data/index/ from scratch by rescanning data/vault/.

The index is a derived artifact; dropping and rebuilding it is always safe.
Run: uv run python scripts/rebuild_index.py
"""
from __future__ import annotations

import json

import pyarrow as pa

import index as idx
import predictions
import vault

# Entities whose Vault frontmatter fields line up 1:1 with their index schema
# (list-typed fields default to [] instead of None).
GENERIC_ENTITIES = [
    "sources",
    "findings",
    "thoughts",
    "themes",
    "theses",
    "signals",
    "strategy_recommendations",
    "investment_actions",
]


def _row_from_frontmatter(entity: str, fm: dict) -> dict:
    schema = idx.TABLE_SCHEMAS[entity]
    row = {}
    for field in schema:
        value = fm.get(field.name)
        if value is None and pa.types.is_list(field.type):
            value = []
        row[field.name] = value
    return row


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

    counts = {"sectors": len(sector_rows), "companies": len(company_rows)}
    if sector_rows:
        idx.get_table(db, "sectors").add(sector_rows)
    if company_rows:
        idx.get_table(db, "companies").add(company_rows)

    for entity in GENERIC_ENTITIES:
        rows = [_row_from_frontmatter(entity, fm) for _, fm, _ in vault.list_entities(entity)]
        counts[entity] = len(rows)
        if rows:
            idx.get_table(db, entity).add(rows)

    prediction_rows = [predictions._index_row(fm) for _, fm, _ in vault.list_entities("predictions")]
    counts["predictions"] = len(prediction_rows)
    if prediction_rows:
        idx.get_table(db, "predictions").add(prediction_rows)

    return counts


if __name__ == "__main__":
    print(json.dumps(rebuild(), ensure_ascii=False))
