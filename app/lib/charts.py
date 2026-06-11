import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from . import format as F
from .style import BRAND, PLOTLY_COLORWAY


PALETTE = PLOTLY_COLORWAY


def _apply_theme(fig: go.Figure, height: int = 380) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans Thai, sans-serif", color=BRAND["text"], size=12),
        title=dict(font=dict(family="IBM Plex Sans Thai, sans-serif", size=15,
                             color=BRAND["primary_dark"])),
        margin=dict(l=10, r=10, t=40, b=20),
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.22,
            xanchor="center", x=0.5,
            font=dict(size=11, color=BRAND["text_muted"]),
        ),
        hoverlabel=dict(
            bgcolor="white",
            font=dict(family="IBM Plex Sans Thai, sans-serif", color=BRAND["text"]),
            bordercolor=BRAND["primary"],
        ),
        colorway=PLOTLY_COLORWAY,
    )
    fig.update_xaxes(
        showgrid=False,
        showline=True, linewidth=1, linecolor="rgba(74,107,58,0.15)",
        tickfont=dict(color=BRAND["text_muted"], size=11),
    )
    fig.update_yaxes(
        showgrid=True, gridcolor="rgba(74,107,58,0.08)",
        showline=False, zeroline=False,
        tickfont=dict(color=BRAND["text_muted"], size=11),
    )
    return fig


def kpi(label: str, value, delta=None, help_text: str | None = None):
    st.metric(label, value, delta=delta, help=help_text)


def line_trend(df: pd.DataFrame, x: str, y: str, color: str | None = None,
               title: str = "", target: float | None = None):
    fig = px.line(df, x=x, y=y, color=color, markers=True,
                  title=title, color_discrete_sequence=PALETTE)
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=7, line=dict(width=2, color="white")),
        hovertemplate="<b>%{x}</b><br>%{y:,.0f}<extra></extra>",
    )
    if target:
        fig.add_hline(
            y=target,
            line=dict(dash="dash", color=BRAND["accent_dark"], width=2),
            annotation_text=f"Target: {F.fmt_compact(target)}",
            annotation_position="top right",
            annotation_font=dict(color=BRAND["accent_dark"], size=11),
        )
    _apply_theme(fig, height=380)
    fig.update_layout(hovermode="x unified")
    return fig


def bar_top(df: pd.DataFrame, x: str, y: str, title: str = "", orientation: str = "h"):
    fig = px.bar(df, x=x, y=y, orientation=orientation, title=title,
                 color_discrete_sequence=PALETTE)
    fig.update_traces(marker=dict(line=dict(width=0)))
    _apply_theme(fig, height=400)
    return fig


def donut(labels: list, values: list, title: str = ""):
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.62,
        marker=dict(colors=PALETTE, line=dict(color="white", width=3)),
        textfont=dict(family="IBM Plex Sans Thai, sans-serif", size=12),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} (%{percent})<extra></extra>",
    )])
    fig.update_layout(title=title)
    _apply_theme(fig, height=340)
    return fig


def progress_bar(actual: float, target: float, label: str, kind: str = "currency"):
    """kind: 'currency' (฿1.2M) | 'number' (1.2M) | 'int' (1,234)"""
    pct = (actual / target * 100) if target else 0
    pct_capped = min(pct, 100)
    color = BRAND["success"] if pct >= 80 else (BRAND["accent_dark"] if pct >= 50 else BRAND["danger"])
    if kind == "currency":
        fmt = F.fmt_compact
    elif kind == "int":
        fmt = lambda v: F.fmt_int(int(v or 0))
    else:
        fmt = F.fmt_int_compact
    st.markdown(
        f"""
        <div style="margin-bottom: 1rem;">
            <div style="display:flex;justify-content:space-between;
                        font-size:0.85rem;margin-bottom:6px;">
                <span style="font-weight:600;color:{BRAND['text']};">{label}</span>
                <span style="color:{BRAND['text_muted']};">
                    {fmt(actual)} / {fmt(target)}
                    <strong style="color:{color};margin-left:8px;">{pct:.1f}%</strong>
                </span>
            </div>
            <div style="background:{BRAND['cream_dark']};border-radius:8px;height:10px;overflow:hidden;">
                <div style="width:{pct_capped}%;height:100%;
                            background:linear-gradient(90deg,{color} 0%,{BRAND['accent']} 100%);
                            border-radius:8px;transition:width 0.6s ease;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
