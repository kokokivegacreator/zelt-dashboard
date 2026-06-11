import pandas as pd
import streamlit as st

from lib import db, format as F, style

st.set_page_config(page_title="Videos — Zelt", page_icon="🎥", layout="wide")
style.inject_css()
style.sidebar_brand()


@st.cache_data(ttl=300)
def load_videos():
    return pd.DataFrame(db.fetch_all("fact_video"))


vdf = load_videos()

if vdf.empty:
    style.subpage_hero("VIDEOS", "Video Performance", "ยังไม่มีข้อมูล")
    st.warning("ยังไม่มีข้อมูล video")
    st.stop()

vdf["post_date"] = pd.to_datetime(vdf["post_date"]).dt.date

style.subpage_hero(
    eyebrow="VIDEOS",
    title="Video Performance",
    subtitle=f"{len(vdf):,} clip ทั้งหมดในระบบ",
)

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

style.section_title("ภาพรวม")
k1, k2, k3, k4 = st.columns(4, gap="small")
k1.markdown(style.kpi_card("จำนวน Video", F.fmt_int(len(view))), unsafe_allow_html=True)
k2.markdown(style.kpi_card("GMV รวม", F.fmt_compact(view["gmv"].sum())), unsafe_allow_html=True)
k3.markdown(style.kpi_card("Avg CTR", F.fmt_percent(view["affiliate_ctr"].mean())), unsafe_allow_html=True)
k4.markdown(style.kpi_card("Avg GPM", F.fmt_currency(view["shoppable_video_gpm"].mean())), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
style.section_title("ตาราง Videos")

display = view[[
    "video_name", "creator_username", "post_date", "gmv", "affiliate_items_sold",
    "affiliate_orders", "shoppable_video_impressions", "affiliate_ctr",
    "shoppable_video_gpm", "shoppable_video_likes", "shoppable_video_comments",
    "video_link",
]].copy()
display.columns = ["Title", "Creator", "Posted", "GMV", "Items", "Orders",
                   "Impressions", "CTR", "GPM", "Likes", "Comments", "Link"]

style.chart_card_open(f"พบ {len(view):,} clip", f"เรียงตาม {sort_by}")
st.dataframe(display, hide_index=True, use_container_width=True,
             column_config={
                 "Title": st.column_config.TextColumn(width="medium"),
                 "GMV": st.column_config.NumberColumn(format="฿%.2f"),
                 "GPM": st.column_config.NumberColumn(format="฿%.2f"),
                 "CTR": st.column_config.NumberColumn(format="%.2f%%"),
                 "Link": st.column_config.LinkColumn("TikTok", display_text="เปิด"),
             })
style.chart_card_close()
