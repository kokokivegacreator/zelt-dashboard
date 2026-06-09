import pandas as pd
import plotly.express as px
import streamlit as st

from lib import db, format as F, charts

st.set_page_config(page_title="Creators — Zelt", page_icon="👤", layout="wide")
st.title("Creator Performance")


@st.cache_data(ttl=300)
def load_creator_daily():
    return pd.DataFrame(db.fetch_all("fact_creator_daily"))


@st.cache_data(ttl=300)
def load_dim_creators():
    return pd.DataFrame(db.fetch_all("dim_creators"))


@st.cache_data(ttl=300)
def load_product_creator():
    return pd.DataFrame(db.fetch_all("fact_product_creator_daily"))


@st.cache_data(ttl=300)
def load_dim_products():
    return pd.DataFrame(db.fetch_all("dim_products"))


cdf = load_creator_daily()
dim_c = load_dim_creators()

if cdf.empty:
    st.warning("ยังไม่มีข้อมูล creator")
    st.stop()

cdf["date"] = pd.to_datetime(cdf["date"]).dt.date
min_d, max_d = cdf["date"].min(), cdf["date"].max()

d_range = st.date_input("ช่วงวันที่", value=(min_d, max_d),
                        min_value=min_d, max_value=max_d, key="creator_date")
if isinstance(d_range, tuple) and len(d_range) == 2:
    d_from, d_to = d_range
else:
    d_from, d_to = min_d, max_d

period = cdf[(cdf["date"] >= d_from) & (cdf["date"] <= d_to)]

agg = period.groupby("creator_username").agg(
    GMV=("affiliate_gmv", "sum"),
    Orders=("affiliate_orders", "sum"),
    Items=("items_sold", "sum"),
    Live_GMV=("affiliate_live_gmv", "sum"),
    Video_GMV=("affiliate_video_gmv", "sum"),
    Card_GMV=("affiliate_product_card_gmv", "sum"),
    Commission=("est_commission", "sum"),
    Refund_GMV=("affiliate_refunded_gmv", "sum"),
    Followers=("affiliate_followers", "max"),
    Avg_CTR=("ctr", "mean"),
).reset_index().sort_values("GMV", ascending=False)
agg["AOV"] = (agg["GMV"] / agg["Orders"]).round(2).fillna(0)
agg["Refund_%"] = (agg["Refund_GMV"] / agg["GMV"] * 100).round(2).fillna(0)

c1, c2, c3 = st.columns(3)
c1.metric("Creators ทั้งหมด", F.fmt_int(len(agg)))
c2.metric("Active (GMV > 0)", F.fmt_int(int((agg["GMV"] > 0).sum())))
c3.metric("GMV รวม", F.fmt_compact(agg["GMV"].sum()))

st.markdown("---")

st.subheader("Creators List")
min_gmv = st.number_input("Filter: GMV ≥", min_value=0.0, value=0.0, step=100.0)
search = st.text_input("ค้นหาชื่อ creator")
view = agg[agg["GMV"] >= min_gmv].copy()
if search:
    view = view[view["creator_username"].str.contains(search, case=False, na=False)]

st.dataframe(view, hide_index=True, use_container_width=True,
             column_config={
                 "GMV": st.column_config.NumberColumn(format="฿%.2f"),
                 "Live_GMV": st.column_config.NumberColumn(format="฿%.2f"),
                 "Video_GMV": st.column_config.NumberColumn(format="฿%.2f"),
                 "Card_GMV": st.column_config.NumberColumn(format="฿%.2f"),
                 "Commission": st.column_config.NumberColumn(format="฿%.2f"),
                 "Refund_GMV": st.column_config.NumberColumn(format="฿%.2f"),
                 "Avg_CTR": st.column_config.NumberColumn(format="%.2f%%"),
                 "Refund_%": st.column_config.NumberColumn(format="%.2f%%"),
             })

st.markdown("---")
st.subheader("Drill-down")
options = view["creator_username"].head(50).tolist() or agg["creator_username"].head(50).tolist()
selected = st.selectbox("เลือก creator", options=options)

if selected:
    sub = period[period["creator_username"] == selected].sort_values("date")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("GMV รวม", F.fmt_compact(sub["affiliate_gmv"].sum()))
    c2.metric("Orders", F.fmt_int(int(sub["affiliate_orders"].sum())))
    c3.metric("Avg CTR", F.fmt_percent(sub["ctr"].mean()))
    c4.metric("Followers", F.fmt_int(int(sub["affiliate_followers"].max())))

    fig = px.line(sub, x="date", y="affiliate_gmv", markers=True,
                  title=f"GMV รายวัน — {selected}",
                  color_discrete_sequence=charts.PALETTE)
    st.plotly_chart(fig, use_container_width=True)

    # Channel mix
    mix = pd.DataFrame({
        "Channel": ["Live", "Video", "Card"],
        "GMV": [sub["affiliate_live_gmv"].sum(),
                sub["affiliate_video_gmv"].sum(),
                sub["affiliate_product_card_gmv"].sum()],
    })
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts.donut(mix["Channel"].tolist(), mix["GMV"].tolist(),
                                      title="Channel Mix"),
                        use_container_width=True)

    # Products sold by this creator
    pc = load_product_creator()
    dim_p = load_dim_products()
    if not pc.empty:
        pc["date"] = pd.to_datetime(pc["date"]).dt.date
        pc_sub = pc[(pc["creator_username"] == selected) &
                    (pc["date"] >= d_from) & (pc["date"] <= d_to)]
        if not pc_sub.empty:
            ptable = pc_sub.groupby("product_id").agg(
                GMV=("gmv", "sum"), Items=("items_sold", "sum"),
                Videos=("videos", "sum"), Lives=("live_streams", "sum"),
            ).reset_index().sort_values("GMV", ascending=False)
            if not dim_p.empty:
                ptable = ptable.merge(dim_p[["product_id", "name"]],
                                       on="product_id", how="left")
            with col2:
                st.markdown("**Products ที่ขาย**")
                st.dataframe(ptable, hide_index=True, use_container_width=True,
                             column_config={"GMV": st.column_config.NumberColumn(format="฿%.2f")})
