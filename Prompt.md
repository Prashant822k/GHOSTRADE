# GHOSTRADE — AI IDE Build Prompt
## Market Integrity Engine · v2.0 · Team O(4)

---

## 🧠 What You Are Building

You are building **GHOSTRADE**, a real-time market integrity engine. It does **not** predict price direction. It audits whether a price move is statistically real or structurally manufactured — outputting a **Trust Score (0–100)** and a plain-English explanation.

This is a **Streamlit + Python** application. Every feature below must be built, tested, and wired end-to-end into the UI before you move on.

---

## 📁 Project Structure to Scaffold First

```
ghostrade/
  app.py                   # Streamlit entry point — wire everything here
  engine/
    fetcher.py             # yfinance data fetch + CSV fallback
    signals.py             # VAI, VBS, PVD, LIP computation
    anomaly.py             # IsolationForest + Z-score pipeline
    scorer.py              # Trust Score 0–100 + classification label
  ui/
    components.py          # Reusable Streamlit layout components
    charts.py              # Plotly chart builders
  data/
    cache/                 # Pre-cached OHLCV CSVs (offline fallback)
  .streamlit/
    config.toml            # Dark theme
  requirements.txt
  README.md
```

---

## ⚙️ Tech Stack (Exact Libraries)

| Layer | Library |
|---|---|
| Language | Python 3.10+ |
| Data | `yfinance` |
| Processing | `pandas`, `numpy` |
| ML | `scikit-learn` (IsolationForest) |
| UI | `streamlit` |
| Charts | `plotly` (via `st.plotly_chart`) |
| DB (optional) | `supabase-py` |

**requirements.txt:**
```
yfinance
pandas
numpy
scikit-learn
streamlit
plotly
supabase
```

---

## 🔢 Step 1 — Data Layer (`engine/fetcher.py`)

- Use `yfinance` to fetch **30 days of OHLCV data** for any ticker
- Required fields: `Open`, `High`, `Low`, `Close`, `Volume`
- Handle these failure cases gracefully (return informative errors, do NOT crash):
  - Invalid ticker (no data returned)
  - Fewer than 20 rows of history (insufficient for Z-scoring)
  - Network failure → fall back to `data/cache/{TICKER}.csv` if it exists
- On every successful fetch, save a CSV copy to `data/cache/{TICKER}.csv`
- Return a clean `pd.DataFrame` with a `DatetimeIndex`

```python
# fetcher.py interface
def fetch_ohlcv(ticker: str) -> pd.DataFrame:
    """Returns 30-day OHLCV DataFrame or raises a descriptive ValueError."""
```

---

## 📊 Step 2 — Signal Engine (`engine/signals.py`)

Compute all four signals from the raw OHLCV DataFrame. Each signal must be returned as a new column added to the DataFrame.

### VAI — Volume Anomaly Index
```
VAI = Volume / rolling_mean(Volume, 20)
VAI_z = zscore(VAI)
```
> Flags: Volume spike without price movement support.

### VBS — Volatility Burst Score
```
ATR_14 = average_true_range(High, Low, Close, 14)
VBS = ATR_14 / rolling_std(ATR_14, 20)
VBS_z = zscore(VBS)
```
> Flags: Sudden volatility beyond historical norm.

### PVD — Price-Volume Divergence
```
price_direction = sign(Close.diff())
volume_direction = sign(Volume.diff())
PVD = 1 - rolling_correlation(price_direction, volume_direction, 5)
PVD_z = zscore(PVD)
```
> Flags: Price moves without volume conviction.

### LIP — Liquidity Instability Proxy
```
LIP = (High - Low) / Close
LIP_z = zscore(LIP)
```
> Flags: Thin book or fragile market structure.

**Return:** The original DataFrame with columns `VAI_z`, `VBS_z`, `PVD_z`, `LIP_z` appended.

```python
# signals.py interface
def compute_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Adds VAI_z, VBS_z, PVD_z, LIP_z columns. Returns enriched DataFrame."""
```

---

## 🤖 Step 3 — Anomaly Detection (`engine/anomaly.py`)

