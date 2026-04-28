"""
engine/fetcher.py  ·  GHOSTRADE Data Layer
===========================================
Fetches ~3 months of OHLCV data via yfinance with a CSV cache fallback.

Why 3 months instead of 30 days (PRD intentional change):
  - More data means better rolling-window baselines (ATR std, VAI mean)
  - VAI uses a 20-day rolling mean: with 90 days we get ~70 fully-valid rows
  - VBS uses ATR(14) / rolling_std(20): needs ~34 rows for first valid point;
    with 90 days we have ~56 good rows instead of ~1–5
  - IsolationForest contamination=0.1 flags ~9 anomalous rows out of 90 vs ~3
    out of 30 — much more statistically robust

Public interface:
    fetch_ohlcv(ticker: str) -> pd.DataFrame

Returns a clean DataFrame with DatetimeIndex and columns:
    Open  High  Low  Close  Volume
"""

import pathlib
import yfinance as yf
import pandas as pd

# ── Cache directory relative to project root ──────────────────────────────
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
_CACHE_DIR = _PROJECT_ROOT / "data" / "cache"

# ── Fetch window ──────────────────────────────────────────────────────────
_FETCH_PERIOD = "3mo"          # ~63 trading days
_MIN_TRADING_DAYS = 40         # absolute minimum to produce meaningful signals
_REQUIRED_COLS = ["Open", "High", "Low", "Close", "Volume"]


def fetch_ohlcv(ticker: str) -> pd.DataFrame:
    """
    Fetch 3-month OHLCV data for *ticker* from yfinance.

    On success:
        • Writes a local CSV cache to data/cache/{TICKER}.csv
        • Returns a clean pd.DataFrame with DatetimeIndex

    On failure:
        • Network error → attempts to load the cached CSV
        • Invalid ticker / empty data → raises ValueError
        • Insufficient history (<40 rows) → raises ValueError

    Raises
    ------
    ValueError
        With a user-friendly message suitable for display in st.error / st.warning.
    """
    ticker = ticker.strip().upper()
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = _CACHE_DIR / f"{ticker}.csv"

    df = _download_from_yfinance(ticker)

    if df is None:
        # yfinance returned nothing — try cache before declaring failure
        df = _load_cache(cache_path)
        if df is None:
            raise ValueError(
                f"Ticker **'{ticker}'** not found. "
                "Please enter a valid stock symbol (e.g. AAPL, TSLA, SPY)."
            )

    df = _validate_and_clean(df, ticker)

    # Persist a fresh copy every successful live fetch
    try:
        df.to_csv(cache_path)
    except OSError:
        pass  # non-fatal; cache write failure must not crash the app

    return df


# ─────────────────────────────────────────────────────────────────────────────
# Private helpers
# ─────────────────────────────────────────────────────────────────────────────

def _download_from_yfinance(ticker: str) -> pd.DataFrame | None:
    """Attempt a live download; return None on any network/API failure."""
    try:
        raw = yf.download(
            ticker,
            period=_FETCH_PERIOD,
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=False,
        )
    except Exception:
        return None

    if raw is None or raw.empty:
        return None

    # yfinance ≥ 0.2.x sometimes returns a MultiIndex column on single-ticker
    # downloads.  Flatten it so we always get plain string column names.
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    # Keep only the columns we need
    missing = [c for c in _REQUIRED_COLS if c not in raw.columns]
    if missing:
        return None

    return raw[_REQUIRED_COLS].copy()


def _load_cache(cache_path: pathlib.Path) -> pd.DataFrame | None:
    """Load a previously cached CSV; return None if unavailable or corrupt."""
    if not cache_path.exists():
        return None
    try:
        df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        missing = [c for c in _REQUIRED_COLS if c not in df.columns]
        if missing:
            return None
        return df[_REQUIRED_COLS].copy()
    except Exception:
        return None


def _validate_and_clean(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """
    Drop NaN rows, enforce the minimum row count, and ensure the index is
    a proper DatetimeIndex sorted ascending.
    """
    df = df.dropna(subset=["Close", "Volume"])
    df = df.sort_index()

    if len(df) < _MIN_TRADING_DAYS:
        raise ValueError(
            f"Not enough trading history for **'{ticker}'** "
            f"({len(df)} days retrieved, {_MIN_TRADING_DAYS} required). "
            "Try a more liquid ticker like AAPL, SPY, or TSLA."
        )

    return df
