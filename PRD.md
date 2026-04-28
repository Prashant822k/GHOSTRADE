# GHOSTRADE  
## Market Integrity Engine  
### Product Requirements Document (PRD) · v2.0 · Team O(4)

---

## 1. Overview

GHOSTRADE is a real-time market integrity engine that audits market behavior rather than predicting price. Given any stock ticker, it fetches 30 days of OHLCV data, computes four statistical microstructure signals, runs an unsupervised ML anomaly detection model, and outputs a Trust Score from 0 to 100 — classifying the market move as Stable, Suspicious, or Ghost Trade.

The system is designed for retail traders who want a fast, explainable signal integrity check before acting on a technical setup, and for any evaluator who wants to understand whether a price move is statistically real or manufactured.

---

## 2. Problem Statement

Retail traders are routinely trapped by market moves that appear technically valid but are structurally manufactured — fake breakouts, wash trading, liquidity sweeps, and coordinated pump activity. Existing free tools offer price prediction and chart overlays, but none provide a signal integrity layer.

### Core Gap

There is no lightweight, free, real-time tool that answers the fundamental question:

> "Is this price move statistically real — or is it manufactured?"

### Observable Symptoms

- Volume spikes occur without any corroborating price movement
- Breakouts form and immediately reverse, trapping long and short entries
- Volatility surges beyond historical norms with no identifiable news catalyst
- No free tool provides explainable anomaly detection on standard OHLCV data

---

## 3. Goals & Non-Goals

### In Scope

- Accept any valid stock ticker as user input
- Fetch 30-day OHLCV data via yfinance (free, no API key required)
- Compute four microstructure signals: VAI, VBS, PVD, LIP with Z-score normalization
- Run Isolation Forest anomaly detection combined with Z-score analysis
- Output a Trust Score (0–100) and a three-class classification label
- Render a polished Streamlit dashboard with interactive charts and plain-English explainability

### Out of Scope

- Price prediction or directional buy/sell signals
- Order book or Level 2 data (no paid APIs)
- User authentication or persistent multi-session storage
- Mobile application or browser extension (see Stretch Goals)
- Multi-ticker portfolio view — single ticker per session in v1

---

## 4. User Personas

### Retail Trader

Trades equities or ETFs. Follows technical setups. Has been burned by false breakouts. Wants a quick integrity check before entering a position.

**Needs:**
- One-click ticker lookup
- Clear green/yellow/red verdict
- Plain-English explanation, not math

### Hackathon / Technical Evaluator

Evaluating novelty, technical depth, and polish. Wants to see real data, an ML component, and a clean UI in one cohesive product.

**Needs:**
- Working demo with any real ticker
- Visible ML / statistical signal
- Explainable output, not a black box

---

## 5. Core Signals — Engineering Specification

All four signals are computed from raw OHLCV data. Each is Z-score normalized against the ticker's 30-day baseline before being fed into the scoring engine.

| Signal Name | Abbr. | Formula / Logic | Flags |
|---|---:|---|---|
| Volume Anomaly Index | VAI | Current volume / 20-day rolling avg volume. Z-scored against ticker baseline. | Volume spike without price support |
| Volatility Burst Score | VBS | ATR(14) / rolling ATR std dev. Measures instability beyond historical norm. | Sudden volatility with no news catalyst |
| Price-Volume Divergence | PVD | Correlation between price direction and volume direction over a 5-day window. | Price moves without volume conviction |
| Liquidity Instability Proxy | LIP | Spread proxy: (High − Low) / Close, Z-scored. High LIP = fragile market structure. | Potential manipulation or thin book |

### Anomaly Detection Pipeline

- Step 1 — Z-score each signal against its 30-day ticker baseline
- Step 2 — Feed all four Z-scores as a feature vector into Isolation Forest (contamination = 0.1)
- Step 3 — Combine the Isolation Forest anomaly score with Z-score magnitudes into the final Trust Score (0–100)
- Step 4 — Classify: 70–100 = Stable | 30–69 = Suspicious | 0–29 = Ghost Trade

---

## 6. Trust Score & Classification

The Trust Score is a normalized 0–100 value that represents the statistical integrity of the most recent market behavior for a given ticker. Lower scores indicate a higher probability of manufactured or anomalous market activity.

