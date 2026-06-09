from __future__ import annotations

import re
from datetime import date, datetime

import pandas as pd


def clean_currency(val) -> float:
    if pd.isna(val) or val in ("--", "", None):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = re.sub(r"[฿$,\s]", "", str(val))
    try:
        return float(s)
    except ValueError:
        return 0.0


def clean_percent(val) -> float:
    if pd.isna(val) or val in ("--", "", None):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).replace("%", "").strip()
    try:
        return float(s)
    except ValueError:
        return 0.0


def clean_int(val) -> int:
    if pd.isna(val) or val in ("--", "", None):
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    s = re.sub(r"[,\s]", "", str(val))
    try:
        return int(float(s))
    except ValueError:
        return 0


def fmt_currency(val: float) -> str:
    return f"฿{val:,.2f}"


def fmt_compact(val: float) -> str:
    if val >= 1_000_000:
        return f"฿{val/1_000_000:.2f}M"
    if val >= 1_000:
        return f"฿{val/1_000:.1f}K"
    return f"฿{val:,.0f}"


def fmt_percent(val: float) -> str:
    return f"{val:.2f}%"


def fmt_int(val: int) -> str:
    return f"{val:,}"


def parse_dt(val) -> datetime | None:
    if pd.isna(val) or not val:
        return None
    if isinstance(val, datetime):
        return val
    for fmt in ("%m/%d/%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(val), fmt)
        except ValueError:
            continue
    try:
        return pd.to_datetime(val).to_pydatetime()
    except Exception:
        return None


def parse_date(val) -> date | None:
    dt = parse_dt(val)
    return dt.date() if dt else None
