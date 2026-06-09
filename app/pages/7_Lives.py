import pandas as pd
import plotly.express as px
import streamlit as st

from lib import db, format as F, charts

st.set_page_config(page_title="Lives — Zelt", page_icon="📡", layout="wide")
st.title("Live Stream Performance")


@st.cache_data(ttl=300)
def load_lives():
    return pd.DataFrame(db.fetch_all("fact_live"))


ldf = load_lives()

if ldf.empty:
    st.warning("ยังไม่มีข้อมูล live")
    st.stop()

ldf["live_start_time"] = pd.to_datetime(ldf["live_start_time"])
ldf["live_date"] = ldf["live_start_time"].dt.date
ldf["hour"] = ldf["live_start_time"].dt.hour

# Aggregate per live (sum across products)
per_live = ldf.groupby(["live_id", "creator_username", "live_title", "live_date", "hour"]).agg(
    GMV=("creator_live_gmv", "sum"),
    Items=("live_items_sold", "sum"),
    Orders=("live_orders", "sum"),
    Commission=("est_commission", "sum"),
    Refunds=("refunds", "sum"),
).reset_index().sort_values("GMV", ascending=False)
per_live["AOV"] = (per_live["GMV"] / per_live["Orders"]).round(2).fillna(0)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Live Sessions", F.fmt_int(len(per_live)))
k2.metric("GMV รวม", F.fmt_compact(per_live["GMV"].sum()))
k3.metric("Items", F.fmt_int(int(per_live["Items"].sum())))
k4.metric("Avg AOV", F.fmt_currency(per_live["AOV"].mean()))

st.markdown("---")
st.subheader("Time-of-Day Heatmap")
heat = ldf.groupby(["live_date", "hour"])["creator_live_gmv"].sum().reset_index()
if not heat.empty:
    pivot = heat.pivot(index="hour", columns="live_date", values="creator_live_gmv").fillna(0)
    fig = px.imshow(pivot, aspect="auto", color_continuous_scale="OrRd",
                    title="GMV by Hour × Date")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Live Sessions")
display = per_live.copy()
display = display[["live_title", "creator_username", "live_date", "hour",
                   "GMV", "Items", "Orders", "AOV", "Commission"]]
display.columns = ["Title", "Creator", "Date", "Hour", "GMV", "Items",
                   "Orders", "AOV", "Commission"]
st.dataframe(display, hide_index=True, use_container_width=True,
             column_config={
                 "GMV": st.column_config.NumberColumn(format="฿%.2f"),
                 "AOV": st.column_config.NumberColumn(format="฿%.2f"),
                 "Commission": st.column_config.NumberColumn(format="฿%.2f"),
             })
