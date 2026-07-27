"""Secondary index (LanceDB): derived from the Vault, safe to delete/rebuild.

Provides fast aggregate queries, duplicate checks, and (later) vector search
over Vault entities. Never treat this as a source of truth — rebuild it from
data/vault/ via rebuild_index.py if it's ever missing or suspected stale.
"""
from __future__ import annotations

import math
from pathlib import Path

import lancedb
import pyarrow as pa

INDEX_ROOT = Path(__file__).resolve().parent.parent / "data" / "index"

TABLE_SCHEMAS: dict[str, pa.Schema] = {
    "sectors": pa.schema(
        [
            ("id", pa.string()),
            ("name", pa.string()),
            ("driverTreeTemplateCount", pa.int64()),
            ("companyCount", pa.int64()),
            ("createdAt", pa.string()),
        ]
    ),
    "companies": pa.schema(
        [
            ("id", pa.string()),
            ("ticker", pa.string()),
            ("market", pa.string()),
            ("name", pa.string()),
            ("sectorIds", pa.list_(pa.string())),
            ("primarySectorId", pa.string()),
            ("fiscalYearEnd", pa.string()),
            ("createdAt", pa.string()),
            ("updatedAt", pa.string()),
        ]
    ),
    "sources": pa.schema(
        [
            ("id", pa.string()),
            ("type", pa.string()),
            ("layer", pa.string()),
            ("companyId", pa.string()),
            ("sectorId", pa.string()),
            ("themeId", pa.string()),
            ("name", pa.string()),
            ("url", pa.string()),
            ("description", pa.string()),
            ("status", pa.string()),
            ("lastFetchedAt", pa.string()),
            ("createdAt", pa.string()),
            ("updatedAt", pa.string()),
        ]
    ),
    "findings": pa.schema(
        [
            ("id", pa.string()),
            ("type", pa.string()),
            ("title", pa.string()),
            ("url", pa.string()),
            ("sourceUrl", pa.string()),
            ("evidenceTier", pa.string()),
            ("savedAt", pa.string()),
            ("contentUpdatedAt", pa.string()),
            ("tags", pa.list_(pa.string())),
        ]
    ),
    "thoughts": pa.schema(
        [
            ("id", pa.string()),
            ("findingIds", pa.list_(pa.string())),
            ("companyIds", pa.list_(pa.string())),
            ("sectorIds", pa.list_(pa.string())),
            ("themeIds", pa.list_(pa.string())),
            ("driverNodeIds", pa.list_(pa.string())),
            ("type", pa.string()),
            ("createdAt", pa.string()),
            ("tags", pa.list_(pa.string())),
        ]
    ),
}


def connect() -> lancedb.DBConnection:
    INDEX_ROOT.mkdir(parents=True, exist_ok=True)
    return lancedb.connect(str(INDEX_ROOT))


def table_names(db: lancedb.DBConnection) -> list[str]:
    return db.list_tables().tables


def get_table(db: lancedb.DBConnection, entity_type: str):
    if entity_type in table_names(db):
        return db.open_table(entity_type)
    return db.create_table(entity_type, schema=TABLE_SCHEMAS[entity_type])


def upsert(entity_type: str, record: dict) -> None:
    db = connect()
    table = get_table(db, entity_type)
    table.delete(f"id = '{record['id']}'")
    table.add([record])


def _normalize(records: list[dict]) -> list[dict]:
    """pandas/pyarrow round-trips list columns as numpy ndarrays and nullable
    scalars as NaN; make both JSON-safe (arrays -> list, NaN -> None)."""
    for record in records:
        for key, value in record.items():
            if hasattr(value, "tolist"):
                record[key] = value.tolist()
            elif isinstance(value, float) and math.isnan(value):
                record[key] = None
    return records


def query_all(entity_type: str) -> list[dict]:
    db = connect()
    if entity_type not in table_names(db):
        return []
    return _normalize(get_table(db, entity_type).to_pandas().to_dict("records"))


def find_by(entity_type: str, **filters) -> list[dict]:
    """Equality filter on one or more columns. Small-scale, in-memory filter."""
    db = connect()
    if entity_type not in table_names(db):
        return []
    df = get_table(db, entity_type).to_pandas()
    for key, value in filters.items():
        df = df[df[key] == value]
    return _normalize(df.to_dict("records"))


def find_containing(entity_type: str, field: str, value: str) -> list[dict]:
    """Rows whose list-typed ``field`` contains ``value`` (e.g. companyIds)."""
    db = connect()
    if entity_type not in table_names(db):
        return []
    df = get_table(db, entity_type).to_pandas()
    df = df[df[field].apply(lambda values: value in list(values))]
    return _normalize(df.to_dict("records"))
