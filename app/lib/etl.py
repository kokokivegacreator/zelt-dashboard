"""ETL orchestrator: detect file type, parse, upsert."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from . import parsers, db


def process_file(filepath: str | Path, file_bytes: bytes | None = None,
                 product_id_hint: str | None = None) -> dict:
    """
    Returns a dict: {file_type, date_range, rows_imported, target_tables, status, notes}
    Either pass a real path, or filename + bytes.
    """
    filename = Path(filepath).name
    df = pd.read_excel(file_bytes or filepath, sheet_name=0)
    cols = set(df.columns)

    ftype = parsers.detect_type(filename, cols)
    if not ftype:
        return {"file_type": None, "rows_imported": 0, "status": "skipped",
                "notes": f"Cannot detect file type for {filename}"}

    d1, d2 = parsers.extract_date_range(filename)
    snapshot = d1 or d2 or date.today()

    rows_imported = 0
    targets = []
    notes = []

    if ftype == "creator":
        creators, daily = parsers.parse_creator(df, snapshot)
        n1 = db.upsert("dim_creators", creators, on_conflict="username")
        n2 = db.upsert("fact_creator_daily", daily, on_conflict="date,creator_username")
        rows_imported = n2
        targets = ["dim_creators", "fact_creator_daily"]
        notes.append(f"creators={n1}, daily={n2}")

    elif ftype == "video":
        creators, videos = parsers.parse_video(df, snapshot)
        n1 = db.upsert("dim_creators", creators, on_conflict="username") if creators else 0
        n2 = db.upsert("fact_video", videos, on_conflict="video_id")
        rows_imported = n2
        targets = ["dim_creators", "fact_video"]
        notes.append(f"creators={n1}, videos={n2}")

    elif ftype == "live":
        creators, products, lives = parsers.parse_live(df)
        n1 = db.upsert("dim_creators", creators, on_conflict="username") if creators else 0
        n2 = db.upsert("dim_products", products, on_conflict="product_id") if products else 0
        n3 = db.upsert("fact_live", lives, on_conflict="live_id,product_id")
        rows_imported = n3
        targets = ["dim_creators", "dim_products", "fact_live"]
        notes.append(f"creators={n1}, products={n2}, lives={n3}")

    elif ftype == "product":
        products, daily = parsers.parse_product(df, snapshot)
        n1 = db.upsert("dim_products", products, on_conflict="product_id")
        n2 = db.upsert("fact_product_daily", daily, on_conflict="date,product_id")
        rows_imported = n2
        targets = ["dim_products", "fact_product_daily"]
        notes.append(f"products={n1}, daily={n2}")

    elif ftype == "product_creator":
        pid = product_id_hint or parsers.extract_product_id_from_path(str(filepath))
        if not pid:
            return {"file_type": ftype, "rows_imported": 0, "status": "failed",
                    "notes": "Cannot detect product_id from path/hint"}
        creators, daily = parsers.parse_product_creator(df, snapshot, pid)
        n1 = db.upsert("dim_creators", creators, on_conflict="username") if creators else 0
        n2 = db.upsert("fact_product_creator_daily", daily,
                       on_conflict="date,product_id,creator_username")
        rows_imported = n2
        targets = ["dim_creators", "fact_product_creator_daily"]
        notes.append(f"product_id={pid}, creators={n1}, rows={n2}")

    return {
        "file_type": ftype,
        "date_range": f"{d1}—{d2}" if d1 else None,
        "rows_imported": rows_imported,
        "target_tables": targets,
        "status": "ok",
        "notes": "; ".join(notes),
    }


def log_upload(filename: str, result: dict):
    db.upsert("upload_log", [{
        "filename": filename,
        "file_type": result.get("file_type"),
        "date_range": result.get("date_range"),
        "rows_imported": result.get("rows_imported", 0),
        "status": result.get("status"),
        "notes": result.get("notes"),
    }])
