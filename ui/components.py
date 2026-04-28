"""
ui/components.py  ·  GHOSTRADE Reusable Streamlit Components
=============================================================
Rules strictly followed in this file:
  1. Every st.markdown() call that contains HTML uses unsafe_allow_html=True.
  2. No HTML block is opened without being closed in the SAME st.markdown() call.
  3. No HTML tags are mixed with st.plotly_chart() in the same "visual card".
  4. HTML strings are built as plain Python string variables — NOT as nested
     f-strings inside f-strings (which break with braces inside CSS).
"""

import streamlit as st

# ── PRD palette ──────────────────────────────────────────────────────────
_CARD    = "#0D0D1F"
_PURPLE  = "#7C6FFF"
_TEAL    = "#5DCAA5"
_GOLD    = "#F0C040"
_RED     = "#E05A5A"
_TP      = "#FFFFFF"
_TS      = "#6A6A8A"
_BORDER  = "rgba(124,111,255,0.20)"


# ─────────────────────────────────────────────────────────────────────────────
# Global CSS
# ─────────────────────────────────────────────────────────────────────────────

def inject_global_css() -> None:
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        max-width: 1180px;
    }

    /* Metric widget */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.70rem !important;
        color: #6A6A8A !important;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        font-weight: 500;
    }
    [data-testid="stMetricDelta"] { display: none; }

    /* Text input */
    [data-testid="stTextInput"] input {
        background    : #0D0D1F !important;
        color         : #FFFFFF !important;
        border        : 1.5px solid rgba(124,111,255,0.40) !important;
        border-radius : 10px !important;
        font-size     : 1rem;
        padding       : 11px 16px;
        transition    : border-color .2s ease, box-shadow .2s ease;
    }
    [data-testid="stTextInput"] input:focus {
        border-color : #7C6FFF !important;
        box-shadow   : 0 0 0 3px rgba(124,111,255,0.25) !important;
        outline      : none;
    }
    [data-testid="stTextInput"] input::placeholder { color: #6A6A8A; }

    /* Primary button */
    button[kind="primary"] {
        background    : linear-gradient(135deg, #7C6FFF 0%, #5A4FBF 100%) !important;
        color         : white !important;
        border        : none !important;
        border-radius : 10px !important;
        font-weight   : 600 !important;
        font-size     : 0.9rem !important;
        height        : 46px;
        transition    : all .2s ease;
    }
    button[kind="primary"]:hover {
        opacity   : 0.88;
        transform : translateY(-1px);
        box-shadow: 0 6px 24px rgba(124,111,255,0.45);
    }

    /* Spinner */
    .stSpinner > div { border-top-color: #7C6FFF !important; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(124,111,255,0.5); border-radius: 10px; }

    /* Card utility class */
    .g-card {
        background    : #0D0D1F;
        border        : 1px solid rgba(124,111,255,0.20);
        border-radius : 14px;
        padding       : 22px 24px;
    }

    /* Label utility */
    .g-label {
        font-size     : 0.68rem;
        color         : #6A6A8A;
        text-transform: uppercase;
        letter-spacing: 1.8px;
        font-weight   : 600;
        margin-bottom : 5px;
    }

    /* Chip badges */
    .chip {
        display      : inline-block;
        padding      : 3px 11px;
        border-radius: 20px;
        font-size    : 0.74rem;
        font-weight  : 600;
        letter-spacing: .5px;
        cursor       : default;
    }
    .chip-teal   { color:#5DCAA5; background:rgba(93,202,165,.12);  border:1px solid rgba(93,202,165,.35); }
    .chip-red    { color:#E05A5A; background:rgba(224,90,90,.12);   border:1px solid rgba(224,90,90,.35); }
    .chip-gold   { color:#F0C040; background:rgba(240,192,64,.12);  border:1px solid rgba(240,192,64,.35); }
    .chip-purple { color:#7C6FFF; background:rgba(124,111,255,.12); border:1px solid rgba(124,111,255,.35); }

    /* Plotly iframe containers */
    [data-testid="stPlotlyChart"] { border-radius: 14px; overflow: hidden; }

    @keyframes gpulse {
        0%,100% { opacity:1; transform:scale(1); }
        50%      { opacity:.3; transform:scale(.85); }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────

def render_header() -> None:
    html = (
        "<div style='text-align:center; padding:16px 0 8px;'>"
        "<div style='font-size:2.8rem; font-weight:900; letter-spacing:4px; line-height:1;'>"
        "GHOST"
        "<span style='color:#7C6FFF;'>TRADE</span>"
        "</div>"
        "<div style='display:inline-flex; align-items:center; gap:8px; color:#6A6A8A;"
        " font-size:0.78rem; margin-top:8px; letter-spacing:1.6px; text-transform:uppercase;'>"
        "<span style='width:8px; height:8px; background:#5DCAA5; border-radius:50%;"
        " display:inline-block; box-shadow:0 0 8px #5DCAA5;"
        " animation:gpulse 2.2s ease-in-out infinite;'></span>"
        "LIVE &nbsp;&middot;&nbsp; Market Integrity Engine &nbsp;&middot;&nbsp; Real-Time Audit"
        "</div>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Ticker card
# ─────────────────────────────────────────────────────────────────────────────

def render_ticker_card(ticker: str, df) -> None:
    last_close  = float(df["Close"].iloc[-1])
    first_date  = df.index[0].strftime("%b %d, %Y")
    last_date   = df.index[-1].strftime("%b %d, %Y")
    n_days      = len(df)
    is_anomaly  = df.get("is_anomaly")
    n_anoms     = int(is_anomaly.sum()) if is_anomaly is not None else 0
    anom_color  = "#E05A5A" if n_anoms > 0 else "#5DCAA5"

    html = (
        "<div class='g-card' style='height:100%; box-sizing:border-box;'>"

        "<div class='g-label'>Ticker</div>"
        "<div style='font-size:2.2rem; font-weight:900; color:#7C6FFF;"
        " letter-spacing:3px; margin-bottom:16px; line-height:1.1;'>"
        + ticker +
        "</div>"

        "<div class='g-label'>Last Close</div>"
        "<div style='font-size:1.7rem; font-weight:700; color:#FFFFFF; margin-bottom:18px;'>"
        "$" + f"{last_close:,.2f}" +
        "</div>"

        "<div style='display:grid; grid-template-columns:1fr 1fr; gap:14px;'>"

        "<div>"
        "<div class='g-label'>Data From</div>"
        "<div style='color:#FFFFFF; font-size:0.86rem; font-weight:500;'>" + first_date + "</div>"
        "</div>"

        "<div>"
        "<div class='g-label'>To</div>"
        "<div style='color:#FFFFFF; font-size:0.86rem; font-weight:500;'>" + last_date + "</div>"
        "</div>"

        "<div>"
        "<div class='g-label'>Window</div>"
        "<div style='color:#FFFFFF; font-size:0.86rem; font-weight:500;'>" + str(n_days) + " trading days</div>"
        "</div>"

        "<div>"
        "<div class='g-label'>Flagged Days</div>"
        "<div style='color:" + anom_color + "; font-size:0.86rem; font-weight:700;'>"
        + str(n_anoms) + " anomal" + ("y" if n_anoms == 1 else "ies") +
        "</div>"
        "</div>"

        "</div>"   # grid
        "</div>"   # g-card
    )
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Classification badge (used above gauge)
# ─────────────────────────────────────────────────────────────────────────────

def render_classification_badge(label: str, color: str, emoji: str) -> None:
    html = (
        "<div style='text-align:center; margin-bottom:6px;'>"
        "<div class='g-label' style='margin-bottom:8px;'>Trust Score</div>"
        "<span style='"
        "display:inline-block; color:" + color + "; font-size:0.88rem;"
        " font-weight:700; padding:4px 18px; border-radius:20px;"
        " border:1px solid " + color + "55; background:" + color + "18;"
        " letter-spacing:.8px; text-transform:uppercase;'>"
        + emoji + " " + label +
        "</span>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Stats row — using native st.metric wrapped in custom HTML cards
# ─────────────────────────────────────────────────────────────────────────────

def render_stats_row(result: dict) -> None:
    vol_pct     = result["volume_spike_pct"]
    price_delta = result["price_delta_3mo"]
    active      = result["active_signals"]

    vol_color   = _RED if abs(vol_pct) > 50 else (_GOLD if abs(vol_pct) > 20 else _TEAL)
    price_color = _TEAL if price_delta >= 0 else _RED
    sig_color   = _RED if active >= 3 else (_GOLD if active >= 1 else _TEAL)

    c1, c2, c3 = st.columns(3, gap="medium")

    def _card(col, label, value, sub, color):
        col.markdown(
            "<div class='g-card' style='text-align:center; padding:18px 12px;'>"
            "<div class='g-label'>" + label + "</div>"
            "<div style='font-size:1.55rem; font-weight:700; color:" + color
            + "; margin:6px 0 3px; line-height:1.2;'>" + value + "</div>"
            "<div style='font-size:0.70rem; color:#6A6A8A;'>" + sub + "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    _card(c1, "Volume vs 20D Avg",   f"{vol_pct:+.1f}%",     "Volume spike indicator", vol_color)
    _card(c2, "3-Month Price Delta", f"{price_delta:+.2f}%",  "Return over window",     price_color)
    _card(c3, "Active Signals",      f"{active} / 4",         "Signals above 2σ",       sig_color)


# ─────────────────────────────────────────────────────────────────────────────
# Anomaly explainer card
# ─────────────────────────────────────────────────────────────────────────────

def render_explainer_card(result: dict) -> None:
    top_flag    = result["top_flag"]
    sigma       = result["top_flag_sigma"]
    trust       = result["trust_score"]
    label       = result["label"]
    color       = result["color"]
    emoji       = result["emoji"]
    vol_pct     = result["volume_spike_pct"]
    active      = result["active_signals"]
    price_delta = result["price_delta_3mo"]

    direction = "above" if sigma >= 0 else "below"
    abs_sigma = abs(sigma)

    # Build bullet items as individual strings (no nested f-strings with HTML)
    b1 = (
        "<li style='margin-bottom:6px;'>The <strong>" + top_flag + "</strong> signal reached "
        "<strong style='color:" + color + ";'>" + f"{abs_sigma:.1f}σ" + "</strong> "
        + direction + " its 3-month baseline.</li>"
    )

    b2 = ""
    if abs(vol_pct) > 20:
        dir_w = "above" if vol_pct > 0 else "below"
        b2 = (
            "<li style='margin-bottom:6px;'>Volume was <strong>" + f"{abs(vol_pct):.0f}%" + "</strong> "
            + dir_w + " its 20-day rolling average.</li>"
        )

    b3 = ""
    if active > 0:
        b3 = (
            "<li style='margin-bottom:6px;'><strong>" + str(active) + " of 4</strong> "
            "signals crossed the 2σ anomaly threshold.</li>"
        )

    price_dir = "gained" if price_delta >= 0 else "lost"
    b4 = (
        "<li style='margin-bottom:6px;'>The ticker <strong>" + price_dir + " "
        + f"{abs(price_delta):.2f}%" + "</strong> over the 3-month window.</li>"
    )

    verdict = {
        "Stable":      "The price move appears statistically consistent with historical behaviour. Manipulation probability is low.",
        "Suspicious":  "One or more signals show abnormal patterns. Exercise caution before acting on this move.",
        "Ghost Trade": "Multiple signals confirm a structural anomaly. High probability of manufactured or manipulated activity.",
    }.get(label, "")

    html = (
        "<div style='"
        "background:#0D0D1F; border:1px solid #F0C040;"
        "border-radius:14px; padding:24px 28px;'>"

        "<div style='display:flex; align-items:center; gap:10px; margin-bottom:14px;'>"
        "<span style='font-size:1.2rem;'>⭐</span>"
        "<span style='font-size:0.68rem; color:#6A6A8A; text-transform:uppercase;"
        " letter-spacing:2px; font-weight:600;'>Anomaly Insight</span>"
        "</div>"

        "<ul style='margin:0 0 16px 0; padding-left:18px;"
        " font-size:0.94rem; line-height:1.8; color:#FFFFFF;'>"
        + b1 + b2 + b3 + b4 +
        "</ul>"

        "<div style='"
        "background:" + color + "12; border-left:3px solid " + color + ";"
        "border-radius:0 8px 8px 0; padding:12px 16px;"
        "font-size:0.88rem; line-height:1.6; color:#FFFFFF;'>"
        "<strong style='color:" + color + ";'>" + emoji + " " + label
        + " — Trust Score " + str(trust) + "</strong><br>"
        + verdict +
        "</div>"

        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Signal Z-score table
# ─────────────────────────────────────────────────────────────────────────────

def render_signal_table(df) -> None:
    SIGNAL_MAP = {
        "VAI_z": "Volume Anomaly",
        "VBS_z": "Volatility Burst",
        "PVD_z": "Price-Vol Diverg.",
        "LIP_z": "Liquidity Instab.",
    }

    df_valid = df.dropna(subset=list(SIGNAL_MAP.keys()))
    if df_valid.empty:
        return

    latest = df_valid.iloc[-1]
    rows_html = ""

    for col, name in SIGNAL_MAP.items():
        z = float(latest[col])
        if abs(z) > 2.0:
            c, icon, bg = "#E05A5A", "🔴", "rgba(224,90,90,0.07)"
        elif abs(z) > 1.5:
            c, icon, bg = "#F0C040", "🟡", "rgba(240,192,64,0.07)"
        else:
            c, icon, bg = "#5DCAA5", "🟢", "rgba(93,202,165,0.05)"

        z_str = f"{z:+.2f}σ"
        rows_html += (
            "<tr style='background:" + bg + "; border-bottom:1px solid rgba(255,255,255,0.04);'>"
            "<td style='padding:9px 14px; font-size:0.82rem; color:#FFFFFF; font-weight:500;'>"
            + name + "</td>"
            "<td style='padding:9px 14px; font-size:0.88rem; color:" + c
            + "; font-weight:700; text-align:right; font-family:monospace;'>"
            + z_str + "</td>"
            "<td style='padding:9px 10px; text-align:center; font-size:0.85rem;'>" + icon + "</td>"
            "</tr>"
        )

    html = (
        "<div class='g-card' style='padding:16px 0 6px;'>"
        "<div style='padding:0 14px 10px;'>"
        "<div class='g-label'>Signal Z-Scores · Latest Day</div>"
        "</div>"
        "<table style='width:100%; border-collapse:collapse;'>"
        "<thead>"
        "<tr style='border-bottom:1px solid rgba(124,111,255,0.20);'>"
        "<th style='padding:6px 14px; font-size:0.65rem; color:#6A6A8A;"
        " text-transform:uppercase; letter-spacing:1.5px; text-align:left;"
        " font-weight:600;'>Signal</th>"
        "<th style='padding:6px 14px; font-size:0.65rem; color:#6A6A8A;"
        " text-transform:uppercase; letter-spacing:1.5px; text-align:right;"
        " font-weight:600;'>Z-Score</th>"
        "<th style='padding:6px 10px; font-size:0.65rem; color:#6A6A8A;"
        " text-transform:uppercase; letter-spacing:1.5px; text-align:center;"
        " font-weight:600;'>Flag</th>"
        "</tr>"
        "</thead>"
        "<tbody>" + rows_html + "</tbody>"
        "</table>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Error / warning helpers
# ─────────────────────────────────────────────────────────────────────────────

def render_error(message: str) -> None:
    html = (
        "<div style='"
        "background:rgba(224,90,90,.10); border:1px solid rgba(224,90,90,.45);"
        "border-radius:10px; padding:14px 18px; font-size:0.9rem;"
        "color:#FFFFFF; line-height:1.6; margin-top:12px;'>"
        "&#10060; &nbsp;" + message +
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def render_warning(message: str) -> None:
    html = (
        "<div style='"
        "background:rgba(240,192,64,.10); border:1px solid rgba(240,192,64,.40);"
        "border-radius:10px; padding:14px 18px; font-size:0.9rem;"
        "color:#FFFFFF; line-height:1.6; margin-top:12px;'>"
        "&#9888;&#65039; &nbsp;" + message +
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)