- Drop rows with NaN (from rolling calculations) before training
- Feature matrix: `X = df[["VAI_z", "VBS_z", "PVD_z", "LIP_z"]]`
- Fit `IsolationForest(contamination=0.1, random_state=42)` on X
- Extract `anomaly_score = -model.decision_function(X)` (higher = more anomalous)
- Label each row: `is_anomaly = model.predict(X) == -1`
- Return enriched DataFrame with `anomaly_score` and `is_anomaly` columns

```python
# anomaly.py interface
def run_anomaly_detection(df: pd.DataFrame) -> pd.DataFrame:
    """Fits IF, adds anomaly_score and is_anomaly columns. Returns enriched DataFrame."""
```

---

## 🎯 Step 4 — Trust Score Engine (`engine/scorer.py`)

Combine the Isolation Forest anomaly score with Z-score magnitudes into a single **Trust Score (0–100)**.

**Scoring formula (example — tune as needed):**
```python
z_magnitude = df[["VAI_z", "VBS_z", "PVD_z", "LIP_z"]].abs().mean(axis=1).iloc[-1]
anomaly = df["anomaly_score"].iloc[-1]

raw = (anomaly * 0.6) + (z_magnitude * 0.4)
trust_score = max(0, min(100, 100 - (raw * 20)))
```

**Classification:**
| Trust Score | Label | Color |
|---|---|---|
| 70–100 | ✅ Stable | `#5DCAA5` (teal) |
| 30–69 | ⚠️ Suspicious | `#F0C040` (gold) |
| 0–29 | 👻 Ghost Trade | `#E05A5A` (red) |

**Also compute and return:**
- `active_signals`: count of signals where `|z| > 2.0` on the latest row
- `volume_spike_pct`: `(VAI_z_latest / 1.0) * 100` (approximate)
- `price_delta_30d`: `((Close[-1] - Close[0]) / Close[0]) * 100`
- `top_flag`: the signal with the highest Z-score on the latest row — used in explainer text

```python
# scorer.py interface
def compute_trust_score(df: pd.DataFrame) -> dict:
    """Returns dict: trust_score, label, color, active_signals, volume_spike_pct,
       price_delta_30d, top_flag, top_flag_sigma"""
```

---

## 🖥️ Step 5 — Streamlit UI (`app.py` + `ui/`)

### `.streamlit/config.toml`
```toml
[theme]
base = "dark"
primaryColor = "#7C6FFF"
backgroundColor = "#06060F"
secondaryBackgroundColor = "#0D0D1F"
textColor = "#FFFFFF"
font = "sans serif"
```

### Layout (top to bottom)

**1. Header**
```python
st.markdown("""
  <div style='text-align:center; font-size:2.5rem; font-weight:900; letter-spacing:2px;'>
    GHOST<span style='color:#7C6FFF'>TRADE</span>
  </div>
  <div style='text-align:center; color:#6A6A8A; font-size:0.9rem;'>
    Market Integrity Engine · Real-Time Audit
  </div>
""", unsafe_allow_html=True)
```

**2. Ticker Input**
```python
ticker = st.text_input("Enter Ticker", placeholder="AAPL, TSLA, GME, SPY...")
if ticker:
    with st.spinner("Fetching data and running analysis..."):
        # run full pipeline
```

**3. Row 1 — Ticker Info + Trust Score Ring (2 columns)**
- Left: ticker name, exchange, last close price, data freshness indicator
- Right: Plotly circular gauge (`indicator` mode) showing Trust Score
  - Dial color = classification color (teal/gold/red)
  - Display score numerically in the center

```python
# Gauge example
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=trust_score,
    gauge={"axis": {"range": [0, 100]},
           "bar": {"color": color},
           "bgcolor": "#0D0D1F"},
    number={"font": {"color": color, "size": 48}},
))
```

**4. Row 2 — Stats Row (3 columns)**
```python
col1, col2, col3 = st.columns(3)
col1.metric("Vol Spike", f"{volume_spike_pct:+.1f}%")
col2.metric("30D Price Δ", f"{price_delta_30d:+.1f}%")
col3.metric("Active Signals", f"{active_signals}/4")
```

