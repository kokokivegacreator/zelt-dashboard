from datetime import date, datetime

import pandas as pd
import streamlit as st

from lib import db, format as F, charts, style, hashtags as ht

st.set_page_config(page_title="Targets — Zelt", page_icon="🎯", layout="wide")
style.inject_css()
style.sidebar_brand()


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


@st.cache_data(ttl=120)
def load_videos():
    return pd.DataFrame(db.fetch_all("fact_video"))


def _clear_and_rerun(msg: str):
    st.cache_data.clear()
    st.toast(msg, icon="✅")
    st.rerun()


style.subpage_hero(
    eyebrow="TARGETS",
    title="Targets & Campaigns",
    subtitle="ตั้งเป้าหมาย แก้ไข ลบ และติดตามแคมเปญผ่าน hashtag",
)

tab1, tab2, tab3 = st.tabs(["Monthly", "Quarterly", "Campaigns"])


# ============ MONTHLY ============
with tab1:
    cdf = load_creator_daily()
    tgt = load_targets_monthly()

    edit_key = "edit_monthly"
    editing = st.session_state.get(edit_key)

    style.section_title("เพิ่ม / แก้ Monthly Target")

    default_month = date.today().replace(day=1)
    default_gmv = 0.0
    default_orders = 0
    default_creators = 0
    default_notes = ""
    if editing is not None and not tgt.empty:
        row = tgt[tgt["month"] == editing]
        if not row.empty:
            r = row.iloc[0]
            default_month = pd.to_datetime(r["month"]).date()
            default_gmv = float(r["target_gmv"] or 0)
            default_orders = int(r["target_orders"] or 0)
            default_creators = int(r["target_creators"] or 0)
            default_notes = r.get("notes") or ""
            st.info(f"กำลังแก้ไข: {default_month:%B %Y}")

    with st.form("monthly_target", clear_on_submit=False):
        c1, c2, c3, c4 = st.columns(4)
        month = c1.date_input("เดือน", value=default_month,
                              disabled=editing is not None,
                              help="เลือกวันที่ 1 ของเดือน")
        target_gmv = c2.number_input("Target GMV (฿)", min_value=0.0,
                                      step=1000.0, value=default_gmv)
        target_orders = c3.number_input("Target Orders", min_value=0,
                                         step=10, value=default_orders)
        target_creators = c4.number_input("Target Creators", min_value=0,
                                            step=1, value=default_creators)
        notes = st.text_input("Notes", value=default_notes)

        cs1, cs2 = st.columns([1, 5])
        save = cs1.form_submit_button("บันทึก", use_container_width=True)
        cancel = cs2.form_submit_button("ยกเลิก", use_container_width=False) if editing else False

        if save:
            month_first = month.replace(day=1)
            db.upsert("targets_monthly", [{
                "month": month_first.isoformat(),
                "target_gmv": float(target_gmv),
                "target_orders": int(target_orders),
                "target_creators": int(target_creators),
                "notes": notes or None,
                "updated_at": datetime.utcnow().isoformat(),
            }], on_conflict="month")
            st.session_state.pop(edit_key, None)
            _clear_and_rerun(f"บันทึก {month_first:%B %Y} แล้ว")
        if cancel:
            st.session_state.pop(edit_key, None)
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    style.section_title("Progress รายเดือน")

    if tgt.empty:
        st.info("ยังไม่มี target — เพิ่มข้างบนได้เลย")
    else:
        tgt["month"] = pd.to_datetime(tgt["month"]).dt.date
        if not cdf.empty:
            cdf["date"] = pd.to_datetime(cdf["date"]).dt.date
            cdf["_m"] = pd.to_datetime(cdf["date"]).dt.to_period("M").dt.to_timestamp().dt.date
            actuals = cdf.groupby("_m").agg(
                actual_gmv=("affiliate_gmv", "sum"),
                actual_orders=("affiliate_orders", "sum"),
                actual_creators=("creator_username", "nunique"),
            ).reset_index().rename(columns={"_m": "month"})
            tgt = tgt.merge(actuals, on="month", how="left").fillna(0)

        for _, row in tgt.sort_values("month", ascending=False).iterrows():
            month_iso = row["month"].isoformat()
            st.markdown(
                f"""
                <div class="zelt-item-card">
                    <div class="zelt-item-head">
                        <div class="zelt-item-title">{row['month'].strftime('%B %Y')}</div>
                        <div class="zelt-item-meta">{row.get('notes') or ''}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col1, col2, col3 = st.columns(3)
            with col1:
                charts.progress_bar(row.get("actual_gmv", 0), row["target_gmv"], "GMV")
            with col2:
                charts.progress_bar(row.get("actual_orders", 0), row["target_orders"], "Orders")
            with col3:
                charts.progress_bar(row.get("actual_creators", 0), row["target_creators"], "Creators")

            ac1, ac2, _ = st.columns([1, 1, 6])
            if ac1.button("✎ แก้ไข", key=f"em_{month_iso}", use_container_width=True):
                st.session_state[edit_key] = month_iso
                st.rerun()
            if ac2.button("🗑 ลบ", key=f"dm_{month_iso}", use_container_width=True):
                db.delete("targets_monthly", {"month": month_iso})
                _clear_and_rerun(f"ลบ {row['month']:%B %Y} แล้ว")


# ============ QUARTERLY ============
with tab2:
    qtgt = load_targets_quarterly()
    cdf = load_creator_daily()

    edit_key = "edit_quarterly"
    editing = st.session_state.get(edit_key)

    style.section_title("เพิ่ม / แก้ Quarterly Target")

    default_q = f"{date.today().year}-Q{(date.today().month-1)//3+1}"
    default_start = date.today().replace(day=1)
    default_end = date.today()
    default_gmv = 0.0
    default_orders = 0
    default_notes = ""
    if editing is not None and not qtgt.empty:
        row = qtgt[qtgt["quarter"] == editing]
        if not row.empty:
            r = row.iloc[0]
            default_q = r["quarter"]
            default_start = pd.to_datetime(r["start_date"]).date()
            default_end = pd.to_datetime(r["end_date"]).date()
            default_gmv = float(r["target_gmv"] or 0)
            default_orders = int(r["target_orders"] or 0)
            default_notes = r.get("notes") or ""
            st.info(f"กำลังแก้ไข: {default_q}")

    with st.form("q_target"):
        c1, c2 = st.columns(2)
        quarter = c1.text_input("Quarter (เช่น 2026-Q2)", value=default_q,
                                  disabled=editing is not None)
        target_gmv = c2.number_input("Target GMV (฿)", min_value=0.0,
                                      step=10000.0, value=default_gmv)
        c3, c4 = st.columns(2)
        s = c3.date_input("Start", value=default_start, key="q_start")
        e = c4.date_input("End", value=default_end, key="q_end")
        target_orders = st.number_input("Target Orders", min_value=0,
                                          step=100, value=default_orders)
        notes = st.text_input("Notes", value=default_notes, key="q_notes")

        cs1, cs2 = st.columns([1, 5])
        save = cs1.form_submit_button("บันทึก", use_container_width=True)
        cancel = cs2.form_submit_button("ยกเลิก") if editing else False

        if save:
            db.upsert("targets_quarterly", [{
                "quarter": quarter,
                "start_date": s.isoformat(),
                "end_date": e.isoformat(),
                "target_gmv": float(target_gmv),
                "target_orders": int(target_orders),
                "notes": notes or None,
                "updated_at": datetime.utcnow().isoformat(),
            }], on_conflict="quarter")
            st.session_state.pop(edit_key, None)
            _clear_and_rerun(f"บันทึก {quarter}")
        if cancel:
            st.session_state.pop(edit_key, None)
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    style.section_title("Progress รายไตรมาส")

    if qtgt.empty:
        st.info("ยังไม่มี quarterly target")
    else:
        if not cdf.empty:
            cdf["date"] = pd.to_datetime(cdf["date"]).dt.date
        for _, row in qtgt.sort_values("quarter", ascending=False).iterrows():
            s_d = pd.to_datetime(row["start_date"]).date()
            e_d = pd.to_datetime(row["end_date"]).date()
            if not cdf.empty:
                sub = cdf[(cdf["date"] >= s_d) & (cdf["date"] <= e_d)]
                actual_gmv = sub["affiliate_gmv"].sum()
                actual_orders = sub["affiliate_orders"].sum()
            else:
                actual_gmv = actual_orders = 0

            st.markdown(
                f"""
                <div class="zelt-item-card">
                    <div class="zelt-item-head">
                        <div class="zelt-item-title">{row['quarter']}</div>
                        <div class="zelt-item-meta">{s_d} → {e_d} • {row.get('notes') or ''}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col1, col2 = st.columns(2)
            with col1:
                charts.progress_bar(actual_gmv, row["target_gmv"], "GMV")
            with col2:
                charts.progress_bar(actual_orders, row["target_orders"], "Orders")

            ac1, ac2, _ = st.columns([1, 1, 6])
            if ac1.button("✎ แก้ไข", key=f"eq_{row['quarter']}", use_container_width=True):
                st.session_state[edit_key] = row["quarter"]
                st.rerun()
            if ac2.button("🗑 ลบ", key=f"dq_{row['quarter']}", use_container_width=True):
                db.delete("targets_quarterly", {"quarter": row["quarter"]})
                _clear_and_rerun(f"ลบ {row['quarter']}")


# ============ CAMPAIGNS ============
with tab3:
    camps = load_campaigns()
    cdf = load_creator_daily()
    vdf = load_videos()

    edit_key = "edit_campaign"
    editing = st.session_state.get(edit_key)

    style.section_title("สร้าง / แก้ Campaign")

    default_name = ""
    default_start = date.today()
    default_end = date.today()
    default_gmv = 0.0
    default_orders = 0
    default_pids = ""
    default_creators_str = ""
    default_hashtags_str = ""
    default_notes = ""

    if editing is not None and not camps.empty:
        row = camps[camps["id"] == editing]
        if not row.empty:
            r = row.iloc[0]
            default_name = r["name"]
            default_start = pd.to_datetime(r["start_date"]).date()
            default_end = pd.to_datetime(r["end_date"]).date()
            default_gmv = float(r["target_gmv"] or 0)
            default_orders = int(r["target_orders"] or 0)
            default_pids = ", ".join(r.get("product_ids") or [])
            default_creators_str = ", ".join(r.get("creator_usernames") or [])
            default_hashtags_str = ", ".join(r.get("hashtags") or [])
            default_notes = r.get("notes") or ""
            st.info(f"กำลังแก้ไข: {default_name}")

    with st.form("campaign"):
        name = st.text_input("ชื่อแคมเปญ", value=default_name)
        c1, c2 = st.columns(2)
        s = c1.date_input("Start", value=default_start, key="c_start")
        e = c2.date_input("End", value=default_end, key="c_end")
        c3, c4 = st.columns(2)
        target_gmv = c3.number_input("Target GMV", min_value=0.0,
                                      step=1000.0, value=default_gmv)
        target_orders = c4.number_input("Target Orders", min_value=0,
                                         step=10, value=default_orders)
        hashtags_str = st.text_input(
            "Hashtags (คั่นด้วย comma หรือ space)",
            value=default_hashtags_str,
            placeholder="เช่น zelt, คีโต, หล่อฮังก๊วย",
            help="ระบบจะหา video ที่ title ติด hashtag เหล่านี้ใน DB อัตโนมัติ",
        )
        product_ids = st.text_input("Product IDs (comma separated, เว้นว่าง = ทุก product)",
                                      value=default_pids)
        creators_str = st.text_input("Creator usernames (comma separated, เว้นว่าง = ทุกคน)",
                                       value=default_creators_str)
        notes = st.text_area("Notes", value=default_notes)

        cs1, cs2 = st.columns([1, 5])
        save = cs1.form_submit_button("บันทึก", use_container_width=True)
        cancel = cs2.form_submit_button("ยกเลิก") if editing else False

        if save:
            if not name:
                st.error("ใส่ชื่อแคมเปญด้วยค่ะ")
            else:
                pids = [p.strip() for p in product_ids.split(",") if p.strip()]
                cnames = [c.strip() for c in creators_str.split(",") if c.strip()]
                tag_list = ht.parse_tag_input(hashtags_str)
                payload = {
                    "name": name,
                    "start_date": s.isoformat(),
                    "end_date": e.isoformat(),
                    "target_gmv": float(target_gmv),
                    "target_orders": int(target_orders),
                    "product_ids": pids,
                    "creator_usernames": cnames,
                    "hashtags": tag_list,
                    "notes": notes or None,
                }
                if editing is not None:
                    db.update("campaigns", payload, {"id": editing})
                    st.session_state.pop(edit_key, None)
                    _clear_and_rerun(f"แก้ไข '{name}'")
                else:
                    db.upsert("campaigns", [payload])
                    _clear_and_rerun(f"สร้าง '{name}'")
        if cancel:
            st.session_state.pop(edit_key, None)
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    style.section_title("Active & Past Campaigns")

    if camps.empty:
        st.info("ยังไม่มี campaign")
    else:
        if not cdf.empty:
            cdf["date"] = pd.to_datetime(cdf["date"]).dt.date
        if not vdf.empty:
            vdf["post_date"] = pd.to_datetime(vdf["post_date"]).dt.date

        today = date.today()
        for _, row in camps.sort_values("start_date", ascending=False).iterrows():
            s_d = pd.to_datetime(row["start_date"]).date()
            e_d = pd.to_datetime(row["end_date"]).date()
            tag_list = list(row.get("hashtags") or [])
            cname_list = list(row.get("creator_usernames") or [])

            if s_d <= today <= e_d:
                status_html = style.badge("Active", "active")
            elif today > e_d:
                status_html = style.badge("Done", "done")
            else:
                status_html = style.badge("Upcoming", "upcoming")

            chip_html = style.chips(tag_list, style="gold") if tag_list else ""

            # Header card
            st.markdown(
                f"""
                <div class="zelt-item-card">
                    <div class="zelt-item-head">
                        <div>
                            <div class="zelt-item-title">{row['name']}</div>
                            <div class="zelt-item-meta">{s_d} → {e_d} {status_html}</div>
                        </div>
                    </div>
                    <div style="margin-top:0.4rem;">{chip_html}</div>
                    {f'<div class="zelt-item-meta" style="margin-top:0.5rem;">{row["notes"]}</div>' if row.get("notes") else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Hashtag-matched videos in range
            matched_videos = pd.DataFrame()
            if tag_list and not vdf.empty:
                in_range = vdf[(vdf["post_date"] >= s_d) & (vdf["post_date"] <= e_d)]
                if cname_list:
                    in_range = in_range[in_range["creator_username"].isin(cname_list)]
                matched_videos = ht.videos_matching(in_range, tag_list, "video_name")

            # Actuals — prefer hashtag-matched videos if hashtags set, else creator_daily fallback
            if tag_list and not matched_videos.empty:
                actual_gmv = matched_videos["gmv"].sum()
                actual_orders = int(matched_videos["affiliate_orders"].sum())
                actual_source = f"จาก {len(matched_videos)} video ที่ติด hashtag"
            elif not cdf.empty:
                sub = cdf[(cdf["date"] >= s_d) & (cdf["date"] <= e_d)]
                if cname_list:
                    sub = sub[sub["creator_username"].isin(cname_list)]
                actual_gmv = sub["affiliate_gmv"].sum()
                actual_orders = int(sub["affiliate_orders"].sum())
                actual_source = "จาก creator daily (ทั้งหมดในช่วง)"
            else:
                actual_gmv = actual_orders = 0
                actual_source = "ไม่มีข้อมูล"

            st.caption(actual_source)
            col1, col2 = st.columns(2)
            with col1:
                charts.progress_bar(actual_gmv, row["target_gmv"], "GMV")
            with col2:
                charts.progress_bar(actual_orders, row["target_orders"], "Orders")

            # Matched videos table
            if tag_list:
                with st.expander(f"📹 Videos ที่ติด hashtag ({len(matched_videos)} clip)"):
                    if matched_videos.empty:
                        st.info("ยังไม่มี video ที่ติด hashtag ในช่วงเวลานี้")
                    else:
                        view = matched_videos.copy()
                        view["matched_tags"] = view["video_name"].apply(
                            lambda t: ", ".join("#" + x for x in ht.matched_tags(t, tag_list))
                        )
                        display = view[[
                            "video_name", "creator_username", "post_date",
                            "matched_tags", "gmv", "affiliate_orders",
                            "affiliate_ctr", "shoppable_video_gpm", "video_link"
                        ]].rename(columns={
                            "video_name": "Title",
                            "creator_username": "Creator",
                            "post_date": "Posted",
                            "matched_tags": "Tags",
                            "gmv": "GMV",
                            "affiliate_orders": "Orders",
                            "affiliate_ctr": "CTR",
                            "shoppable_video_gpm": "GPM",
                            "video_link": "Link",
                        }).sort_values("GMV", ascending=False)
                        st.dataframe(
                            display, hide_index=True, use_container_width=True,
                            column_config={
                                "Title": st.column_config.TextColumn(width="medium"),
                                "GMV": st.column_config.NumberColumn(format="฿%.2f"),
                                "GPM": st.column_config.NumberColumn(format="฿%.2f"),
                                "CTR": st.column_config.NumberColumn(format="%.2f%%"),
                                "Link": st.column_config.LinkColumn("TikTok", display_text="เปิด"),
                            },
                        )

            # Edit / Delete
            ac1, ac2, _ = st.columns([1, 1, 6])
            if ac1.button("✎ แก้ไข", key=f"ec_{row['id']}", use_container_width=True):
                st.session_state[edit_key] = int(row["id"])
                st.rerun()
            if ac2.button("🗑 ลบ", key=f"dc_{row['id']}", use_container_width=True):
                db.delete("campaigns", {"id": int(row["id"])})
                _clear_and_rerun(f"ลบ '{row['name']}'")

            st.markdown("<br>", unsafe_allow_html=True)
