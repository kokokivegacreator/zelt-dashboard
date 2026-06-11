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

        .zelt-subhero {{
            background: linear-gradient(135deg, {BRAND['cream_dark']} 0%, {BRAND['cream']} 100%);
            border: 1px solid rgba(74, 107, 58, 0.10);
            border-radius: 16px;
            padding: 1.6rem 1.8rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1.5rem;
            flex-wrap: wrap;
        }}
        .zelt-subhero-left {{ flex: 1; min-width: 280px; }}
        .zelt-subhero-eyebrow {{
            font-size: 0.72rem;
            letter-spacing: 3px;
            text-transform: uppercase;
            color: {BRAND['accent_dark']};
            font-weight: 600;
            margin-bottom: 0.3rem;
        }}
        .zelt-subhero-title {{
            font-family: 'Playfair Display', serif;
            font-size: 2rem;
            font-weight: 700;
            color: {BRAND['primary_dark']};
            line-height: 1.15;
            margin: 0;
        }}
        .zelt-subhero-sub {{
            font-size: 0.95rem;
            color: {BRAND['text_muted']};
            margin-top: 0.35rem;
        }}

        .zelt-kpi {{
            background: white;
            border: 1px solid rgba(74, 107, 58, 0.10);
            border-radius: 16px;
            padding: 1.3rem 1.4rem;
            box-shadow: 0 2px 12px rgba(45, 58, 42, 0.04);
            transition: all 0.25s ease;
            height: 100%;
            position: relative;
            overflow: hidden;
        }}
        .zelt-kpi::before {{
            content: '';
            position: absolute;
            top: 0; left: 0;
            width: 4px; height: 100%;
            background: {BRAND['accent']};
            opacity: 0.7;
        }}
        .zelt-kpi:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 28px rgba(45, 58, 42, 0.10);
        }}
        .zelt-kpi-label {{
            font-size: 0.75rem;
            font-weight: 600;
            color: {BRAND['text_muted']};
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 0.6rem;
        }}
        .zelt-kpi-value {{
            font-family: 'Playfair Display', serif;
            font-size: 1.85rem;
            font-weight: 700;
            color: {BRAND['primary_dark']};
            line-height: 1.1;
        }}
        .zelt-kpi-delta {{
            display: inline-block;
            font-size: 0.78rem;
            font-weight: 600;
            margin-top: 0.5rem;
            padding: 2px 8px;
            border-radius: 6px;
        }}
        .zelt-kpi-delta.up {{ background: {BRAND['success']}22; color: {BRAND['success']}; }}
        .zelt-kpi-delta.down {{ background: {BRAND['danger']}22; color: {BRAND['danger']}; }}
        .zelt-kpi-delta.flat {{ background: {BRAND['cream_dark']}; color: {BRAND['text_muted']}; }}

        .zelt-chart-card {{
            background: white;
            border: 1px solid rgba(74, 107, 58, 0.10);
            border-radius: 16px;
            padding: 1.3rem 1.4rem 0.6rem 1.4rem;
            box-shadow: 0 2px 12px rgba(45, 58, 42, 0.04);
            margin-bottom: 1.2rem;
        }}
        .zelt-chart-title {{
            font-family: 'Playfair Display', serif;
            font-size: 1.15rem;
            color: {BRAND['primary_dark']};
            margin: 0 0 0.5rem 0;
        }}
        .zelt-chart-cap {{
            font-size: 0.8rem;
            color: {BRAND['text_muted']};
            margin-bottom: 0.6rem;
        }}

        .zelt-rank-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.7rem 0.2rem;
            border-bottom: 1px solid rgba(74, 107, 58, 0.08);
        }}
        .zelt-rank-row:last-child {{ border-bottom: none; }}
        .zelt-rank-left {{
            display: flex; align-items: center; gap: 12px;
            flex: 1; min-width: 0;
        }}
        .zelt-rank-num {{
            width: 28px; height: 28px;
            background: {BRAND['cream_dark']};
            color: {BRAND['primary_dark']};
            border-radius: 8px;
            display: flex; align-items: center; justify-content: center;
            font-weight: 700; font-size: 0.85rem;
            flex-shrink: 0;
        }}
        .zelt-rank-row:nth-child(1) .zelt-rank-num {{
            background: {BRAND['accent']}; color: {BRAND['primary_dark']};
        }}
        .zelt-rank-name {{
            font-weight: 500;
            color: {BRAND['text']};
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }}
        .zelt-rank-val {{
            font-family: 'Playfair Display', serif;
            font-weight: 700;
            color: {BRAND['primary_dark']};
            font-size: 0.95rem;
            flex-shrink: 0;
            margin-left: 12px;
        }}

        div[data-testid="stDateInput"] label,
        div[data-testid="stSelectbox"] label {{
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            color: {BRAND['text_muted']} !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .zelt-chip {{
            display: inline-block;
            background: {BRAND['accent']}25;
            color: {BRAND['accent_dark']};
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.78rem;
            font-weight: 600;
            margin: 2px 4px 2px 0;
            border: 1px solid {BRAND['accent']}40;
        }}
        .zelt-chip-sage {{
            background: {BRAND['primary']}15;
            color: {BRAND['primary_dark']};
            border-color: {BRAND['primary']}30;
        }}

        .zelt-badge {{
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 600;
            padding: 2px 10px;
            border-radius: 10px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}
        .zelt-badge.active {{ background: {BRAND['success']}22; color: {BRAND['success']}; }}
        .zelt-badge.done {{ background: {BRAND['text_muted']}22; color: {BRAND['text_muted']}; }}
        .zelt-badge.upcoming {{ background: {BRAND['accent']}25; color: {BRAND['accent_dark']}; }}

        .zelt-item-card {{
            background: white;
            border: 1px solid rgba(74, 107, 58, 0.10);
            border-radius: 14px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 10px rgba(45, 58, 42, 0.03);
        }}
        .zelt-item-head {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            margin-bottom: 0.4rem;
            flex-wrap: wrap;
        }}
        .zelt-item-title {{
            font-family: 'Playfair Display', serif;
            font-size: 1.2rem;
            font-weight: 700;
            color: {BRAND['primary_dark']};
        }}
        .zelt-item-meta {{
            font-size: 0.82rem;
            color: {BRAND['text_muted']};
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


def subpage_hero(eyebrow: str, title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="zelt-subhero">
            <div class="zelt-subhero-left">
                <div class="zelt-subhero-eyebrow">{eyebrow}</div>
                <div class="zelt-subhero-title">{title}</div>
                <div class="zelt-subhero-sub">{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, delta: str | None = None,
             delta_dir: str = "flat") -> str:
    delta_html = ""
    if delta:
        arrow = "▲" if delta_dir == "up" else ("▼" if delta_dir == "down" else "•")
        delta_html = f'<div class="zelt-kpi-delta {delta_dir}">{arrow} {delta}</div>'
    return f"""
    <div class="zelt-kpi">
        <div class="zelt-kpi-label">{label}</div>
        <div class="zelt-kpi-value">{value}</div>
        {delta_html}
    </div>
    """


def chart_card_open(title: str, caption: str = "") -> None:
    cap = f'<div class="zelt-chart-cap">{caption}</div>' if caption else ""
    st.markdown(
        f'<div class="zelt-chart-card"><div class="zelt-chart-title">{title}</div>{cap}',
        unsafe_allow_html=True,
    )


def chart_card_close() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def rank_list(items: list[tuple[str, str]]) -> None:
    rows = "".join(
        f"""
        <div class="zelt-rank-row">
            <div class="zelt-rank-left">
                <div class="zelt-rank-num">{i+1}</div>
                <div class="zelt-rank-name">{name}</div>
            </div>
            <div class="zelt-rank-val">{val}</div>
        </div>
        """
        for i, (name, val) in enumerate(items)
    )
    st.markdown(rows, unsafe_allow_html=True)


def chips(tags: list[str], style: str = "gold") -> str:
    if not tags:
        return ""
    cls = "zelt-chip" if style == "gold" else "zelt-chip zelt-chip-sage"
    return "".join(f'<span class="{cls}">#{t}</span>' for t in tags)


def badge(text: str, kind: str = "active") -> str:
    return f'<span class="zelt-badge {kind}">{text}</span>'


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