| Score Range | Label | Meaning |
|---|---|---|
| 70 – 100 | ✅ Stable | Move is statistically consistent with historical behavior. Low manipulation probability. |
| 30 – 69 | ⚠️ Suspicious | One or more signals show abnormal patterns. Caution warranted before acting on this move. |
| 0 – 29 | 👻 Ghost Trade | Multiple signals confirm structural anomaly. High probability of manufactured or manipulated move. |

The classification label and its color must be consistent throughout the UI: teal for Stable, gold for Suspicious, and red for Ghost Trade.

---

## 7. Feature List & Priorities

| Feature | Description | Priority |
|---|---|---|
| Ticker Input & Validation | Text input field that accepts any stock ticker. Validates format before executing the pipeline. Returns clear error on invalid or unknown tickers. | P0 |
| OHLCV Data Fetch | Fetches 30-day Open/High/Low/Close/Volume data via yfinance. Handles missing data, stale data, and insufficient history gracefully. Falls back to cached CSV if API is unavailable. | P0 |
| Signal Engine | Computes VAI, VBS, PVD, and LIP signals from raw OHLCV data. Applies Z-score normalization against the ticker's 30-day baseline before scoring. | P0 |
| Anomaly Detection (ML) | Fits an Isolation Forest model (scikit-learn) on 30 days of Z-scored signal data per ticker. Extracts anomaly scores per data point. | P0 |
| Trust Score Engine | Combines Isolation Forest anomaly score with Z-score magnitudes into a final normalized 0–100 Trust Score. Applies classification label (Stable / Suspicious / Ghost Trade). | P0 |
| 30-Day Price Chart | Interactive line chart of closing price with anomalous periods visually highlighted (e.g., red bands or markers on flagged dates). | P0 |
| Volume Bar Chart | Bar chart of daily volume. Anomalous volume days rendered in red; normal days in blue. | P0 |
| Trust Score Ring / Gauge | Circular Plotly gauge displaying the computed Trust Score numerically and by color (teal / gold / red based on classification). | P0 |
| Anomaly Explainer Card | Plain-English card that describes what was flagged and why. Must reference actual computed sigma values (e.g., 'Volume was 3.2σ above its 20-day baseline'). | P0 |
| Stats Row | Three summary metrics displayed prominently: Volume Spike %, 30-Day Price Delta, and Active Signal Count. | P1 |
| Dark Theme UI | Full dark-theme Streamlit dashboard matching the defined color palette. Background #06060F, card surfaces #0D0D1F, purple/gold/teal accents. | P1 |
| Error Handling | Clean, user-friendly messages for: invalid ticker, network failure, insufficient data history. Application must not crash on any expected error. | P1 |
| Loading State | Visual loading indicator during data fetch and ML computation. Prevents user from re-submitting during analysis. | P2 |
| Historical Mode | Optional date range picker that allows non-real-time analysis of a past 30-day window for any supported ticker. | P2 |

---

## 8. UX & Design Specification

The UI is a single-page Streamlit dashboard with a dark theme. The following defines the authoritative layout structure and color palette.

### Color Palette

| Role | Hex | Usage |
|---|---|---|
| Background | #06060F | Near-black canvas |
| Card Background | #0D0D1F | Slightly elevated surface |
| Primary Accent | #7C6FFF | Purple — borders, ticker badge, chart line |
| Trust Score / Warning | #F0C040 | Gold — Trust Score ring and Suspicious label |
| Danger | #E05A5A | Red — Ghost Trade, anomalous volume bars |
| Positive | #5DCAA5 | Teal — Stable label and signal count |
| Text Primary | #FFFFFF | Headings and key values |
| Text Secondary | #6A6A8A | Descriptions and secondary labels |

### Layout Structure (Top to Bottom)

- Header Bar — GHOSTRADE logotype (purple accent on 'TRADE'), LIVE indicator dot, product subtitle
- Row 1 (2 columns) — Ticker badge card (left) | Trust Score ring / gauge card (right)
- Row 2 (3 columns) — Vol Spike % stat | 30-Day Price Delta stat | Active Signal Count stat
- Price & Volume Chart Card — 30-day price line chart stacked above volume bar chart
- Anomaly Insight Card — Gold border, star icon, plain-English explanation with actual sigma values

