from __future__ import annotations

import re
from typing import Iterable

import pandas as pd


HASHTAG_RE = re.compile(r"#([^\s#]+)")


def extract_from_text(text: str) -> list[str]:
    if not text or not isinstance(text, str):
        return []
    return [h.lower() for h in HASHTAG_RE.findall(text)]


def normalize(tag: str) -> str:
    return tag.lstrip("#").strip().lower()


def videos_matching(videos_df: pd.DataFrame, tags: Iterable[str],
                    text_col: str = "video_name") -> pd.DataFrame:
    norm_tags = {normalize(t) for t in tags if t and normalize(t)}
    if not norm_tags or videos_df.empty:
        return videos_df.iloc[0:0].copy()

    def _match(text: str) -> bool:
        found = set(extract_from_text(text or ""))
        return bool(found & norm_tags)

    mask = videos_df[text_col].fillna("").apply(_match)
    return videos_df[mask].copy()


def matched_tags(text: str, tags: Iterable[str]) -> list[str]:
    norm_tags = {normalize(t) for t in tags}
    found = set(extract_from_text(text or ""))
    return sorted(found & norm_tags)


def parse_tag_input(raw: str) -> list[str]:
    if not raw:
        return []
    parts = re.split(r"[,\s]+", raw)
    return [normalize(p) for p in parts if normalize(p)]
