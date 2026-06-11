from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from lib import db, format as F, charts, style

st.set_page_config(page_title="Overview — Zelt", page_icon="📊", layout="wide")
style.inject_css()
style.sidebar_brand()


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
    style.subpage_hero("OVERVIEW", "ภาพรวมการขาย", "ยังไม่มีข้อมูล")
    st.warning("ยังไม่มีข้อมูล — ไปหน้า Upload เพื่ออัพโหลดไฟล์ก่อนค่ะ")
    st.stop()

cdf["date"] = pd.to_datetime(cdf["date"]).dt.date
min_d, max_d = cdf["date"].min(), cdf["date"].max()

style.subpage_hero(
    eyebrow="OVERVIEW",
    title="ภาพรวมการขาย",
    subtitle=f"ข้อมูลตั้งแต่ {min_d:%d %b %Y} ถึง {max_d:%d %b %Y}",
)

c1, c2 = st.columns([2, 3])
with c1:
    d_range = st.date_input("ช่วงวันที่", value=(min_d, max_d),
                            min_value=min_d, max_value=max_d)

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


def delta_info(curr, prev):
    if not prev:
        return None, "flat"
    pct = (curr - prev) / prev * 100
    direction = "up" if pct > 0.5 else ("down" if pct < -0.5 else "flat")
    return f"{pct:+.1f}% vs ก่อนหน้า", direction


total_gmv = period["affiliate_gmv"].sum()
total_orders = int(period["affiliate_orders"].sum())
aov = (total_gmv / total_orders) if total_orders else 0
active_creators = period[period["affiliate_gmv"] > 0]["creator_username"].nunique()
refund = period["affiliate_refunded_gmv"].sum()
refund_rate = (refund / total_gmv * 100) if total_gmv else 0

prev_gmv = prev_period["affiliate_gmv"].sum()
prev_orders = int(prev_period["affiliate_orders"].sum())
prev_creators = prev_period[prev_period["affiliate_gmv"] > 0]["creator_username"].nunique()

style.section_title("KPI หลัก")

gmv_d, gmv_dir = delta_info(total_gmv, prev_gmv)
ord_d, ord_dir = delta_info(total_orders, prev_orders)
cr_d, cr_dir = delta_info(active_creators, prev_creators)

k1, k2, k3, k4, k5 = st.columns(5, gap="small")
k1.markdown(style.kpi_card("GMV รวม", F.fmt_compact(total_gmv), gmv_d, gmv_dir), unsafe_allow_html=True)
k2.markdown(style.kpi_card("ออเดอร์", F.fmt_int(total_orders), ord_d, ord_dir), unsafe_allow_html=True)
k3.markdown(style.kpi_card("AOV", F.fmt_currency(aov)), unsafe_allow_html=True)
k4.markdown(style.kpi_card("Active Creators", F.fmt_int(active_creators), cr_d, cr_dir), unsafe_allow_html=True)
k5.markdown(style.kpi_card("Refund %", F.fmt_percent(refund_rate)), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

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

daily_target = None
if target_val:
    days_in_m = pd.Timestamp(d_to).days_in_month
    daily_target = target_val / days_in_m

style.section_title("Trend & Mix")

style.chart_card_open("GMV รายวัน", "เทียบกับ daily target (เส้นทอง) ถ้าตั้งไว้")
st.plotly_chart(
    charts.line_trend(daily, "date", "GMV", title="", target=daily_target),
    use_container_width=True,
    config={"displayModeBar": False},
)
style.chart_card_close()

c1, c2 = st.columns(2, gap="medium")
with c1:
    style.chart_card_open("Channel Mix", "สัดส่วน GMV แยกตามช่องทาง")
    mix = pd.DataFrame({
        "Channel": ["Live", "Video", "Product Card"],
        "GMV": [daily["Live"].sum(), daily["Video"].sum(), daily["Card"].sum()],
    })
    st.plotly_chart(
        charts.donut(mix["Channel"].tolist(), mix["GMV"].tolist()),
        use_container_width=True,
        config={"displayModeBar": False},
    )
    style.chart_card_close()

with c2:
    style.chart_card_open("Top 5 Creators", "เรียงตาม GMV รวม")
    top_c = period.groupby("creator_username")["affiliate_gmv"].sum() \
        .sort_values(ascending=False).head(5)
    style.rank_list([(name, F.fmt_compact(val)) for name, val in top_c.items()])
    style.chart_card_close()

if not pdf.empty:
    style.section_title("Top Products")
    pdf["date"] = pd.to_datetime(pdf["date"]).dt.date
    p_period = pdf[(pdf["date"] >= d_from) & (pdf["date"] <= d_to)]
    top_p = p_period.groupby("product_id")["gmv"].sum() \
        .sort_values(ascending=False).head(5).reset_index()
    if not dim_p.empty:
        top_p = top_p.merge(dim_p[["product_id", "name"]], on="product_id", how="left")
        items = [(row.get("name") or row["product_id"], F.fmt_compact(row["gmv"]))
                 for _, row in top_p.iterrows()]
    else:
        items = [(row["product_id"], F.fmt_compact(row["gmv"]))
                 for _, row in top_p.iterrows()]
    style.chart_card_open("Top 5 Products", "เรียงตาม GMV รวมในช่วงที่เลือก")
    style.rank_list(items)
    style.chart_card_close()
