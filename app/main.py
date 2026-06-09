import streamlit as st

from lib import db

st.set_page_config(page_title="Zelt Dashboard", page_icon="📊", layout="wide")

st.title("Zelt Sales Dashboard")
st.caption("ติดตามยอดขาย Zelt บน TikTok Shop Affiliate")

col1, col2, col3 = st.columns(3)
client = db.get_client()

try:
    c_count = client.table("dim_creators").select("username", count="exact").limit(1).execute()
    p_count = client.table("dim_products").select("product_id", count="exact").limit(1).execute()
    log = client.table("upload_log").select("uploaded_at").order("uploaded_at", desc=True).limit(1).execute()

    col1.metric("Creators ในระบบ", f"{c_count.count or 0:,}")
    col2.metric("Products ในระบบ", f"{p_count.count or 0:,}")
    col3.metric("อัพโหลดล่าสุด", log.data[0]["uploaded_at"][:10] if log.data else "—")
except Exception as e:
    st.error(f"เชื่อม Supabase ไม่ได้: {e}")

st.markdown("---")
st.markdown("""
### หน้าใช้งาน
- **Overview** — KPI + trend ภาพรวม
- **Month Comparison** — เทียบเดือน
- **Targets** — เป้าหมาย & แคมเปญ
- **Creators / Products / Videos / Lives** — ลึกราย entity
- **Upload** — อัพโหลดไฟล์ใหม่ (auto-detect)
""")
