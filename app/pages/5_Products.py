import pandas as pd
import plotly.express as px
import streamlit as st

from lib import db, format as F, charts, style

st.set_page_config(page_title="Products — Zelt", page_icon="📦", layout="wide")
style.inject_css()
style.sidebar_brand()


@st.cache_data(ttl=300)
def load_product_daily():
    return pd.DataFrame(db.fetch_all("fact_product_daily"))


@st.cache_data(ttl=300)
def load_dim_products():
    return pd.DataFrame(db.fetch_all("dim_products"))


@st.cache_data(ttl=300)
def load_product_creator():
    return pd.DataFrame(db.fetch_all("fact_product_creator_daily"))


pdf = load_product_daily()
dim_p = load_dim_products()

if pdf.empty:
    style.subpage_hero("PRODUCTS", "Product Performance", "ยังไม่มีข้อมูล")
    st.warning("ยังไม่มีข้อมูล product")
    st.stop()

pdf["date"] = pd.to_datetime(pdf["date"]).dt.date
min_d, max_d = pdf["date"].min(), pdf["date"].max()

style.subpage_hero(
    eyebrow="PRODUCTS",
    title="Product Performance",
    subtitle=f"{len(dim_p)} SKU • ข้อมูลตั้งแต่ {min_d:%d %b %Y} ถึง {max_d:%d %b %Y}",
)

c1, _ = st.columns([2, 3])
with c1:
    d_range = st.date_input("ช่วงวันที่", value=(min_d, max_d),
                            min_value=min_d, max_value=max_d, key="product_date")
if isinstance(d_range, tuple) and len(d_range) == 2:
    d_from, d_to = d_range
else:
    d_from, d_to = min_d, max_d

period = pdf[(pdf["date"] >= d_from) & (pdf["date"] <= d_to)]
agg = period.groupby("product_id").agg(
    GMV=("gmv", "sum"),
    Items=("items_sold", "sum"),
    Commission=("est_commission", "sum"),
    Lives=("live_streams", "sum"),
    Videos=("videos", "sum"),
    Creators=("sales_creator", "max"),
    Refund_GMV=("refunded_gmv", "sum"),
).reset_index().sort_values("GMV", ascending=False)
if not dim_p.empty:
    agg = agg.merge(dim_p[["product_id", "name"]], on="product_id", how="left")

style.section_title("ภาพรวม")
k1, k2, k3, k4 = st.columns(4, gap="small")
k1.markdown(style.kpi_card("SKU", F.fmt_int(len(agg))), unsafe_allow_html=True)
k2.markdown(style.kpi_card("GMV รวม", F.fmt_compact(agg["GMV"].sum())), unsafe_allow_html=True)
k3.markdown(style.kpi_card("Items", F.fmt_int(int(agg["Items"].sum()))), unsafe_allow_html=True)
k4.markdown(style.kpi_card("Commission", F.fmt_compact(agg["Commission"].sum())), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
style.section_title("Products Summary")

style.chart_card_open("ทุก SKU ในช่วงที่เลือก", "เรียงตาม GMV จากมากไปน้อย")
st.dataframe(agg, hide_index=True, use_container_width=True,
             column_config={
                 "GMV": st.column_config.NumberColumn(format="฿%.2f"),
                 "Commission": st.column_config.NumberColumn(format="฿%.2f"),
                 "Refund_GMV": st.column_config.NumberColumn(format="฿%.2f"),
             })
style.chart_card_close()

st.markdown("<br>", unsafe_allow_html=True)
style.section_title("Drill-down")

options = agg["product_id"].tolist()
display_map = dict(zip(agg["product_id"], agg.get("name", agg["product_id"])))
selected = st.selectbox("เลือก product", options=options,
                        format_func=lambda x: f"{display_map.get(x, x)[:80]}")

if selected:
    sub = period[period["product_id"] == selected].sort_values("date")

    k1, k2, k3 = st.columns(3, gap="small")
    k1.markdown(style.kpi_card("GMV", F.fmt_compact(sub["gmv"].sum())), unsafe_allow_html=True)
    k2.markdown(style.kpi_card("Items", F.fmt_int(int(sub["items_sold"].sum()))), unsafe_allow_html=True)
    k3.markdown(style.kpi_card("Commission", F.fmt_currency(sub["est_commission"].sum())), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    style.chart_card_open("GMV รายวัน", "")
    fig = px.line(sub, x="date", y="gmv", markers=True,
                  color_discrete_sequence=charts.PALETTE)
    fig.update_traces(line=dict(width=3), marker=dict(size=7, line=dict(width=2, color="white")))
    charts._apply_theme(fig, height=350)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    style.chart_card_close()

    pc = load_product_creator()
    if not pc.empty:
        pc["date"] = pd.to_datetime(pc["date"]).dt.date
        pc_sub = pc[(pc["product_id"] == selected) &
                    (pc["date"] >= d_from) & (pc["date"] <= d_to)]
        if not pc_sub.empty:
            ctable = pc_sub.groupby(["creator_username", "creator_nickname"]).agg(
                GMV=("gmv", "sum"), Items=("items_sold", "sum"),
                Videos=("videos", "sum"), Lives=("live_streams", "sum"),
                Commission=("est_commission", "sum"),
            ).reset_index().sort_values("GMV", ascending=False)
            style.chart_card_open("Creators ที่ขายสินค้านี้", "เรียงตาม GMV")
            st.dataframe(ctable, hide_index=True, use_container_width=True,
                         column_config={
                             "GMV": st.column_config.NumberColumn(format="฿%.2f"),
                             "Commission": st.column_config.NumberColumn(format="฿%.2f"),
                         })
            style.chart_card_close()
