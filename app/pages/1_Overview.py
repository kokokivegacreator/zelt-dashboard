from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from lib import db, format as F, charts

st.set_page_config(page_title="Overview — Zelt", page_icon="📊", layout="wide")
st.title("Overview")


@st.cache_data(ttl=300)
def load_creator_daily():
    return pd.DataFrame(db.fetch_all("fact_creator_daily"))


@st.cache_data(ttl=300)
def load_product_daily():
    return pd.DataFrame(db.fetch_all("fact_product_daily"))


@st.cache_data(ttl=300)
def load_dim_products():
    return pd.DataFrame(db.fetch_all("dim_products"))


@st.cache_data(ttl=300)
def load_targets_monthly():
    return pd.DataFrame(db.fetch_all("targets_monthly"))


cdf = load_creator_daily()
pdf = load_product_daily()
dim_p = load_dim_products()
tgt = load_targets_monthly()

if cdf.empty:
    st.warning("ยังไม่มีข้อมูล — ไปหน้า Upload เพื่ออัพโหลดไฟล์ก่อนค่ะ")
    st.stop()

cdf["date"] = pd.to_datetime(cdf["date"]).dt.date

min_d, max_d = cdf["date"].min(), cdf["date"].max()
c1, c2 = st.columns([2, 1])
with c1:
    d_range = st.date_input("ช่วงวันที่", value=(min_d, max_d),
                            min_value=min_d, max_value=max_d)
with c2:
    st.write("")
    st.write("")
    st.caption(f"ข้อมูล: {min_d} → {max_d}")

if isinstance(d_range, tuple) and len(d_range) == 2:
    d_from, d_to = d_range
else:
    d_from, d_to = min_d, max_d

mask = (cdf["date"] >= d_from) & (cdf["date"] <= d_to)
period = cdf[mask]

prev_len = (d_to - d_from).days + 1
prev_to = d_from - timedelta(days=1)
prev_from = prev_to - timedelta(days=prev_len - 1)
prev_mask = (cdf["date"] >= prev_from) & (cdf["date"] <= prev_to)
prev_period = cdf[prev_mask]


def pct_change(curr, prev):
    if not prev:
        return None
    return f"{((curr - prev) / prev * 100):+.1f}%"


total_gmv = period["affiliate_gmv"].sum()
total_orders = period["affiliate_orders"].sum()
aov = (total_gmv / total_orders) if total_orders else 0
active_creators = period[period["affiliate_gmv"] > 0]["creator_username"].nunique()
refund = period["affiliate_refunded_gmv"].sum()
refund_rate = (refund / total_gmv * 100) if total_gmv else 0

prev_gmv = prev_period["affiliate_gmv"].sum()
prev_orders = prev_period["affiliate_orders"].sum()
prev_creators = prev_period[prev_period["affiliate_gmv"] > 0]["creator_username"].nunique()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("GMV รวม", F.fmt_compact(total_gmv), pct_change(total_gmv, prev_gmv))
k2.metric("ออเดอร์", F.fmt_int(int(total_orders)), pct_change(total_orders, prev_orders))
k3.metric("AOV", F.fmt_currency(aov))
k4.metric("Active Creators", F.fmt_int(active_creators), pct_change(active_creators, prev_creators))
k5.metric("Refund %", F.fmt_percent(refund_rate))

st.markdown("---")

# Target line for current month
target_val = None
if not tgt.empty:
    tgt["month"] = pd.to_datetime(tgt["month"]).dt.to_period("M")
    cur_m = pd.Timestamp(d_to).to_period("M")
    row = tgt[tgt["month"] == cur_m]
    if not row.empty:
        target_val = float(row["target_gmv"].iloc[0])

daily = period.groupby("date").agg(
    GMV=("affiliate_gmv", "sum"),
    Live=("affiliate_live_gmv", "sum"),
    Video=("affiliate_video_gmv", "sum"),
    Card=("affiliate_product_card_gmv", "sum"),
).reset_index()

# Daily target = monthly target / days in month
daily_target = None
if target_val:
    days_in_m = pd.Timestamp(d_to).days_in_month
    daily_target = target_val / days_in_m

st.subheader("Trend รายวัน")
st.plotly_chart(charts.line_trend(daily, "date", "GMV",
                                   title="GMV รายวัน", target=daily_target),
                use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    st.subheader("Channel Mix")
    mix = pd.DataFrame({
        "Channel": ["Live", "Video", "Product Card"],
        "GMV": [daily["Live"].sum(), daily["Video"].sum(), daily["Card"].sum()],
    })
    st.plotly_chart(charts.donut(mix["Channel"].tolist(), mix["GMV"].tolist()),
                    use_container_width=True)

with c2:
    st.subheader("Top 5 Creators")
    top_c = period.groupby("creator_username")["affiliate_gmv"].sum() \
        .sort_values(ascending=False).head(5).reset_index()
    top_c.columns = ["Creator", "GMV"]
    top_c["GMV"] = top_c["GMV"].round(2)
    st.dataframe(top_c, hide_index=True, use_container_width=True)

if not pdf.empty:
    st.subheader("Top 5 Products")
    pdf["date"] = pd.to_datetime(pdf["date"]).dt.date
    p_period = pdf[(pdf["date"] >= d_from) & (pdf["date"] <= d_to)]
    top_p = p_period.groupby("product_id")["gmv"].sum() \
        .sort_values(ascending=False).head(5).reset_index()
    if not dim_p.empty:
        top_p = top_p.merge(dim_p[["product_id", "name"]], on="product_id", how="left")
    top_p["gmv"] = top_p["gmv"].round(2)
    st.dataframe(top_p[["name", "gmv"]] if "name" in top_p else top_p,
                 hide_index=True, use_container_width=True)
