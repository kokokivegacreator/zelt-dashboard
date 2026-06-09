# Zelt Sales Dashboard

Dashboard ติดตามยอดขายแบรนด์ Zelt บน TikTok Shop Affiliate

## Stack
- Streamlit (frontend)
- Supabase Postgres (DB + storage)
- Plotly (charts)

## Local dev

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# แก้ค่า SUPABASE_URL / SUPABASE_KEY
streamlit run app/main.py
```

## Batch import M6 data

```bash
python scripts/import_m6.py
```

## Deploy

ใช้ Streamlit Community Cloud:
1. Push code ขึ้น GitHub
2. ไปที่ https://share.streamlit.io
3. Connect repo → ตั้ง path `app/main.py`
4. ใส่ secrets ใน Streamlit Cloud (`SUPABASE_URL`, `SUPABASE_KEY`)

## Pages
- Overview — KPI + trend
- Month Comparison — เทียบเดือน
- Targets — เป้าหมาย & แคมเปญ
- Creators / Products / Videos / Lives — drill-down
- Upload — อัพโหลดไฟล์ใหม่
