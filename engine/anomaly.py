"""
engine/anomaly.py  ·  GHOSTRADE Anomaly Detection
==================================================
Fits an IsolationForest on the current ticker's 3-month signal window
and annotates each row with an anomaly score and a boolean flag.

Design decision — dynamic per-ticker training (no model persistence):
  • IsolationForest is an unsupervised density estimator. "Anomalous" means
    "far from this ticker's own distribution." A model trained on AAPL has
    zero valid definition of normal for GME.
  • 90 rows × 4 features = 360 floats. sklearn fit+predict: ~40ms on any CPU.
    There is no latency justification for caching the model.
  • A saved .pkl becomes stale by the next trading day. Dynamic retraining
    is the only correct approach here.

Fallback:
  • If fewer than MIN_ROWS_FOR_IF rows remain after dropping NaN, the IF
    cannot flag ~9 anomalies at contamination=0.1.  In that case we use
    Z-score magnitude as the anomaly proxy (pure Z-score path).

Public interface:
    run_anomaly_detection(df: pd.DataFrame) -> pd.DataFrame

Adds columns: anomaly_score  (float, higher = more anomalous)
              is_anomaly      (bool)
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

FEATURE_COLS    = ["VAI_z", "VBS_z", "PVD_z", "LIP_z"]
CONTAMINATION   = 0.1
RANDOM_STATE    = 42
N_ESTIMATORS    = 150          # slightly more trees → smoother score surface
MIN_ROWS_FOR_IF = 20           # need at least 20 clean rows for IF to be meaningful


def run_anomaly_detection(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fit IsolationForest on *df*'s Z-scored signal columns.

    Returns the same DataFrame with two new columns appended:
        anomaly_score : float  — higher value = more anomalous
        is_anomaly    : bool   — True for the top-10% most anomalous rows
    """
    df = df.copy()

    # Safe defaults (rows that stay NaN in signals get score=0, flag=False)
    df["anomaly_score"] = 0.0
    df["is_anomaly"]    = False

    # Select only rows where all four signal columns are finite
    valid_mask = df[FEATURE_COLS].notna().all(axis=1)
    df_clean   = df.loc[valid_mask].copy()

    if df_clean.empty:
        return df   # nothing to score

    if len(df_clean) < MIN_ROWS_FOR_IF:
        # Fallback: use mean absolute Z-score as anomaly proxy
        df_clean = _zscore_magnitude_fallback(df_clean)
    else:
        df_clean = _run_isolation_forest(df_clean)

    # Write results back into the full-index DataFrame
    df.loc[valid_mask, "anomaly_score"] = df_clean["anomaly_score"]
    df.loc[valid_mask, "is_anomaly"]    = df_clean["is_anomaly"]

    return df


# ─────────────────────────────────────────────────────────────────────────────
# Private helpers
# ─────────────────────────────────────────────────────────────────────────────

def _run_isolation_forest(df_clean: pd.DataFrame) -> pd.DataFrame:
    """
    Fit IsolationForest and write anomaly_score / is_anomaly back into df_clean.

    anomaly_score = -model.decision_function(X)
        decision_function returns values near +0.5 for normal, near -0.5 for
        anomalous.  Negating makes the value intuitively "higher = worse."

    is_anomaly = (model.predict(X) == -1)
        IsolationForest labels the contamination fraction as -1.
    """
    X = df_clean[FEATURE_COLS].values.astype(float)

    model = IsolationForest(
        n_estimators  = N_ESTIMATORS,
        contamination = CONTAMINATION,
        random_state  = RANDOM_STATE,
        n_jobs        = 1,
    )
    model.fit(X)

    raw_scores = -model.decision_function(X)   # flip: higher = more anomalous
    labels     = model.predict(X)              # -1 = anomaly, 1 = normal

    df_clean = df_clean.copy()
    df_clean["anomaly_score"] = raw_scores
    df_clean["is_anomaly"]    = (labels == -1)
    return df_clean


def _zscore_magnitude_fallback(df_clean: pd.DataFrame) -> pd.DataFrame:
    """
    Pure Z-score fallback used when there are too few rows for IsolationForest.

    anomaly_score = mean(|VAI_z|, |VBS_z|, |PVD_z|, |LIP_z|)
    is_anomaly    = any single signal |z| > 2.0
    """
    z_abs = df_clean[FEATURE_COLS].abs()
    df_clean = df_clean.copy()
    df_clean["anomaly_score"] = z_abs.mean(axis=1).fillna(0.0)
    df_clean["is_anomaly"]    = (z_abs > 2.0).any(axis=1)
    return df_clean
