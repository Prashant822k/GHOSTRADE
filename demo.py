from engine.fetcher import fetch_ohlcv
from engine.signals import compute_signals
from engine.anomaly import run_anomaly_detection
from engine.scorer import compute_trust_score

print("=== GHOSTRADE Pipeline Smoke Test ===")

df = fetch_ohlcv("AAPL")
print(f"[1] Fetched: {len(df)} rows | cols: {list(df.columns)}")

df = compute_signals(df)
print(f"[2] Signals OK | VAI_z NaNs={df['VAI_z'].isna().sum()} | VBS_z NaNs={df['VBS_z'].isna().sum()}")

df = run_anomaly_detection(df)
flagged = int(df["is_anomaly"].sum())
score_min = round(float(df["anomaly_score"].min()), 3)
score_max = round(float(df["anomaly_score"].max()), 3)
print(f"[3] Anomaly OK | Flagged rows={flagged} | Score range=[{score_min}, {score_max}]")

r = compute_trust_score(df)
print(f"[4] Scorer OK")
print(f"    Trust Score : {r['trust_score']}")
print(f"    Label       : {r['label']}")
print(f"    Top Signal  : {r['top_flag']} @ {r['top_flag_sigma']} sigma")
print(f"    Vol Spike   : {r['volume_spike_pct']}%")
print(f"    Price Delta : {r['price_delta_3mo']}%")
print(f"    Active Sigs : {r['active_signals']}/4")
print("=== ALL STEPS PASSED ===")
