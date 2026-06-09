"""Auto-detect Excel file type + parse to DB rows."""
from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

import pandas as pd

from . import format as F


FILE_TYPES = {
    "creator": {
        "filename_pattern": r"Creator_List_",
        "signature_cols": {"Creator username", "Affiliate GMV"},
        "target_table": "fact_creator_daily",
    },
    "video": {
        "filename_pattern": r"Video_List_",
        "signature_cols": {"Video name", "Video link", "Creator username"},
        "target_table": "fact_video",
    },
    "live": {
        "filename_pattern": r"Transaction_Analysis_Live_List_",
        "signature_cols": {"LIVE ID", "LIVE title", "Creator name"},
        "target_table": "fact_live",
    },
    "product": {
        "filename_pattern": r"ListProducts_",
        "signature_cols": {"Product ID", "Product name", "GMV"},
        "target_table": "fact_product_daily",
    },
    "product_creator": {
        "filename_pattern": r"ListCreators_",
        "signature_cols": {"Creator Name", "Creator Nickname"},
        "target_table": "fact_product_creator_daily",
    },
}

DATE_RANGE_RE = re.compile(r"(\d{4})[-]?(\d{2})[-]?(\d{2})[-_](\d{4})[-]?(\d{2})[-]?(\d{2})")


def extract_date_range(filename: str) -> tuple[date | None, date | None]:
    m = DATE_RANGE_RE.search(filename)
    if not m:
        return None, None
    y1, mo1, d1, y2, mo2, d2 = m.groups()
    try:
        return date(int(y1), int(mo1), int(d1)), date(int(y2), int(mo2), int(d2))
    except ValueError:
        return None, None


def detect_type(filename: str, columns: set[str]) -> str | None:
    base = Path(filename).name
    candidates = []
    for ftype, spec in FILE_TYPES.items():
        name_match = re.search(spec["filename_pattern"], base, re.IGNORECASE) is not None
        col_match = spec["signature_cols"].issubset(columns)
        if name_match and col_match:
            candidates.append(ftype)
        elif col_match:
            candidates.append(ftype)
    if not candidates:
        return None
    # Prefer product_creator over creator when in product subfolder
    if "product_creator" in candidates:
        return "product_creator"
    return candidates[0]


def extract_product_id_from_path(path: str) -> str | None:
    parts = Path(path).parts
    for p in parts:
        if p.isdigit() and len(p) >= 15:
            return p
    return None


# ---------- Parsers ----------

def parse_creator(df: pd.DataFrame, snapshot_date: date) -> tuple[list[dict], list[dict]]:
    creators, daily = [], []
    for _, row in df.iterrows():
        username = str(row.get("Creator username", "")).strip()
        if not username or username.lower() == "nan":
            continue
        followers = F.clean_int(row.get("Affiliate followers", 0))
        creators.append({
            "username": username,
            "followers": followers,
            "first_seen": snapshot_date.isoformat(),
            "last_seen": snapshot_date.isoformat(),
        })
        daily.append({
            "date": snapshot_date.isoformat(),
            "creator_username": username,
            "affiliate_gmv": F.clean_currency(row.get("Affiliate GMV")),
            "affiliate_live_gmv": F.clean_currency(row.get("Affiliate LIVE GMV")),
            "affiliate_video_gmv": F.clean_currency(row.get("Affiliate shoppable video GMV")),
            "affiliate_product_card_gmv": F.clean_currency(row.get("Affiliate product card GMV")),
            "affiliate_products_sold": F.clean_int(row.get("Affiliate products sold")),
            "items_sold": F.clean_int(row.get("Items sold")),
            "est_commission": F.clean_currency(row.get("Est. commission")),
            "est_flat_fee": F.clean_currency(row.get("Est. flat fee")),
            "avg_order_value": F.clean_currency(row.get("Avg. order value")),
            "affiliate_product_showcase": F.clean_int(row.get("Affiliate product showcase")),
            "affiliate_orders": F.clean_int(row.get("Affiliate orders")),
            "ctr": F.clean_percent(row.get("CTR")),
            "product_impressions": F.clean_int(row.get("Product impressions")),
            "avg_affiliate_customers": F.clean_currency(row.get("Avg. affiliate customers")),
            "affiliate_live_streams": F.clean_int(row.get("Affiliate LIVE streams")),
            "affiliate_shoppable_videos": F.clean_int(row.get("Affiliate shoppable videos")),
            "target_collab_gmv": F.clean_currency(row.get("Target collaboration GMV")),
            "target_collab_est_commission": F.clean_currency(row.get("Target collaboration est. commission")),
            "open_collab_gmv": F.clean_currency(row.get("Open collaboration GMV")),
            "open_collab_est_commission": F.clean_currency(row.get("Open collaboration est. commission")),
            "affiliate_refunded_gmv": F.clean_currency(row.get("Affiliate refunded GMV")),
            "affiliate_items_refunded": F.clean_int(row.get("Affiliate items refunded")),
            "affiliate_followers": followers,
        })
    return creators, daily


