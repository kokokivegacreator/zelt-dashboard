import streamlit as st

from lib import db, style

st.set_page_config(
    page_title="Zelt Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

style.inject_css()
style.sidebar_brand()
style.hero()

client = db.get_client()

try:
    c_count = client.table("dim_creators").select("username", count="exact").limit(1).execute()
    p_count = client.table("dim_products").select("product_id", count="exact").limit(1).execute()
    log = client.table("upload_log").select("uploaded_at").order("uploaded_at", desc=True).limit(1).execute()
    last_upload = log.data[0]["uploaded_at"][:10] if log.data else "—"

    style.section_title("ภาพรวมระบบ")

    col1, col2, col3 = st.columns(3, gap="medium")
    col1.markdown(
        style.metric_card("Creators ในระบบ", f"{c_count.count or 0:,}", icon="👥", foot="affiliate creators"),
        unsafe_allow_html=True,
    )
    col2.markdown(
        style.metric_card("Products ในระบบ", f"{p_count.count or 0:,}", icon="📦", foot="SKU ทั้งหมด"),
        unsafe_allow_html=True,
    )
    col3.markdown(
        style.metric_card("อัพโหลดล่าสุด", last_upload, icon="⏱", foot="วันที่ sync ข้อมูล"),
        unsafe_allow_html=True,
    )
except Exception as e:
    st.error(f"เชื่อม Supabase ไม่ได้: {e}")

st.markdown("<br>", unsafe_allow_html=True)
style.section_title("หน้าใช้งาน")

pages = [
    ("📊", "Overview", "KPI + trend ภาพรวมการขาย"),
    ("🔁", "Month Comparison", "เทียบยอดระหว่างเดือน"),
    ("🎯", "Targets", "เป้าหมายเดือน/ไตรมาส + แคมเปญ"),
    ("👥", "Creators", "ลึกระดับ creator + drill-down"),
    ("📦", "Products", "16 SKU + creator-by-product"),
    ("🎬", "Videos", "ตาราง + sort GPM/CTR + TikTok link"),
    ("🔴", "Lives", "session list + time-of-day heatmap"),
    ("⬆️", "Upload", "อัพไฟล์ใหม่ (auto-detect)"),
]

cols = st.columns(2, gap="medium")
for i, (icon, name, desc) in enumerate(pages):
    cols[i % 2].markdown(
        style.metric_card(name, "", icon=icon, foot=desc),
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
    <div style="text-align:center; color:{style.BRAND['text_muted']}; font-size:0.78rem;
                margin-top:3rem; padding-top:1.2rem; border-top:1px solid rgba(74,107,58,0.10);">
        Zelt Sales Intelligence • Powered by TikTok Shop Affiliate Data
    </div>
    """,
    unsafe_allow_html=True,
)
