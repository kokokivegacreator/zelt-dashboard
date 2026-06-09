import pandas as pd
import plotly.express as px
import streamlit as st

from lib import db, format as F, charts

st.set_page_config(page_title="Products — Zelt", page_icon="📦", layout="wide")
st.title("Product Performance")


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
    st.warning("ยังไม่มีข้อมูล product")
    st.stop()

pdf["date"] = pd.to_datetime(pdf["date"]).dt.date
min_d, max_d = pdf["date"].min(), pdf["date"].max()

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

st.subheader("Products Summary")
st.dataframe(agg, hide_index=True, use_container_width=True,
             column_config={
                 "GMV": st.column_config.NumberColumn(format="฿%.2f"),
                 "Commission": st.column_config.NumberColumn(format="฿%.2f"),
                 "Refund_GMV": st.column_config.NumberColumn(format="฿%.2f"),
             })

st.markdown("---")
st.subheader("Drill-down")
options = agg["product_id"].tolist()
display_map = dict(zip(agg["product_id"], agg.get("name", agg["product_id"])))
selected = st.selectbox("เลือก product", options=options,
                        format_func=lambda x: f"{display_map.get(x, x)[:80]}")

if selected:
    sub = period[period["product_id"] == selected].sort_values("date")
    c1, c2, c3 = st.columns(3)
    c1.metric("GMV", F.fmt_compact(sub["gmv"].sum()))
    c2.metric("Items", F.fmt_int(int(sub["items_sold"].sum())))
    c3.metric("Commission", F.fmt_currency(sub["est_commission"].sum()))

    fig = px.line(sub, x="date", y="gmv", markers=True,
                  title="GMV รายวัน", color_discrete_sequence=charts.PALETTE)
    st.plotly_chart(fig, use_container_width=True)

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
            st.markdown("**Creators ที่ขายสินค้านี้**")
            st.dataframe(ctable, hide_index=True, use_container_width=True,
                         column_config={
                             "GMV": st.column_config.NumberColumn(format="฿%.2f"),
                             "Commission": st.column_config.NumberColumn(format="฿%.2f"),
                         })