def parse_video(df: pd.DataFrame, snapshot_date: date) -> tuple[list[dict], list[dict]]:
    creators_seen = {}
    videos_map = {}  # dedupe by video_id, keep highest GMV
    for _, row in df.iterrows():
        link = str(row.get("Video link", "")).strip()
        if not link or link.lower() == "nan":
            continue
        m = re.search(r"/video/(\d+)", link)
        video_id = m.group(1) if m else link
        username = str(row.get("Creator username", "")).strip()
        if username and username.lower() != "nan":
            creators_seen[username] = {
                "username": username,
                "first_seen": snapshot_date.isoformat(),
                "last_seen": snapshot_date.isoformat(),
            }
        rec = {
            "video_id": video_id,
            "video_link": link,
            "video_name": str(row.get("Video name", ""))[:5000],
            "post_date": (F.parse_date(row.get("Video post date")) or snapshot_date).isoformat(),
            "snapshot_date": snapshot_date.isoformat(),
            "creator_username": username if username and username.lower() != "nan" else None,
            "gmv": F.clean_currency(row.get("GMV")),
            "affiliate_items_sold": F.clean_int(row.get("Affiliate items sold ", row.get("Affiliate items sold"))),
            "affiliate_shoppable_video_gmv": F.clean_currency(row.get("Affiliate shoppable video GMV")),
            "shoppable_video_aov": F.clean_currency(row.get("Shoppable video avg. order value")),
            "est_commission": F.clean_currency(row.get("Est. commission")),
            "est_flat_fee": F.clean_currency(row.get("Est. flat fee")),
            "affiliate_orders": F.clean_int(row.get("Affiliate orders")),
            "shoppable_video_impressions": F.clean_int(row.get("Shoppable video impressions")),
            "affiliate_ctr": F.clean_percent(row.get("Affiliate CTR")),
            "shoppable_video_gpm": F.clean_currency(row.get("Shoppable video GPM")),
            "affiliate_items_refunded": F.clean_int(row.get("Affiliate items refunded")),
            "affiliate_refunded_gmv": F.clean_currency(row.get("Affiliate refunded GMV")),
            "shoppable_video_comments": F.clean_int(row.get("Shoppable video comments")),
            "shoppable_video_likes": F.clean_int(row.get("Shoppable video likes")),
        }
        prev = videos_map.get(video_id)
        if prev is None or rec["gmv"] >= prev["gmv"]:
            videos_map[video_id] = rec
    return list(creators_seen.values()), list(videos_map.values())


