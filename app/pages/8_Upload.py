import io

import pandas as pd
import streamlit as st

from lib import db, etl, parsers, style

st.set_page_config(page_title="Upload — Zelt", page_icon="📤", layout="wide")
style.inject_css()
style.sidebar_brand()

style.subpage_hero(
    eyebrow="UPLOAD",
    title="นำเข้าข้อมูลใหม่",
    subtitle="ลากไฟล์ xlsx มาวาง — ระบบจะ detect ชนิดอัตโนมัติแล้วเอาเข้า DB",
)

with st.expander("รูปแบบไฟล์ที่รองรับ"):
    st.markdown("""
| Pattern | Type | Table |
|---|---|---|
| `Creator_List_*` | Creator daily | `fact_creator_daily` |
| `Video_List_*` | Videos | `fact_video` |
| `Transaction_Analysis_Live_List_*` | Lives | `fact_live` |
| `ListProducts_*` | Product daily | `fact_product_daily` |
| `ListCreators_*` | Creators per product | `fact_product_creator_daily` |

**หมายเหตุ:** `ListCreators_*` ต้องระบุ Product ID (จากชื่อโฟลเดอร์เดิม) — ถ้า upload ผ่านเว็บ ใส่ Product ID เพิ่มในช่องล่าง
""")

style.section_title("Upload ไฟล์")

product_hint = st.text_input("Product ID (เฉพาะกรณีอัพ ListCreators_*)",
                              help="ใส่ Product ID ที่ ListCreators นั้นๆ ขึ้นกับ")

files = st.file_uploader("เลือกไฟล์ (หลายไฟล์ได้)",
                          type=["xlsx"], accept_multiple_files=True)

if files and st.button("Import ทั้งหมด", type="primary"):
    results = []
    progress = st.progress(0)
    for i, f in enumerate(files):
        try:
            b = io.BytesIO(f.getvalue())
            r = etl.process_file(f.name, file_bytes=b,
                                  product_id_hint=product_hint or None)
            etl.log_upload(f.name, r)
            results.append({"file": f.name, **r})
        except Exception as e:
            results.append({"file": f.name, "status": "error", "notes": str(e)})
        progress.progress((i + 1) / len(files))
    st.success(f"นำเข้าเสร็จ {len(results)} ไฟล์")
    style.chart_card_open("ผลการนำเข้า", "")
    st.dataframe(pd.DataFrame(results), hide_index=True, use_container_width=True)
    style.chart_card_close()
    st.cache_data.clear()

st.markdown("<br>", unsafe_allow_html=True)
style.section_title("Upload Log")

log = db.fetch_all("upload_log", order="-uploaded_at", limit=50)
if log:
    df = pd.DataFrame(log)
    style.chart_card_open(f"{len(log)} รายการล่าสุด", "")
    st.dataframe(df[["uploaded_at", "filename", "file_type", "date_range",
                     "rows_imported", "status", "notes"]],
                  hide_index=True, use_container_width=True)
    style.chart_card_close()
else:
    st.info("ยังไม่มี upload log")
