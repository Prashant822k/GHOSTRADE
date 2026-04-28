"""
engine/signals.py  ·  GHOSTRADE Signal Engine
===============================================
Computes four microstructure signals from raw OHLCV data and
Z-score normalises each one.

3-month window stability notes (why this is better than 30 days):
  • VAI  uses rolling(20): first valid row at index 20 → 90d gives ~70 valid rows
  • VBS  uses ATR(14) then rolling_std(20) on top: first valid ~row 34
          → with 90d we get ~56 valid VBS rows vs ~1 with 30d
  • PVD  uses rolling corr(5): min_periods=3 means valid from row 3
  • LIP  is elementwise — valid from row 1

All Z-scores use the full available valid series as the reference distribution,
so the 90-day window gives a much more stable baseline σ.

Public interface:
    compute_signals(df: pd.DataFrame) -> pd.DataFrame

Adds columns: VAI_z, VBS_z, PVD_z, LIP_z
"""

import numpy as np
import pandas as pd
from scipy.stats import zscore as _scipy_zscore


# ── Public entry point ────────────────────────────────────────────────────

def compute_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute VAI, VBS, PVD, LIP and their Z-scores.
    Returns the input DataFrame extended with four new columns.
    """
    df = df.copy()
    df = _add_vai(df)
    df = _add_vbs(df)
    df = _add_pvd(df)
    df = _add_lip(df)
    return df


# ── Signal helpers ────────────────────────────────────────────────────────

def _safe_zscore(series: pd.Series) -> pd.Series:
    """
    Z-score a pandas Series, handling NaN values and constant series safely.

    Approach:
      1. Work only on the non-NaN subset.
      2. If std ≈ 0 (constant series), return zeros — not NaN — so downstream
         code never receives an unexpected NaN from a degenerate signal.
      3. Re-align back to the original index so the Series stays aligned with df.
    """
    result = pd.Series(np.nan, index=series.index, dtype=float)
    valid_mask = series.notna()
    vals = series[valid_mask].values.astype(float)

    if len(vals) < 3:
        return result  # too few points for meaningful Z-scoring

    std = np.nanstd(vals, ddof=1)
    if std < 1e-10:
        # Constant signal: every value is 0 σ from the mean
        result[valid_mask] = 0.0
        return result

    z = (vals - np.nanmean(vals)) / std
    result[valid_mask] = z
    return result


def _add_vai(df: pd.DataFrame) -> pd.DataFrame:
    """
    Volume Anomaly Index
    ────────────────────
    Raw   : VAI = Volume / rolling_mean(Volume, 20)
    Signal: VAI_z = zscore(VAI)

    Interpretation:
      High +VAI_z → volume spike far above 20-day baseline.
      If this occurs without a commensurate price move → manufactured activity.

    min_periods=10: ensures we get valid values even near the start of the
    series, avoiding an excessive NaN run-in.
    """
    rolling_mean_vol = df["Volume"].rolling(window=20, min_periods=10).mean()
    vai_raw = df["Volume"] / rolling_mean_vol          # ratio: 1.0 = baseline
    df["VAI_z"] = _safe_zscore(vai_raw)
    return df


def _add_vbs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Volatility Burst Score
    ──────────────────────
    Step 1 — True Range (Wilder):
        TR  = max(High-Low, |High-PrevClose|, |Low-PrevClose|)
    Step 2 — ATR(14):
        ATR = rolling_mean(TR, 14)
    Step 3 — Normalise by ATR's own rolling std:
        VBS = ATR / rolling_std(ATR, 20)
    Step 4 — Z-score:
        VBS_z = zscore(VBS)

    3-month stability fix:
        ddof=0 in rolling std avoids NaN on short early windows.
        min_periods=10 for both rolling windows keeps the effective
        run-in to ~23 rows instead of 34, giving more usable data.
    """
    high = df["High"]
    low  = df["Low"]
    prev_close = df["Close"].shift(1)

    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low  - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    atr14 = tr.rolling(window=14, min_periods=7).mean()

    # Rolling std of ATR — use ddof=0 (population std) to avoid NaN on
    # small windows; and min_periods=10 to start producing values sooner.
    atr_std = atr14.rolling(window=20, min_periods=10).std(ddof=0)
    atr_std = atr_std.replace(0.0, np.nan)   # guard against zero denominator

    vbs_raw  = atr14 / atr_std
    df["VBS_z"] = _safe_zscore(vbs_raw)
    return df


def _add_pvd(df: pd.DataFrame) -> pd.DataFrame:
    """
    Price-Volume Divergence
    ───────────────────────
    Raw   : PVD = 1 - rolling_corr(sign(ΔClose), sign(ΔVolume), 5)
    Signal: PVD_z = zscore(PVD)

    PVD ≈ 0  → price and volume move in lockstep (healthy)
    PVD ≈ 2  → perfect negative correlation (maximum divergence)

    min_periods=3: lets correlation start as early as day 3.
    A window of 5 and min_periods=3 is stable over 90 days with ~85 valid rows.
    """
    price_dir = np.sign(df["Close"].diff())
    vol_dir   = np.sign(df["Volume"].diff())

    rolling_corr = price_dir.rolling(window=5, min_periods=3).corr(vol_dir)
    pvd_raw = 1.0 - rolling_corr
    df["PVD_z"] = _safe_zscore(pvd_raw)
    return df


def _add_lip(df: pd.DataFrame) -> pd.DataFrame:
    """
    Liquidity Instability Proxy
    ───────────────────────────
    Raw   : LIP = (High - Low) / Close
    Signal: LIP_z = zscore(LIP)

    LIP measures intraday spread as a fraction of price.
    High LIP_z → unusually wide spread → thin or fragile liquidity.

    This is elementwise (no rolling window) so all 90 rows are valid from day 1.
    """
    lip_raw = (df["High"] - df["Low"]) / df["Close"]
    df["LIP_z"] = _safe_zscore(lip_raw)
    return df
