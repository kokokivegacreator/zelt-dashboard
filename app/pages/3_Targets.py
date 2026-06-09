from datetime import date, datetime

import pandas as pd
import streamlit as st

from lib import db, format as F, charts

st.set_page_config(page_title="Targets — Zelt", page_icon="🎯", layout="wide")
st.title("Targets & Campaigns")


@st.cache_data(ttl=60)
def load_targets_monthly():
    return pd.DataFrame(db.fetch_all("targets_monthly"))


@st.cache_data(ttl=60)
def load_targets_quarterly():
    return pd.DataFrame(db.fetch_all("targets_quarterly"))


@st.cache_data(ttl=60)
def load_campaigns():
    return pd.DataFrame(db.fetch_all("campaigns"))


@st.cache_data(ttl=120)
def load_creator_daily():
    return pd.DataFrame(db.fetch_all("fact_creator_daily"))


tab1, tab2, tab3 = st.tabs(["Monthly", "Quarterly", "Campaigns"])

# ---------- Monthly ----------
with tab1:
    cdf = load_creator_daily()
    tgt = load_targets_monthly()

    st.subheader("เพิ่ม/แก้ Monthly Target")
    with st.form("monthly_target"):
        c1, c2, c3, c4 = st.columns(4)
        month = c1.date_input("เดือน (เลือกวันที่ 1 ของเดือน)",
                              value=date.today().replace(day=1))
        target_gmv = c2.number_input("Target GMV (฿)", min_value=0.0, step=1000.0)
        target_orders = c3.number_input("Target Orders", min_value=0, step=10)
        target_creators = c4.number_input("Target Creators", min_value=0, step=1)
        notes = st.text_input("Notes")
        submit = st.form_submit_button("บันทึก")
        if submit:
            month_first = month.replace(day=1)
            db.upsert("targets_monthly", [{
                "month": month_first.isoformat(),
                "target_gmv": float(target_gmv),
                "target_orders": int(target_orders),
                "target_creators": int(target_creators),
                "notes": notes or None,
                "updated_at": datetime.utcnow().isoformat(),
            }], on_conflict="month")
            st.cache_data.clear()
            st.success(f"บันทึก target {month_first} แล้วค่ะ")
            st.rerun()

    st.markdown("### Progress รายเดือน")
    if tgt.empty:
        st.info("ยังไม่มี target — เพิ่มข้างบนได้เลย")
    else:
        tgt["month"] = pd.to_datetime(tgt["month"])
        if not cdf.empty:
            cdf["date"] = pd.to_datetime(cdf["date"])
            cdf["month"] = cdf["date"].dt.to_period("M").dt.to_timestamp()
            actuals = cdf.groupby("month").agg(
                actual_gmv=("affiliate_gmv", "sum"),
                actual_orders=("affiliate_orders", "sum"),
                actual_creators=("creator_username", "nunique"),
            ).reset_index()
            tgt = tgt.merge(actuals, on="month", how="left").fillna(0)
        for _, row in tgt.sort_values("month", ascending=False).iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['month'].strftime('%B %Y')}** — {row.get('notes') or ''}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    charts.progress_bar(row.get("actual_gmv", 0), row["target_gmv"], "GMV")
                with col2:
                    charts.progress_bar(row.get("actual_orders", 0), row["target_orders"], "Orders")
                with col3:
                    charts.progress_bar(row.get("actual_creators", 0), row["target_creators"], "Creators")

