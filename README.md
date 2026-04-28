# GHOSTRADE · Market Integrity Engine

> *The market can lie. Now you'll know when it does. 👻*

Real-time anomaly detection for stock market behavior.  
Input any ticker → get a **Trust Score (0–100)** + classification in seconds.

---

## Quick Start

```powershell
# 1. Clone
git clone https://github.com/Prashant822k/GHOSTRADE.git
cd GHOSTRADE

# 2. Virtual environment
python -m venv venv
.\venv\Scripts\activate

# 3. Install
pip install -r requirements.txt

# 4. Run
streamlit run app.py
```

Open http://localhost:8501

---

## How It Works

| Step | Module | Description |
|---|---|---|
| Fetch | `engine/fetcher.py` | 3-month OHLCV from yfinance + CSV fallback |
| Signals | `engine/signals.py` | VAI, VBS, PVD, LIP — Z-score normalised |
| Anomaly | `engine/anomaly.py` | IsolationForest (contamination=0.1), dynamic per-ticker |
| Score | `engine/scorer.py` | Trust Score 0–100, classification label |
| UI | `app.py` + `ui/` | Streamlit dark dashboard + Plotly charts |

## Classification

| Score | Label | Meaning |
|---|---|---|
| 70–100 | ✅ Stable | Move is statistically consistent |
| 30–69 | ⚠️ Suspicious | One or more signals abnormal |
| 0–29 | 👻 Ghost Trade | Multiple signals confirm manufactured activity |

## Demo Tickers

`AAPL` · `GME` · `TSLA` · `SPY` · `AMC`

---

GHOSTRADE · PRD v2.0 · Team O(4)
