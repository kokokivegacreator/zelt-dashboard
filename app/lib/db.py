from __future__ import annotations

import os
import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_client() -> Client:
    url = st.secrets.get("SUPABASE_URL") or os.environ["SUPABASE_URL"]
    key = st.secrets.get("SUPABASE_KEY") or os.environ["SUPABASE_KEY"]
    return create_client(url, key)


def fetch_all(table: str, select: str = "*", filters: dict | None = None,
              order: str | None = None, limit: int | None = None):
    q = get_client().table(table).select(select)
    if filters:
        for col, val in filters.items():
            if isinstance(val, tuple) and len(val) == 2:
                op, v = val
                q = getattr(q, op)(col, v)
            else:
                q = q.eq(col, val)
    if order:
        desc = order.startswith("-")
        q = q.order(order.lstrip("-"), desc=desc)
    if limit:
        q = q.limit(limit)

    rows, offset, page = [], 0, 1000
    while True:
        r = q.range(offset, offset + page - 1).execute()
        rows.extend(r.data)
        if len(r.data) < page:
            break
        offset += page
    return rows


def delete(table: str, filters: dict) -> int:
    client = get_client()
    q = client.table(table).delete()
    for col, val in filters.items():
        q = q.eq(col, val)
    r = q.execute()
    return len(r.data or [])


def update(table: str, values: dict, filters: dict) -> int:
    client = get_client()
    q = client.table(table).update(values)
    for col, val in filters.items():
        q = q.eq(col, val)
    r = q.execute()
    return len(r.data or [])


def upsert(table: str, rows: list[dict], on_conflict: str | None = None, chunk: int = 500):
    if not rows:
        return 0
    client = get_client()
    total = 0
    for i in range(0, len(rows), chunk):
        batch = rows[i:i + chunk]
        q = client.table(table).upsert(batch, on_conflict=on_conflict) if on_conflict \
            else client.table(table).upsert(batch)
        r = q.execute()
        total += len(r.data or batch)
    return total