# ---------- Quarterly ----------
with tab2:
    qtgt = load_targets_quarterly()
    cdf = load_creator_daily()
    st.subheader("เพิ่ม/แก้ Quarterly Target")
    with st.form("q_target"):
        c1, c2 = st.columns(2)
        quarter = c1.text_input("Quarter (เช่น 2026-Q2)", value=f"{date.today().year}-Q{(date.today().month-1)//3+1}")
        target_gmv = c2.number_input("Target GMV (฿)", min_value=0.0, step=10000.0)
        c3, c4 = st.columns(2)
        s = c3.date_input("Start", value=date.today().replace(day=1))
        e = c4.date_input("End", value=date.today())
        target_orders = st.number_input("Target Orders", min_value=0, step=100)
        notes = st.text_input("Notes", key="q_notes")
        if st.form_submit_button("บันทึก"):
            db.upsert("targets_quarterly", [{
                "quarter": quarter,
                "start_date": s.isoformat(),
                "end_date": e.isoformat(),
                "target_gmv": float(target_gmv),
                "target_orders": int(target_orders),
                "notes": notes or None,
                "updated_at": datetime.utcnow().isoformat(),
            }], on_conflict="quarter")
            st.cache_data.clear()
            st.success(f"บันทึก {quarter}")
            st.rerun()

    st.markdown("### Progress รายไตรมาส")
    if qtgt.empty:
        st.info("ยังไม่มี quarterly target")
    elif not cdf.empty:
        cdf["date"] = pd.to_datetime(cdf["date"]).dt.date
        for _, row in qtgt.sort_values("quarter", ascending=False).iterrows():
            s, e = pd.to_datetime(row["start_date"]).date(), pd.to_datetime(row["end_date"]).date()
            sub = cdf[(cdf["date"] >= s) & (cdf["date"] <= e)]
            actual_gmv = sub["affiliate_gmv"].sum()
            actual_orders = sub["affiliate_orders"].sum()
            with st.container(border=True):
                st.markdown(f"**{row['quarter']}** ({s} → {e}) — {row.get('notes') or ''}")
                col1, col2 = st.columns(2)
                with col1:
                    charts.progress_bar(actual_gmv, row["target_gmv"], "GMV")
                with col2:
                    charts.progress_bar(actual_orders, row["target_orders"], "Orders")

# ---------- Campaigns ----------
with tab3:
    camps = load_campaigns()
    cdf = load_creator_daily()
    st.subheader("สร้าง Campaign")
    with st.form("campaign"):
        name = st.text_input("ชื่อแคมเปญ")
        c1, c2 = st.columns(2)
        s = c1.date_input("Start", value=date.today())
        e = c2.date_input("End", value=date.today())
        c3, c4 = st.columns(2)
        target_gmv = c3.number_input("Target GMV", min_value=0.0, step=1000.0)
        target_orders = c4.number_input("Target Orders", min_value=0, step=10)
        product_ids = st.text_input("Product IDs (comma separated)", help="เว้นว่าง = ทุก product")
        creators = st.text_input("Creator usernames (comma separated)", help="เว้นว่าง = ทุก creator")
        notes = st.text_area("Notes")
        if st.form_submit_button("สร้าง Campaign"):
            if not name:
                st.error("ใส่ชื่อแคมเปญด้วยค่ะ")
            else:
                pids = [p.strip() for p in product_ids.split(",") if p.strip()]
                cnames = [c.strip() for c in creators.split(",") if c.strip()]
                db.upsert("campaigns", [{
                    "name": name,
                    "start_date": s.isoformat(),
                    "end_date": e.isoformat(),
                    "target_gmv": float(target_gmv),
                    "target_orders": int(target_orders),
                    "product_ids": pids,
                    "creator_usernames": cnames,
                    "notes": notes or None,
                }])
                st.cache_data.clear()
                st.success(f"สร้าง campaign '{name}'")
                st.rerun()

    st.markdown("### Active & Past Campaigns")
    if camps.empty:
        st.info("ยังไม่มี campaign")
    elif not cdf.empty:
        cdf["date"] = pd.to_datetime(cdf["date"]).dt.date
        for _, row in camps.sort_values("start_date", ascending=False).iterrows():
            s, e = pd.to_datetime(row["start_date"]).date(), pd.to_datetime(row["end_date"]).date()
            today = date.today()
            status = "🟢 Active" if s <= today <= e else ("✅ Done" if today > e else "⏳ Upcoming")
            sub = cdf[(cdf["date"] >= s) & (cdf["date"] <= e)]
            if row.get("creator_usernames"):
                sub = sub[sub["creator_username"].isin(row["creator_usernames"])]
            actual_gmv = sub["affiliate_gmv"].sum()
            actual_orders = sub["affiliate_orders"].sum()
            with st.container(border=True):
                st.markdown(f"**{row['name']}** — {status} ({s} → {e})")
                if row.get("notes"):
                    st.caption(row["notes"])
                col1, col2 = st.columns(2)
                with col1:
                    charts.progress_bar(actual_gmv, row["target_gmv"], "GMV")
                with col2:
                    charts.progress_bar(actual_orders, row["target_orders"], "Orders")
