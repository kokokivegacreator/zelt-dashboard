from __future__ import annotations

import streamlit as st


BRAND = {
    "name": "Zelt",
    "tagline": "Sales Intelligence — TikTok Shop Affiliate",
    "primary": "#4A6B3A",
    "primary_dark": "#324A28",
    "accent": "#C9A961",
    "accent_dark": "#A8884A",
    "cream": "#FAF7F2",
    "cream_dark": "#F0EBE0",
    "text": "#2D3A2A",
    "text_muted": "#6B7568",
    "danger": "#B8504B",
    "success": "#5C8A4F",
}

PLOTLY_COLORWAY = [
    "#4A6B3A", "#C9A961", "#7A9B6E", "#A8884A",
    "#324A28", "#D4B981", "#5C8A4F", "#8C6F3A",
]


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, sans-serif;
        }}

        h1, h2, h3 {{
            font-family: 'Playfair Display', serif;
            color: {BRAND['text']};
            letter-spacing: -0.5px;
        }}

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1280px;
        }}

        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {BRAND['cream_dark']} 0%, {BRAND['cream']} 100%);
            border-right: 1px solid rgba(74, 107, 58, 0.08);
        }}
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {{
            color: {BRAND['primary_dark']};
        }}

        .zelt-hero {{
            background: linear-gradient(135deg, {BRAND['primary']} 0%, {BRAND['primary_dark']} 100%);
            color: {BRAND['cream']};
            padding: 2.5rem 2.5rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 12px 32px rgba(74, 107, 58, 0.18);
            position: relative;
            overflow: hidden;
        }}
        .zelt-hero::after {{
            content: '';
            position: absolute;
            top: -40%; right: -10%;
            width: 360px; height: 360px;
            background: radial-gradient(circle, {BRAND['accent']}33 0%, transparent 70%);
            border-radius: 50%;
        }}
        .zelt-hero-logo {{
            display: inline-flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 1rem;
        }}
        .zelt-hero-mark {{
            width: 56px; height: 56px;
            background: {BRAND['accent']};
            color: {BRAND['primary_dark']};
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Playfair Display', serif;
            font-size: 30px;
            font-weight: 700;
            box-shadow: 0 6px 18px rgba(201, 169, 97, 0.35);
        }}
        .zelt-hero-name {{
            font-family: 'Playfair Display', serif;
            font-size: 2.4rem;
            font-weight: 700;
            line-height: 1;
            color: {BRAND['cream']};
        }}
        .zelt-hero-tag {{
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            letter-spacing: 4px;
            text-transform: uppercase;
            color: {BRAND['accent']};
            opacity: 0.9;
        }}
        .zelt-hero-sub {{
            font-size: 1.05rem;
            opacity: 0.88;
            margin-top: 0.6rem;
            position: relative;
            z-index: 1;
        }}

        .zelt-card {{
            background: white;
            border: 1px solid rgba(74, 107, 58, 0.10);
            border-radius: 16px;
            padding: 1.4rem 1.5rem;
            box-shadow: 0 2px 12px rgba(45, 58, 42, 0.04);
            transition: all 0.25s ease;
            height: 100%;
        }}
        .zelt-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(45, 58, 42, 0.10);
            border-color: {BRAND['primary']}33;
        }}
        .zelt-card-label {{
            font-size: 0.78rem;
            font-weight: 600;
            color: {BRAND['text_muted']};
            text-transform: uppercase;
            letter-spacing: 1.2px;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .zelt-card-icon {{
            width: 28px; height: 28px;
            background: {BRAND['cream_dark']};
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }}
        .zelt-card-value {{
            font-family: 'Playfair Display', serif;
            font-size: 2rem;
            font-weight: 700;
            color: {BRAND['primary_dark']};
            line-height: 1.1;
        }}
        .zelt-card-foot {{
            font-size: 0.82rem;
            color: {BRAND['text_muted']};
            margin-top: 0.4rem;
        }}

        div[data-testid="stMetric"] {{
            background: white;
            border: 1px solid rgba(74, 107, 58, 0.10);
            border-radius: 14px;
            padding: 1.1rem 1.2rem;
            box-shadow: 0 2px 10px rgba(45, 58, 42, 0.04);
        }}
        div[data-testid="stMetricLabel"] p {{
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            color: {BRAND['text_muted']} !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        div[data-testid="stMetricValue"] {{
            font-family: 'Playfair Display', serif;
            font-size: 1.9rem !important;
            color: {BRAND['primary_dark']} !important;
        }}

        .stButton > button {{
            background: {BRAND['primary']};
            color: {BRAND['cream']};
            border: none;
            border-radius: 10px;
            padding: 0.55rem 1.4rem;
            font-weight: 600;
            transition: all 0.2s;
        }}
        .stButton > button:hover {{
            background: {BRAND['primary_dark']};
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(74, 107, 58, 0.25);
        }}

        hr {{
            border: none;
            border-top: 1px solid rgba(74, 107, 58, 0.12);
            margin: 2rem 0;
        }}

        .zelt-section-title {{
            font-family: 'Playfair Display', serif;
            font-size: 1.4rem;
            color: {BRAND['primary_dark']};
            margin: 0.5rem 0 1rem 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .zelt-section-title::before {{
            content: '';
            width: 4px; height: 22px;
            background: {BRAND['accent']};
            border-radius: 2px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str | None = None, subtitle: str | None = None) -> None:
    title = title or BRAND["name"]
    subtitle = subtitle or "ติดตามยอดขาย • วิเคราะห์ Creator • ตามเป้าหมายแคมเปญ — แบบ real-time"
    st.markdown(
        f"""
        <div class="zelt-hero">
            <div class="zelt-hero-logo">
                <div class="zelt-hero-mark">Z</div>
                <div>
                    <div class="zelt-hero-tag">{BRAND['tagline']}</div>
                    <div class="zelt-hero-name">{title}</div>
                </div>
            </div>
            <div class="zelt-hero-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, icon: str = "•", foot: str = "") -> str:
    return f"""
    <div class="zelt-card">
        <div class="zelt-card-label"><span class="zelt-card-icon">{icon}</span>{label}</div>
        <div class="zelt-card-value">{value}</div>
        <div class="zelt-card-foot">{foot}</div>
    </div>
    """


def section_title(text: str) -> None:
    st.markdown(f'<div class="zelt-section-title">{text}</div>', unsafe_allow_html=True)


def sidebar_brand() -> None:
    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding: 0.5rem 0 1.2rem 0; border-bottom: 1px solid rgba(74,107,58,0.12); margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width:38px;height:38px;background:{BRAND['primary']};color:{BRAND['cream']};
                                border-radius:10px;display:flex;align-items:center;justify-content:center;
                                font-family:'Playfair Display',serif;font-size:22px;font-weight:700;">Z</div>
                    <div>
                        <div style="font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:700;color:{BRAND['primary_dark']};line-height:1;">Zelt</div>
                        <div style="font-size:0.7rem;color:{BRAND['text_muted']};letter-spacing:1.5px;text-transform:uppercase;">Dashboard</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
