"""
Run this script from the project root to diagnose chart generation:
  python diagnose_chart.py
"""
import sys, traceback, os

print("=" * 60)
print("InsightBoard Chart Diagnostics")
print("=" * 60)

# ── 1. Python & path ────────────────────────────────────────────
print(f"\n[1] Python {sys.version}")
print(f"    CWD: {os.getcwd()}")

# ── 2. matplotlib ────────────────────────────────────────────────
print("\n[2] matplotlib")
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    print(f"    version  : {matplotlib.__version__}")
    print(f"    backend  : {matplotlib.get_backend()}")
    styles = plt.style.available
    print(f"    styles   : {[s for s in styles if 'seaborn' in s or 'ggplot' in s or 'bmh' in s]}")
    # quick render
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    import io, base64
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    b64 = base64.b64encode(buf.getvalue()).decode()
    print(f"    quick-render OK  ({len(b64)} chars)")
except Exception as e:
    print(f"    FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

# ── 3. numpy ─────────────────────────────────────────────────────
print("\n[3] numpy")
try:
    import numpy as np
    print(f"    version: {np.__version__}")
except Exception as e:
    print(f"    FAILED: {e}")

# ── 4. pandas ────────────────────────────────────────────────────
print("\n[4] pandas")
try:
    import pandas as pd
    print(f"    version: {pd.__version__}")
except Exception as e:
    print(f"    FAILED: {e}")

# ── 5. CSV ingestion ─────────────────────────────────────────────
print("\n[5] CSV ingestion")
dataset = None
snapshots = []
anomalies = []
try:
    from app.services.ingestion import CSVIngestionService
    svc = CSVIngestionService()

    csv_candidates = [
        "large_sales_data_transformed.csv",
        "large_sales_data.csv",
    ]
    csv_path = next((p for p in csv_candidates if os.path.exists(p)), None)
    if csv_path is None:
        print("    No sample CSV found — skipping ingestion test")
    else:
        with open(csv_path, "rb") as f:
            csv_bytes = f.read()[:200_000]  # limit to first 200 KB
        dataset = svc.load_csv(csv_bytes, aggregation_granularity="monthly",
                               missing_value_strategy="forward_fill")
        print(f"    metrics  : {dataset.metric_columns}")
        print(f"    shape    : {dataset.frame.shape}")
        print(f"    date col : {dataset.date_column}")
        print(f"    head:")
        print(dataset.frame.head(3).to_string(index=False))
except Exception as e:
    print(f"    FAILED: {e}")
    traceback.print_exc()

# ── 6. analytics + anomaly ───────────────────────────────────────
print("\n[6] analytics + anomaly detection")
if dataset is not None:
    try:
        from app.services.analytics import KPIAnalyzer
        from app.services.anomaly import AnomalyDetector
        analyzer = KPIAnalyzer()
        snapshots = analyzer.build_metric_snapshots(dataset)
        print(f"    snapshots: {len(snapshots)}")
        detector = AnomalyDetector(zscore_threshold=2.0, change_threshold=0.15)
        anomalies = detector.detect(dataset, snapshots)
        print(f"    anomalies: {len(anomalies)}")
    except Exception as e:
        print(f"    FAILED: {e}")
        traceback.print_exc()
else:
    print("    skipped (no dataset)")

# ── 7. visualization ─────────────────────────────────────────────
print("\n[7] visualization service")
if dataset is not None:
    try:
        from app.services.visualization import DataVisualizationService
        viz = DataVisualizationService()
        raw, b64 = viz.generate_executive_dashboard(dataset, snapshots, anomalies)
        print(f"    SUCCESS: {len(raw)} bytes  ({len(b64)} b64 chars)")
        # Save the image so you can open it
        out_path = "diagnose_chart_output.png"
        with open(out_path, "wb") as f:
            f.write(raw)
        print(f"    Saved : {out_path}  <- open this file to verify chart")
    except Exception as e:
        print(f"    FAILED: {e}")
        traceback.print_exc()
else:
    print("    skipped (no dataset)")

print("\n" + "=" * 60)
print("Diagnostics complete.")
print("=" * 60)
