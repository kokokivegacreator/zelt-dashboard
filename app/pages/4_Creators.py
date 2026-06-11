import pandas as pd
import plotly.express as px
import streamlit as st

from lib import db, format as F, charts, style

st.set_page_config(page_title="Creators — Zelt", page_icon="👥", layout="wide")
style.inject_css()
style.sidebar_brand()


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
    style.subpage_hero("CREATORS", "Creator Performance", "ยังไม่มีข้อมูล")
    st.warning("ยังไม่มีข้อมูล creator")
    st.stop()

cdf["date"] = pd.to_datetime(cdf["date"]).dt.date
min_d, max_d = cdf["date"].min(), cdf["date"].max()

style.subpage_hero(
    eyebrow="CREATORS",
    title="Creator Performance",
    subtitle=f"ข้อมูลตั้งแต่ {min_d:%d %b %Y} ถึง {max_d:%d %b %Y}",
)

c1, _ = st.columns([2, 3])
with c1:
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

style.section_title("ภาพรวม")
k1, k2, k3 = st.columns(3, gap="small")
k1.markdown(style.kpi_card("Creators ทั้งหมด", F.fmt_int(len(agg))), unsafe_allow_html=True)
k2.markdown(style.kpi_card("Active (GMV > 0)", F.fmt_int(int((agg["GMV"] > 0).sum()))), unsafe_allow_html=True)
k3.markdown(style.kpi_card("GMV รวม", F.fmt_compact(agg["GMV"].sum())), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
style.section_title("Creators List")

f1, f2 = st.columns(2)
with f1:
    min_gmv = st.number_input("Filter: GMV ≥", min_value=0.0, value=0.0, step=100.0)
with f2:
    search = st.text_input("ค้นหาชื่อ creator")

view = agg[agg["GMV"] >= min_gmv].copy()
if search:
    view = view[view["creator_username"].str.contains(search, case=False, na=False)]

style.chart_card_open(f"พบ {len(view):,} creator", "เรียงตาม GMV จากมากไปน้อย")
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
style.chart_card_close()

st.markdown("<br>", unsafe_allow_html=True)
style.section_title("Drill-down")

options = view["creator_username"].head(50).tolist() or agg["creator_username"].head(50).tolist()
selected = st.selectbox("เลือก creator", options=options)

if selected:
    sub = period[period["creator_username"] == selected].sort_values("date")

    k1, k2, k3, k4 = st.columns(4, gap="small")
    k1.markdown(style.kpi_card("GMV รวม", F.fmt_compact(sub["affiliate_gmv"].sum())), unsafe_allow_html=True)
    k2.markdown(style.kpi_card("Orders", F.fmt_int(int(sub["affiliate_orders"].sum()))), unsafe_allow_html=True)
    k3.markdown(style.kpi_card("Avg CTR", F.fmt_percent(sub["ctr"].mean())), unsafe_allow_html=True)
    k4.markdown(style.kpi_card("Followers", F.fmt_int(int(sub["affiliate_followers"].max()))), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    style.chart_card_open(f"GMV รายวัน — {selected}", "")
    fig = px.line(sub, x="date", y="affiliate_gmv", markers=True,
                  color_discrete_sequence=charts.PALETTE)
    fig.update_traces(line=dict(width=3), marker=dict(size=7, line=dict(width=2, color="white")))
    charts._apply_theme(fig, height=350)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    style.chart_card_close()

    mix = pd.DataFrame({
        "Channel": ["Live", "Video", "Card"],
        "GMV": [sub["affiliate_live_gmv"].sum(),
                sub["affiliate_video_gmv"].sum(),
                sub["affiliate_product_card_gmv"].sum()],
    })
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        style.chart_card_open("Channel Mix", "สัดส่วน GMV ของ creator นี้")
        st.plotly_chart(charts.donut(mix["Channel"].tolist(), mix["GMV"].tolist()),
                        use_container_width=True, config={"displayModeBar": False})
        style.chart_card_close()

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
                style.chart_card_open("Products ที่ขาย", "เรียงตาม GMV")
                st.dataframe(ptable, hide_index=True, use_container_width=True,
                             column_config={"GMV": st.column_config.NumberColumn(format="฿%.2f")})
                style.chart_card_close()
