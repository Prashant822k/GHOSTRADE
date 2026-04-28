"""
ui/charts.py  ·  GHOSTRADE Plotly Chart Builders
=================================================
All chart construction isolated here.
Every figure uses explicit margin, no _BASE_LAYOUT merging that can
produce duplicate-keyword errors.
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Brand palette ─────────────────────────────────────────────────────────
_CARD    = "#0D0D1F"
_PURPLE  = "#7C6FFF"
_TEAL    = "#5DCAA5"
_GOLD    = "#F0C040"
_RED     = "#E05A5A"
_TP      = "#FFFFFF"
_TS      = "#6A6A8A"

_FONT = dict(family="Inter, sans-serif", color=_TP)


def _base(height: int, margin: dict | None = None) -> dict:
    """Returns a base layout dict — no margin so callers set it explicitly."""
    m = margin or dict(l=20, r=20, t=44, b=20)
    return dict(
        paper_bgcolor = _CARD,
        plot_bgcolor  = _CARD,
        font          = _FONT,
        height        = height,
        margin        = m,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Gauge
# ─────────────────────────────────────────────────────────────────────────────

def build_gauge(trust_score: float, color: str) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode  = "gauge+number",
        value = trust_score,
        number = dict(
            font   = dict(color=color, size=60, family="Inter, sans-serif"),
            suffix = "",
        ),
        gauge = dict(
            axis = dict(
                range    = [0, 100],
                tickwidth = 1,
                tickcolor = _TS,
                tickfont  = dict(color=_TS, size=10),
                nticks   = 6,
            ),
            bar         = dict(color=color, thickness=0.24),
            bgcolor     = _CARD,
            borderwidth = 0,
            steps = [
                dict(range=[0,  29], color="rgba(224, 90, 90, 0.13)"),
                dict(range=[30, 69], color="rgba(240,192, 64, 0.10)"),
                dict(range=[70,100], color="rgba( 93,202,165, 0.10)"),
            ],
            threshold = dict(
                line      = dict(color=color, width=3),
                thickness = 0.80,
                value     = trust_score,
            ),
        ),
    ))
    fig.update_layout(
        paper_bgcolor = _CARD,
        plot_bgcolor  = _CARD,
        font          = _FONT,
        height        = 240,
        margin        = dict(l=32, r=32, t=10, b=0),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Price chart
# ─────────────────────────────────────────────────────────────────────────────

def build_price_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    # ── Main line ──────────────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x    = df.index,
        y    = df["Close"],
        mode = "lines",
        line = dict(color=_PURPLE, width=2.0, shape="spline", smoothing=0.6),
        name = "Close Price",
        fill = "tozeroy",
        fillcolor = "rgba(124,111,255,0.06)",
        hovertemplate = "<b>%{x|%b %d, %Y}</b><br>$%{y:,.2f}<extra></extra>",
    ))

    # ── Anomaly markers ────────────────────────────────────────────────────
    is_anom = df.get("is_anomaly", pd.Series(False, index=df.index))
    adf = df[is_anom == True]

    if not adf.empty:
        fig.add_trace(go.Scatter(
            x    = adf.index,
            y    = adf["Close"],
            mode = "markers",
            marker = dict(
                color  = _RED,
                size   = 10,
                symbol = "circle",
                line   = dict(color="#ffffff", width=1.5),
            ),
            name = "⚠ Anomaly",
            hovertemplate = "<b>%{x|%b %d, %Y}</b><br>$%{y:,.2f}<br><i>Anomalous day</i><extra></extra>",
        ))
        for date in adf.index:
            fig.add_vrect(
                x0=date, x1=date,
                fillcolor=_RED, opacity=0.08,
                layer="below", line_width=0,
            )

    fig.update_layout(
        **_base(300),
        title = dict(
            text = "<b>Price History</b>  ·  <span style='color:#E05A5A'>● Anomaly</span>",
            font = dict(size=13, color=_TS, family="Inter, sans-serif"),
            x=0, xanchor="left", pad=dict(l=0),
        ),
        xaxis = dict(
            showgrid=False, zeroline=False,
            tickfont=dict(color=_TS, size=10),
            color=_TS,
        ),
        yaxis = dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.04)",
            zeroline=False,
            tickprefix="$",
            tickfont=dict(color=_TS, size=10),
            color=_TS,
        ),
        legend = dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            font=dict(size=11, color=_TS),
            bgcolor="rgba(0,0,0,0)",
        ),
        hovermode="x unified",
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Volume chart
# ─────────────────────────────────────────────────────────────────────────────

def build_volume_chart(df: pd.DataFrame) -> go.Figure:
    is_anom = df.get("is_anomaly", pd.Series(False, index=df.index))
    colors  = [_RED if a else _PURPLE for a in is_anom]

    # Opacity: anomalous bars fully opaque, normal slightly muted
    opacities = [1.0 if a else 0.70 for a in is_anom]

    fig = go.Figure(go.Bar(
        x             = df.index,
        y             = df["Volume"],
        marker        = dict(color=colors, opacity=opacities, line=dict(width=0)),
        name          = "Volume",
        hovertemplate = "<b>%{x|%b %d, %Y}</b><br>%{y:,.0f} shares<extra></extra>",
    ))

    fig.update_layout(
        **_base(210),
        title = dict(
            text = (
                "<b>Daily Volume</b>  ·  "
                "<span style='color:#E05A5A'>■ Anomaly</span>  "
                "<span style='color:#7C6FFF'>■ Normal</span>"
            ),
            font = dict(size=13, color=_TS, family="Inter, sans-serif"),
            x=0, xanchor="left",
        ),
        xaxis = dict(
            showgrid=False, zeroline=False,
            tickfont=dict(color=_TS, size=10), color=_TS,
        ),
        yaxis = dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.04)",
            zeroline=False,
            tickfont=dict(color=_TS, size=10), color=_TS,
        ),
        bargap=0.2,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Signal radar
# ─────────────────────────────────────────────────────────────────────────────

def build_signal_radar(result: dict) -> go.Figure:
    df   = result["df"]
    cols = ["VAI_z", "VBS_z", "PVD_z", "LIP_z"]
    # Short labels that fit in the radar without clipping
    names = ["Volume", "Volatility", "Price-Vol", "Liquidity"]

    df_v = df.dropna(subset=cols)
    if df_v.empty:
        return go.Figure()

    latest = df_v.iloc[-1]
    vals   = [abs(float(latest[c])) for c in cols]
    max_r  = max(max(vals) * 1.3, 3.5)

    # Close polygon
    vals_c  = vals + [vals[0]]
    names_c = names + [names[0]]

    fig = go.Figure()

    # ── Filled polygon ─────────────────────────────────────────────────────
    fig.add_trace(go.Scatterpolar(
        r         = vals_c,
        theta     = names_c,
        fill      = "toself",
        fillcolor = "rgba(124,111,255,0.18)",
        line      = dict(color=_PURPLE, width=2.2),
        name      = "|Z|",
        hovertemplate = "<b>%{theta}</b>: %{r:.2f}σ<extra></extra>",
    ))

    # ── 2σ ring ────────────────────────────────────────────────────────────
    fig.add_trace(go.Scatterpolar(
        r         = [2.0] * 5,
        theta     = names_c,
        mode      = "lines",
        line      = dict(color=_RED, width=1.4, dash="dot"),
        name      = "2σ line",
        hoverinfo = "skip",
    ))

    fig.update_layout(
        paper_bgcolor = _CARD,
        plot_bgcolor  = _CARD,
        font          = dict(family="Inter, sans-serif", color=_TP),
        height        = 290,
        margin        = dict(l=28, r=28, t=44, b=36),
        title = dict(
            text = "<b>Signal Intensity</b>",
            font = dict(size=13, color=_TS, family="Inter, sans-serif"),
            x=0, xanchor="left",
        ),
        polar = dict(
            bgcolor     = _CARD,
            radialaxis  = dict(
                visible   = True,
                range     = [0, max_r],
                color     = _TS,
                gridcolor = "rgba(255,255,255,0.07)",
                tickfont  = dict(size=9),
                showline  = False,
            ),
            angularaxis = dict(
                color     = _TS,
                gridcolor = "rgba(255,255,255,0.07)",
                tickfont  = dict(size=11, color=_TP),
            ),
        ),
        legend = dict(
            orientation="h",
            yanchor="top", y=-0.05,
            xanchor="center", x=0.5,
            font=dict(size=10, color=_TS),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=True,
    )
    return fig
