import pandas as pd
import plotly.express as px
import streamlit as st

from lib import db, format as F, charts, style

st.set_page_config(page_title="Month Comparison — Zelt", page_icon="📅", layout="wide")
style.inject_css()
style.sidebar_brand()


@st.cache_data(ttl=300)
def load_creator_daily():
    return pd.DataFrame(db.fetch_all("fact_creator_daily"))


@st.cache_data(ttl=300)
def load_product_daily():
    return pd.DataFrame(db.fetch_all("fact_product_daily"))


cdf = load_creator_daily()
pdf = load_product_daily()

if cdf.empty:
    style.subpage_hero("MONTH COMPARISON", "เทียบเดือน", "ยังไม่มีข้อมูล")
    st.warning("ยังไม่มีข้อมูล")
    st.stop()

cdf["date"] = pd.to_datetime(cdf["date"])
cdf["month"] = cdf["date"].dt.to_period("M").astype(str)
months = sorted(cdf["month"].unique(), reverse=True)

style.subpage_hero(
    eyebrow="MONTH COMPARISON",
    title="เทียบยอดระหว่างเดือน",
    subtitle=f"ข้อมูลทั้งหมด {len(months)} เดือน • เลือก 2-3 เดือนเพื่อเทียบ",
)

if len(months) < 2:
    st.info(f"มีข้อมูลแค่เดือนเดียว ({months[0]}) — อัพเดือนอื่นเพิ่มเพื่อเทียบค่ะ")

selected = st.multiselect("เลือกเดือน", months,
                          default=months[: min(2, len(months))])

if not selected:
    st.stop()

sub = cdf[cdf["month"].isin(selected)]
summary = sub.groupby("month").agg(
    GMV=("affiliate_gmv", "sum"),
    Orders=("affiliate_orders", "sum"),
    Live_GMV=("affiliate_live_gmv", "sum"),
    Video_GMV=("affiliate_video_gmv", "sum"),
    Refund_GMV=("affiliate_refunded_gmv", "sum"),
    Active_Creators=("creator_username", "nunique"),
).reset_index()
summary["AOV"] = (summary["GMV"] / summary["Orders"]).round(2)
summary["Refund_%"] = (summary["Refund_GMV"] / summary["GMV"] * 100).round(2)

style.section_title("KPI เทียบเดือน")
display = summary.copy()
for col in ["GMV", "Live_GMV", "Video_GMV", "Refund_GMV"]:
    display[col] = display[col].apply(F.fmt_compact)
display["AOV"] = display["AOV"].apply(lambda x: F.fmt_currency(x) if pd.notna(x) else "—")
display["Orders"] = display["Orders"].apply(F.fmt_int)
display["Refund_%"] = display["Refund_%"].astype(str) + "%"

style.chart_card_open("ตารางเทียบเดือน", "ตัวเลขรวมทั้งเดือนต่อเดือนที่เลือก")
st.dataframe(display, hide_index=True, use_container_width=True)
style.chart_card_close()

style.section_title("Trend ภาพรวม")
sub_daily = sub.groupby([sub["date"].dt.date, "month"])["affiliate_gmv"].sum().reset_index()
sub_daily.columns = ["date", "month", "GMV"]
sub_daily["day_of_month"] = pd.to_datetime(sub_daily["date"]).dt.day

style.chart_card_open("GMV รายวัน", "แกน X = วันที่ในเดือน (1-31)")
fig = px.line(sub_daily, x="day_of_month", y="GMV", color="month", markers=True,
              color_discrete_sequence=charts.PALETTE)
fig.update_traces(line=dict(width=3), marker=dict(size=7, line=dict(width=2, color="white")))
charts._apply_theme(fig, height=400)
fig.update_layout(hovermode="x unified", xaxis_title="วันที่")
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
style.chart_card_close()

style.section_title("Top Creators เทียบเดือน")
top_c = sub.groupby(["month", "creator_username"])["affiliate_gmv"].sum().reset_index()
top_c["rank"] = top_c.groupby("month")["affiliate_gmv"].rank(ascending=False, method="dense")
top_c = top_c[top_c["rank"] <= 10].sort_values(["month", "rank"])

style.chart_card_open("Top 10 Creators ต่อเดือน", "เรียงตาม GMV — แท่งสีคือเดือนที่เลือก")
fig2 = px.bar(top_c, x="affiliate_gmv", y="creator_username",
              color="month", barmode="group", orientation="h",
              color_discrete_sequence=charts.PALETTE)
charts._apply_theme(fig2, height=500)
st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
style.chart_card_close()
