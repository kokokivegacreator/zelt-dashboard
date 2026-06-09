import pandas as pd
import streamlit as st

from lib import db, format as F

st.set_page_config(page_title="Videos — Zelt", page_icon="🎥", layout="wide")
st.title("Video Performance")


@st.cache_data(ttl=300)
def load_videos():
    return pd.DataFrame(db.fetch_all("fact_video"))


vdf = load_videos()

if vdf.empty:
    st.warning("ยังไม่มีข้อมูล video")
    st.stop()

vdf["post_date"] = pd.to_datetime(vdf["post_date"]).dt.date

c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    creators = ["(ทุกคน)"] + sorted(vdf["creator_username"].dropna().unique().tolist())
    creator_filter = st.selectbox("Creator", creators)
with c2:
    min_gmv = st.number_input("GMV ≥", min_value=0.0, value=0.0)
with c3:
    sort_by = st.selectbox("Sort by",
                           ["gmv", "shoppable_video_gpm", "affiliate_ctr",
                            "shoppable_video_impressions", "post_date"])

view = vdf.copy()
if creator_filter != "(ทุกคน)":
    view = view[view["creator_username"] == creator_filter]
view = view[view["gmv"] >= min_gmv]
view = view.sort_values(sort_by, ascending=False)

k1, k2, k3, k4 = st.columns(4)
k1.metric("จำนวน Video", F.fmt_int(len(view)))
k2.metric("GMV รวม", F.fmt_compact(view["gmv"].sum()))
k3.metric("Avg CTR", F.fmt_percent(view["affiliate_ctr"].mean()))
k4.metric("Avg GPM", F.fmt_currency(view["shoppable_video_gpm"].mean()))

display = view[[
    "video_name", "creator_username", "post_date", "gmv", "affiliate_items_sold",
    "affiliate_orders", "shoppable_video_impressions", "affiliate_ctr",
    "shoppable_video_gpm", "shoppable_video_likes", "shoppable_video_comments",
    "video_link",
]].copy()
display.columns = ["Title", "Creator", "Posted", "GMV", "Items", "Orders",
                   "Impressions", "CTR", "GPM", "Likes", "Comments", "Link"]

st.dataframe(display, hide_index=True, use_container_width=True,
             column_config={
                 "Title": st.column_config.TextColumn(width="medium"),
                 "GMV": st.column_config.NumberColumn(format="฿%.2f"),
                 "GPM": st.column_config.NumberColumn(format="฿%.2f"),
                 "CTR": st.column_config.NumberColumn(format="%.2f%%"),
                 "Link": st.column_config.LinkColumn("TikTok", display_text="เปิด"),
             })