### Key UX Rules

- Never show raw numbers without context — always pair a value with its label and unit
- Anomalous volume bars must be visually distinct (red) from normal bars (blue) — never use only opacity
- The Trust Score ring must reflect the actual computed score; hardcoded demo values are not acceptable
- The classification label color must match its score bracket at all times: gold for Suspicious, red for Ghost Trade, teal for Stable
- Explainer text must reference actual computed values (e.g., 'Volume was 3.2σ above its 20-day baseline')
- All chart interactions must be enabled (hover tooltips, zoom, pan via Plotly's built-in controls)

---

## 9. Tech Stack

| Component | Tool / Library |
|---|---|
| Language | Python 3.10+ |
| Data Fetching | yfinance — free, no API key required |
| Data Processing | pandas, NumPy — rolling statistics, signal computation, Z-scoring |
| Machine Learning | scikit-learn — IsolationForest for anomaly scoring |
| Dashboard UI | Streamlit — layout, widgets, theming via config.toml |
| Charts | Plotly (via st.plotly_chart) — price line, volume bars, Trust Score gauge |
| Styling | .streamlit/config.toml — primaryColor, backgroundColor, secondaryBackgroundColor |
| Environment | Python venv with pinned requirements.txt |

### File Structure

    ghostrade/
      app.py                   # Streamlit entry point
      engine/
        fetcher.py             # yfinance data fetch + validation
        signals.py             # VAI, VBS, PVD, LIP computation
        anomaly.py             # IsolationForest + Z-score pipeline
        scorer.py              # Trust Score 0–100 + classification
      ui/
        components.py          # Reusable Streamlit UI components
        charts.py              # Plotly chart builders
      data/
        cache/                 # Pre-cached OHLCV CSVs (offline fallback)
      .streamlit/
        config.toml            # Dark theme configuration
      requirements.txt
      README.md

---

## 10. Acceptance Criteria

All of the following must be true for the product to be considered ready for demonstration or release.

### Functional

- Entering AAPL, GME, TSLA, or SPY returns a Trust Score and classification within 10 seconds
- An invalid ticker (e.g. 'FAKEXYZ') shows a clean error message and does not crash the application
- The Trust Score ring reflects the actual computed score — not a hardcoded value
- Volume bars are red for statistically anomalous periods and blue otherwise
- The Anomaly Explainer card contains actual sigma values from the computation (e.g. '3.2σ above baseline')

### Visual

- Dashboard background is dark (#06060F or visually equivalent)
- Card surfaces are elevated (#0D0D1F) with purple/gold accents applied correctly
- Classification label color matches score bracket: teal for Stable, gold for Suspicious, red for Ghost Trade
- Dashboard is polished enough to screenshot for a presentation slide deck

---

## 11. Risk Register

| Risk | Likelihood / Impact | Mitigation |
|---|---|---|
| yfinance rate limit or downtime | Medium / High | Pre-cache OHLCV CSVs for primary demo tickers. Implement automatic fallback to cached CSV on API failure. |
| Streamlit dark theme incomplete | Low / Medium | Use st.markdown() with inline CSS for component-level overrides. Match config.toml exactly to the defined palette. |
| Isolation Forest overfits thin data | Medium / Low | Set contamination=0.1 and enforce a minimum of 20 days of data. Fall back to Z-score as primary signal if IF cannot train. |
| Plotly gauge styling mismatch | Low / Low | Keep gauge simple. Use st.metric() as a visual fallback if Plotly customization proves time-prohibitive. |

---

## 12. Stretch Goals (Post v1)

The following features are explicitly deferred from v1 but represent the natural product evolution roadmap:

- Multi-ticker watchlist with batch Trust Score computation
- Historical backtesting — retroactively flag known manipulation events (e.g. GME Jan 2021)
- Browser extension for real-time Trust Score overlay on TradingView
- REST API endpoint so third-party apps can query Trust Scores programmatically
- Alert system — email or Telegram notification when a watched ticker crosses into Ghost Trade territory
- Portfolio-level integrity view aggregating scores across multiple holdings

---

The market can lie. Now you'll know when it does. 👻

GHOSTRADE  ·  PRD v2.0  ·  Team O(4)