def parse_live(df: pd.DataFrame) -> tuple[list[dict], list[dict], list[dict]]:
    creators, products, lives_map = {}, {}, {}
    for _, row in df.iterrows():
        live_id = str(row.get("LIVE ID", "")).strip()
        product_id = str(row.get("Product ID", "")).strip()
        if not live_id or live_id.lower() == "nan":
            continue
        creator = str(row.get("Creator name", "")).strip()
        if creator and creator.lower() != "nan":
            creators[creator] = {"username": creator}
        if product_id and product_id.lower() != "nan":
            products[product_id] = {
                "product_id": product_id,
                "name": str(row.get("Product name", ""))[:1000],
            }
        start = F.parse_dt(row.get("LIVE start time"))
        end = F.parse_dt(row.get("LIVE end time"))
        key = (live_id, product_id or "")
        rec = {
            "live_id": live_id,
            "product_id": product_id if product_id and product_id.lower() != "nan" else None,
            "creator_username": creator if creator and creator.lower() != "nan" else None,
            "live_title": str(row.get("LIVE title", ""))[:1000] if not pd.isna(row.get("LIVE title")) else None,
            "live_start_time": start.isoformat() if start else None,
            "live_end_time": end.isoformat() if end else None,
            "product_name": str(row.get("Product name", ""))[:1000],
            "creator_live_gmv": F.clean_currency(row.get("Creator LIVE-attributed GMV")),
            "live_items_sold": F.clean_int(row.get("LIVE-attributed items sold")),
            "refunds": F.clean_currency(row.get("Refunds")),
            "items_refunded": F.clean_int(row.get("Items refunded")),
            "live_orders": F.clean_int(row.get("LIVE-attributed orders")),
            "aov": F.clean_currency(row.get("AOV")),
            "est_commission": F.clean_currency(row.get("Est. commission")),
        }
        prev = lives_map.get(key)
        if prev is None or rec["creator_live_gmv"] >= prev["creator_live_gmv"]:
            lives_map[key] = rec
    return list(creators.values()), list(products.values()), list(lives_map.values())


def parse_product(df: pd.DataFrame, snapshot_date: date) -> tuple[list[dict], list[dict]]:
    products, daily = [], []
    for _, row in df.iterrows():
        pid = str(row.get("Product ID", "")).strip()
        if not pid or pid.lower() == "nan":
            continue
        products.append({
            "product_id": pid,
            "name": str(row.get("Product name", ""))[:1000],
            "first_seen": snapshot_date.isoformat(),
            "last_seen": snapshot_date.isoformat(),
        })
        daily.append({
            "date": snapshot_date.isoformat(),
            "product_id": pid,
            "gmv": F.clean_currency(row.get("GMV")),
            "items_sold": F.clean_int(row.get("Items sold")),
            "est_commission": F.clean_currency(row.get("Est. commission")),
            "samples": F.clean_int(row.get("Samples")),
            "sales_creator": F.clean_int(row.get("Sales creator")),
            "live_streams": F.clean_int(row.get("LIVE streams")),
            "videos": F.clean_int(row.get("Videos")),
            "refunded_gmv": F.clean_currency(row.get("Refunded GMV")),
            "refunded_items_sold": F.clean_int(row.get("Refunded items sold")),
            "est_flat_fee": F.clean_currency(row.get("Est. flat fee")),
        })
    return products, daily


def parse_product_creator(df: pd.DataFrame, snapshot_date: date, product_id: str) -> tuple[list[dict], list[dict]]:
    creators, daily = [], []
    for _, row in df.iterrows():
        username = str(row.get("Creator Name", "")).strip()
        if not username or username.lower() == "nan":
            continue
        nickname = str(row.get("Creator Nickname", "")).strip()
        creators.append({
            "username": username,
            "nickname": nickname if nickname.lower() != "nan" else None,
            "first_seen": snapshot_date.isoformat(),
            "last_seen": snapshot_date.isoformat(),
        })
        daily.append({
            "date": snapshot_date.isoformat(),
            "product_id": product_id,
            "creator_username": username,
            "creator_nickname": nickname if nickname.lower() != "nan" else None,
            "gmv": F.clean_currency(row.get("GMV")),
            "items_sold": F.clean_int(row.get("Items sold")),
            "videos": F.clean_int(row.get("Videos")),
            "live_streams": F.clean_int(row.get("LIVE streams")),
            "est_commission": F.clean_currency(row.get("Est. commission")),
            "samples": F.clean_int(row.get("Samples")),
            "refunded_gmv": F.clean_currency(row.get("Refunded GMV")),
            "refunded_items_sold": F.clean_int(row.get("Refunded items sold")),
            "est_flat_fee": F.clean_currency(row.get("Est. flat fee")),
        })
    return creators, daily
