import pandas as pd
import plotly.express as px
import streamlit as st

from lib import db, format as F, charts, style

st.set_page_config(page_title="Lives — Zelt", page_icon="📡", layout="wide")
style.inject_css()
style.sidebar_brand()


@st.cache_data(ttl=300)
def load_lives():
    return pd.DataFrame(db.fetch_all("fact_live"))


ldf = load_lives()

if ldf.empty:
    style.subpage_hero("LIVES", "Live Stream Performance", "ยังไม่มีข้อมูล")
    st.warning("ยังไม่มีข้อมูล live")
    st.stop()

ldf["live_start_time"] = pd.to_datetime(ldf["live_start_time"])
ldf["live_date"] = ldf["live_start_time"].dt.date
ldf["hour"] = ldf["live_start_time"].dt.hour

style.subpage_hero(
    eyebrow="LIVES",
    title="Live Stream Performance",
    subtitle="วิเคราะห์ live session • heatmap ช่วงเวลา • ranking",
)

per_live = ldf.groupby(["live_id", "creator_username", "live_title", "live_date", "hour"]).agg(
    GMV=("creator_live_gmv", "sum"),
    Items=("live_items_sold", "sum"),
    Orders=("live_orders", "sum"),
    Commission=("est_commission", "sum"),
    Refunds=("refunds", "sum"),
).reset_index().sort_values("GMV", ascending=False)
per_live["AOV"] = (per_live["GMV"] / per_live["Orders"]).round(2).fillna(0)

style.section_title("ภาพรวม")
k1, k2, k3, k4 = st.columns(4, gap="small")
k1.markdown(style.kpi_card("Live Sessions", F.fmt_int(len(per_live))), unsafe_allow_html=True)
k2.markdown(style.kpi_card("GMV รวม", F.fmt_compact(per_live["GMV"].sum())), unsafe_allow_html=True)
k3.markdown(style.kpi_card("Items", F.fmt_int(int(per_live["Items"].sum()))), unsafe_allow_html=True)
k4.markdown(style.kpi_card("Avg AOV", F.fmt_currency(per_live["AOV"].mean())), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
style.section_title("Heatmap ช่วงเวลา")

style.chart_card_open("GMV by Hour × Date", "ดูว่าช่วงเวลาไหนทำ GMV ได้สูง")
heat = ldf.groupby(["live_date", "hour"])["creator_live_gmv"].sum().reset_index()
if not heat.empty:
    pivot = heat.pivot(index="hour", columns="live_date", values="creator_live_gmv").fillna(0)
    sage_scale = [
        [0.0, "#FAF7F2"],
        [0.25, "#D4DBC5"],
        [0.5, "#A8B591"],
        [0.75, "#7A9B6E"],
        [1.0, "#324A28"],
    ]
    fig = px.imshow(pivot, aspect="auto", color_continuous_scale=sage_scale)
    charts._apply_theme(fig, height=420)
    fig.update_layout(coloraxis_colorbar=dict(title=""))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
style.chart_card_close()

st.markdown("<br>", unsafe_allow_html=True)
style.section_title("Live Sessions")

display = per_live.copy()
display = display[["live_title", "creator_username", "live_date", "hour",
                   "GMV", "Items", "Orders", "AOV", "Commission"]]
display.columns = ["Title", "Creator", "Date", "Hour", "GMV", "Items",
                   "Orders", "AOV", "Commission"]

style.chart_card_open(f"{len(per_live):,} session", "เรียงตาม GMV")
st.dataframe(display, hide_index=True, use_container_width=True,
             column_config={
                 "GMV": st.column_config.NumberColumn(format="฿%.2f"),
                 "AOV": st.column_config.NumberColumn(format="฿%.2f"),
                 "Commission": st.column_config.NumberColumn(format="฿%.2f"),
             })
style.chart_card_close()
