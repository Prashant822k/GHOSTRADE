"""
app.py  ·  GHOSTRADE Market Integrity Engine — Streamlit Entry Point
=====================================================================
Run:  python -m streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="GHOSTRADE · Market Integrity Engine",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from engine.fetcher  import fetch_ohlcv
from engine.signals  import compute_signals
from engine.anomaly  import run_anomaly_detection
from engine.scorer   import compute_trust_score

from ui.components import (
    inject_global_css,
    render_header,
    render_ticker_card,
    render_classification_badge,
    render_stats_row,
    render_explainer_card,
    render_signal_table,
    render_error,
    render_warning,
)
from ui.charts import (
    build_gauge,
    build_price_chart,
    build_volume_chart,
    build_signal_radar,
)

_TS   = "#6A6A8A"
_CARD = "#0D0D1F"


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline
# ─────────────────────────────────────────────────────────────────────────────

def run_pipeline(ticker: str) -> dict:
    df = fetch_ohlcv(ticker)
    df = compute_signals(df)
    df = run_anomaly_detection(df)
    return compute_trust_score(df)


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard renderer
# ─────────────────────────────────────────────────────────────────────────────

def render_dashboard(ticker: str, result: dict) -> None:
    df    = result["df"]
    color = result["color"]
    emoji = result["emoji"]
    label = result["label"]
    score = result["trust_score"]

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── Row 1: Ticker card  |  Gauge card ────────────────────────────────
    c_info, c_gauge = st.columns([1, 1], gap="large")

    with c_info:
        render_ticker_card(ticker, df)

    with c_gauge:
        # Badge header is its own self-contained markdown block
        render_classification_badge(label, color, emoji)
        # Gauge chart — separate Streamlit element, no wrapping HTML
        st.plotly_chart(
            build_gauge(score, color),
            use_container_width=True,
            config={"displayModeBar": False, "displaylogo": False},
        )

    st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

    # ── Row 2: Stats metrics ─────────────────────────────────────────────
    render_stats_row(result)

    st.markdown(
        "<hr style='border:none; border-top:1px solid rgba(124,111,255,0.15);"
        " margin:20px 0 16px;'>",
        unsafe_allow_html=True,
    )

    # ── Row 3: Price + Volume  |  Radar + Signal table ───────────────────
    c_charts, c_side = st.columns([2, 1], gap="large")

    with c_charts:
        st.plotly_chart(
            build_price_chart(df),
            use_container_width=True,
            config={
                "displayModeBar": True,
                "displaylogo": False,
                "modeBarButtonsToRemove": ["lasso2d", "select2d"],
            },
        )
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        st.plotly_chart(
            build_volume_chart(df),
            use_container_width=True,
            config={"displayModeBar": False, "displaylogo": False},
        )

    with c_side:
        st.plotly_chart(
            build_signal_radar(result),
            use_container_width=True,
            config={"displayModeBar": False, "displaylogo": False},
        )
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        render_signal_table(df)

    # ── Explainer card ───────────────────────────────────────────────────
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    render_explainer_card(result)


# ─────────────────────────────────────────────────────────────────────────────
# Error dispatch
# ─────────────────────────────────────────────────────────────────────────────

def _dispatch_error(ticker: str, exc: Exception) -> None:
    msg = str(exc).lower()
    if "not found" in msg or "valid stock" in msg:
        render_error(
            "Ticker <strong>'" + ticker + "'</strong> not found. "
            "Please enter a valid symbol — e.g. AAPL, GME, SPY."
        )
    elif "not enough" in msg or "required" in msg:
        render_warning(
            "Not enough trading history for <strong>'" + ticker + "'</strong>. "
            "Try a more liquid ticker like AAPL, SPY, or TSLA."
        )
    elif "unable to fetch" in msg or "connection" in msg:
        render_error(
            "Cannot reach market data. Check your internet connection — "
            "a cached result will be used if one exists."
        )
    else:
        render_error(str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    inject_global_css()
    render_header()

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # ── Input row ──────────────────────────────────────────────────────────
    inp_col, btn_col = st.columns([5, 1], gap="small")
    with inp_col:
        ticker_raw = st.text_input(
            label="Ticker",
            placeholder="Enter ticker:  AAPL   TSLA   GME   SPY …",
            label_visibility="collapsed",
            key="ticker_input",
        )
    with btn_col:
        clicked = st.button("🔍  Analyze", use_container_width=True, type="primary")

    # Demo chip strip
    chips_html = (
        "<div style='display:flex; align-items:center; gap:8px;"
        " margin-top:8px; flex-wrap:wrap;'>"
        "<span style='color:#6A6A8A; font-size:0.75rem; letter-spacing:.5px;'>Try:</span>"
        "<span class='chip chip-teal'>AAPL</span>"
        "<span class='chip chip-red'>GME</span>"
        "<span class='chip chip-gold'>TSLA</span>"
        "<span class='chip chip-purple'>SPY</span>"
        "<span class='chip chip-gold'>AMC</span>"
        "</div>"
    )
    st.markdown(chips_html, unsafe_allow_html=True)

    # ── Trigger: button OR new ticker ────────────────────────────────────
    ticker = ticker_raw.strip().upper() if ticker_raw else ""
    prev   = st.session_state.get("_last", "")

    if ticker and (clicked or ticker != prev):
        st.session_state["_last"] = ticker
        with st.spinner("Analyzing " + ticker + " …"):
            try:
                result = run_pipeline(ticker)
                render_dashboard(ticker, result)
            except ValueError as exc:
                _dispatch_error(ticker, exc)
            except Exception as exc:
                render_error("Unexpected error: " + type(exc).__name__ + " — " + str(exc))
    elif not ticker:
        st.session_state.pop("_last", None)

    # ── Footer ─────────────────────────────────────────────────────────────
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    footer_html = (
        "<div style='text-align:center; color:#6A6A8A; font-size:0.72rem; letter-spacing:1px;'>"
        "GHOSTRADE &nbsp;&middot;&nbsp; Market Integrity Engine &nbsp;&middot;&nbsp;"
        " v2.0 &nbsp;&middot;&nbsp; Team O(4)"
        "<br><span style='font-size:0.68rem; font-style:italic;'>"
        "The market can lie. Now you'll know when it does. 👻"
        "</span></div>"
    )
    st.markdown(footer_html, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
