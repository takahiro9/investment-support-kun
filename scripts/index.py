"""Secondary index (LanceDB): derived from the Vault, safe to delete/rebuild.

Provides fast aggregate queries, duplicate checks, and (later) vector search
over Vault entities. Never treat this as a source of truth — rebuild it from
data/vault/ via rebuild_index.py if it's ever missing or suspected stale.
"""
from __future__ import annotations

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
    """pandas/pyarrow round-trips list columns as numpy ndarrays; make them JSON-safe."""
    for record in records:
        for key, value in record.items():
            if hasattr(value, "tolist"):
                record[key] = value.tolist()
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