**5. Price Chart (30D Line + Anomaly Highlights)**
- Line chart of `Close` price over 30 days
- Overlay red vertical shading or red markers on dates where `is_anomaly == True`
- Use Plotly, not `st.line_chart`

**6. Volume Bar Chart**
- Bar chart of daily `Volume`
- Bars where `is_anomaly == True` → `#E05A5A` (red)
- All other bars → `#7C6FFF` (purple/blue)

**7. Anomaly Explainer Card**
```python
st.markdown(f"""
<div style='border: 1px solid #F0C040; border-radius: 8px; padding: 20px; background: #0D0D1F;'>
  ⭐ <strong>Anomaly Insight</strong><br><br>
  The <strong>{top_flag}</strong> signal reached <strong>{top_flag_sigma:.1f}σ</strong>
  above its 30-day baseline. Trust Score of <strong>{trust_score}</strong> indicates
  this move is classified as <span style='color:{color}'><strong>{label}</strong></span>.
  {f"Volume spiked {volume_spike_pct:.0f}% above normal." if volume_spike_pct > 50 else ""}
</div>
""", unsafe_allow_html=True)
```

---

## 🛡️ Step 6 — Error Handling Requirements

Every failure must show a helpful, styled error — never a raw Python traceback:

| Failure | Expected Behavior |
|---|---|
| Invalid ticker | `st.error("Ticker 'XYZ' not found. Please enter a valid stock symbol.")` |
| Insufficient data (< 20 rows) | `st.warning("Not enough history for {ticker}. Try a more liquid ticker.")` |
| Network failure + no cache | `st.error("Unable to fetch data. Check your connection and try again.")` |
| Any uncaught exception | Wrap main pipeline in `try/except`, display `st.error(str(e))` |

---

## 🗄️ Step 7 — Supabase Integration (Optional / P2)

If a Supabase project is available, log every Trust Score result:

**Table Schema:**
```sql
CREATE TABLE audit_log (
  id SERIAL PRIMARY KEY,
  ticker TEXT NOT NULL,
  trust_score FLOAT NOT NULL,
  label TEXT NOT NULL,
  active_signals INTEGER,
  created_at TIMESTAMP DEFAULT now()
);
```

**Python:**
```python
from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase.table("audit_log").insert({
    "ticker": ticker,
    "trust_score": result["trust_score"],
    "label": result["label"],
    "active_signals": result["active_signals"]
}).execute()
```

Load credentials from environment variables — never hardcode.

---

## ✅ Acceptance Checklist (Must Pass Before Done)

### Functional
- [ ] AAPL, GME, TSLA, SPY all return a score + label within 10 seconds
- [ ] `FAKEXYZ` shows a clean error and does not crash
- [ ] Trust Score ring reflects the actual computed score (not hardcoded)
- [ ] Red volume bars appear on anomalous dates only
- [ ] Explainer card shows actual sigma values from the latest row

### Visual
- [ ] Background is `#06060F` (not Streamlit default white)
- [ ] Cards use `#0D0D1F` with purple/gold/teal accents applied correctly
- [ ] Classification label color matches bracket: teal / gold / red
- [ ] Dashboard looks polished enough to screenshot for a deck

---

## 🚀 Deployment

**Local:**
```bash
pip install -r requirements.txt
streamlit run app.py
```

**Streamlit Cloud (recommended for sharing):**
- Push repo to GitHub
- Connect at share.streamlit.io
- Set environment variables (Supabase keys) in Streamlit Cloud secrets

**Backup (ngrok):**
```bash
ngrok http 8501
```

---

## 📋 Demo Tickers & Talking Points

| Ticker | Why It's Interesting |
|---|---|
| **GME** (Jan 2021 period) | Classic coordinated pump — multiple signals should fire simultaneously |
| **AMC** | Similar manipulation pattern, slightly different volume structure |
| **AAPL** | Large cap baseline — should score Stable (70+) in normal periods |
| **SPY** | Index ETF — very stable, good contrast to GME/AMC |
| **TSLA** | High volatility but usually real moves — interesting edge case |

---

> *The market can lie. Now you'll know when it does. 👻*
> **GHOSTRADE · v2.0 · Team O(4)**