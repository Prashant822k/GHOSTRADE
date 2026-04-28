"""
engine/scorer.py  ·  GHOSTRADE Trust Score Engine
==================================================
Converts IsolationForest anomaly scores + Z-score magnitudes into a
single normalised Trust Score (0–100) and applies classification.

Trust Score formula
───────────────────
    z_mag        = mean(|VAI_z|, |VBS_z|, |PVD_z|, |LIP_z|)  ← latest valid row
    if_score     = anomaly_score                                ← higher = worse
    raw_penalty  = (if_score × 0.6) + (z_mag × 0.4)
    trust_score  = clamp(100 − raw_penalty × 20,  0, 100)

Weights: IsolationForest majority (60%) + Z-magnitude anchor (40%).
Scale factor ×20 maps the expected penalty range [0 ~ 5] → [0 ~ 100] inverted.

Classification
──────────────
    70 – 100  →  Stable      ✅  #5DCAA5 teal
    30 –  69  →  Suspicious  ⚠️  #F0C040 gold
     0 –  29  →  Ghost Trade 👻  #E05A5A red

Public interface:
    compute_trust_score(df: pd.DataFrame) -> dict
"""

import numpy as np
import pandas as pd

FEATURE_COLS = ["VAI_z", "VBS_z", "PVD_z", "LIP_z"]

_SIGNAL_LABELS = {
    "VAI_z": "Volume Anomaly Index",
    "VBS_z": "Volatility Burst Score",
    "PVD_z": "Price-Volume Divergence",
    "LIP_z": "Liquidity Instability Proxy",
}

# Formula constants
_IF_WEIGHT    = 0.60
_Z_WEIGHT     = 0.40
_SCALE        = 20.0    # maps raw penalty → 0–100 range after inversion

# Classification thresholds
_STABLE_MIN   = 70
_SUSPIC_MIN   = 30


def compute_trust_score(df: pd.DataFrame) -> dict:
    """
    Compute the Trust Score and all ancillary metrics for the UI.

    Parameters
    ----------
    df : pd.DataFrame
        Enriched DataFrame from run_anomaly_detection().

    Returns
    -------
    dict with keys:
        trust_score      float  0–100
        label            str    'Stable' | 'Suspicious' | 'Ghost Trade'
        color            str    hex color matching the classification
        emoji            str    visual badge
        active_signals   int    count of signals where |z| > 2.0 on latest row
        volume_spike_pct float  (Volume[-1] / 20d rolling mean − 1) × 100
        price_delta_3mo  float  percent change from first to last Close
        top_flag         str    human-readable name of the most extreme signal
        top_flag_sigma   float  that signal's z-value (signed)
        df               pd.DataFrame  pass-through for charting
    """
    # ── Find the most-recent row that has all four signal columns ──────────
    df_valid = df.dropna(subset=FEATURE_COLS + ["anomaly_score"])

    if df_valid.empty:
        # Extreme edge-case: nothing to score → return a neutral result
        return _neutral_result(df)

    latest = df_valid.iloc[-1]

    # ── Core Trust Score ───────────────────────────────────────────────────
    z_values  = {c: float(latest[c]) for c in FEATURE_COLS}
    z_mag     = float(np.mean([abs(v) for v in z_values.values()]))
    if_score  = float(latest["anomaly_score"])

    raw_penalty  = (if_score * _IF_WEIGHT) + (z_mag * _Z_WEIGHT)
    trust_score  = float(np.clip(100.0 - raw_penalty * _SCALE, 0.0, 100.0))
    trust_score  = round(trust_score, 1)

    label, color, emoji = _classify(trust_score)

    # ── Active signals: count |z| > 2.0 on the latest row ─────────────────
    active_signals = sum(1 for v in z_values.values() if abs(v) > 2.0)

    # ── Top flag: signal with the largest absolute Z-score ─────────────────
    top_col        = max(z_values, key=lambda c: abs(z_values[c]))
    top_flag       = _SIGNAL_LABELS.get(top_col, top_col)
    top_flag_sigma = round(z_values[top_col], 2)

    # ── Volume Spike % — actual volume ratio, not z-score ─────────────────
    try:
        vol_mean_20  = df["Volume"].rolling(20, min_periods=10).mean().iloc[-1]
        vol_latest   = float(df["Volume"].iloc[-1])
        volume_spike_pct = round(((vol_latest / vol_mean_20) - 1.0) * 100.0, 1)
    except Exception:
        volume_spike_pct = round(float(latest.get("VAI_z", 0.0)) * 100.0, 1)

    # ── 3-Month Price Δ ────────────────────────────────────────────────────
    try:
        close_series  = df["Close"].dropna()
        price_delta   = ((float(close_series.iloc[-1]) - float(close_series.iloc[0]))
                         / float(close_series.iloc[0])) * 100.0
        price_delta   = round(price_delta, 2)
    except Exception:
        price_delta = 0.0

    return {
        "trust_score":      trust_score,
        "label":            label,
        "color":            color,
        "emoji":            emoji,
        "active_signals":   active_signals,
        "volume_spike_pct": volume_spike_pct,
        "price_delta_3mo":  price_delta,
        "top_flag":         top_flag,
        "top_flag_sigma":   top_flag_sigma,
        "df":               df,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Private helpers
# ─────────────────────────────────────────────────────────────────────────────

def _classify(score: float) -> tuple[str, str, str]:
    if score >= _STABLE_MIN:
        return "Stable", "#5DCAA5", "✅"
    elif score >= _SUSPIC_MIN:
        return "Suspicious", "#F0C040", "⚠️"
    else:
        return "Ghost Trade", "#E05A5A", "👻"


def _neutral_result(df: pd.DataFrame) -> dict:
    """Return a 50/Suspicious result when no valid rows exist."""
    return {
        "trust_score":      50.0,
        "label":            "Suspicious",
        "color":            "#F0C040",
        "emoji":            "⚠️",
        "active_signals":   0,
        "volume_spike_pct": 0.0,
        "price_delta_3mo":  0.0,
        "top_flag":         "Unknown",
        "top_flag_sigma":   0.0,
        "df":               df,
    }
