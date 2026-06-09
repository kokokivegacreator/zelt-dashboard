import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from . import format as F


PALETTE = ["#FF6B35", "#F7931E", "#FFD23F", "#06A77D", "#005377", "#9F86C0"]


def kpi(label: str, value, delta=None, help_text: str | None = None):
    st.metric(label, value, delta=delta, help=help_text)


def line_trend(df: pd.DataFrame, x: str, y: str, color: str | None = None,
               title: str = "", target: float | None = None):
    fig = px.line(df, x=x, y=y, color=color, markers=True,
                  title=title, color_discrete_sequence=PALETTE)
    if target:
        fig.add_hline(y=target, line_dash="dash", line_color="red",
                      annotation_text=f"Target: {F.fmt_compact(target)}")
    fig.update_layout(hovermode="x unified", height=380)
    return fig


def bar_top(df: pd.DataFrame, x: str, y: str, title: str = "", orientation: str = "h"):
    fig = px.bar(df, x=x, y=y, orientation=orientation, title=title,
                 color_discrete_sequence=PALETTE)
    fig.update_layout(height=400)
    return fig


def donut(labels: list, values: list, title: str = ""):
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.45,
                                  marker=dict(colors=PALETTE))])
    fig.update_layout(title=title, height=350)
    return fig


def progress_bar(actual: float, target: float, label: str):
    pct = (actual / target * 100) if target else 0
    pct = min(pct, 100)
    color = "#06A77D" if pct >= 80 else "#F7931E" if pct >= 50 else "#FF6B35"
    st.markdown(f"**{label}**")
    st.progress(pct / 100, text=f"{F.fmt_compact(actual)} / {F.fmt_compact(target)} ({pct:.1f}%)")
