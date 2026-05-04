import base64
import io
import logging

import matplotlib
matplotlib.use("Agg")  # non-interactive backend — must be set before pyplot import
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd

from app.models.schemas import AnomalyInsight, MetricSnapshot
from app.services.ingestion import DatasetBundle

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Safe style selection – fall back gracefully if the requested style is gone
# ---------------------------------------------------------------------------
_PREFERRED_STYLES = ["seaborn-v0_8-darkgrid", "seaborn-darkgrid", "ggplot", "bmh"]

def _apply_safe_style() -> None:
    available = plt.style.available
    for style in _PREFERRED_STYLES:
        if style in available:
            plt.style.use(style)
            return
    # No preferred style found: use matplotlib defaults (always safe)
    plt.rcParams.update(plt.rcParamsDefault)


# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
_PALETTE = [
    "#4F8EF7", "#F76E4F", "#4FD1A5", "#F7C34F",
    "#A78BFA", "#F472B6", "#34D399", "#FB923C",
]

_TREND_COLORS = {"up": "#4FD1A5", "down": "#F76E4F", "flat": "#4F8EF7"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _buf_to_b64(buf: io.BytesIO, fig: plt.Figure, dpi: int) -> tuple[bytes, str]:
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    buf.seek(0)
    raw = buf.getvalue()
    plt.close(fig)
    return raw, base64.b64encode(raw).decode("utf-8")


class DataVisualizationService:
    """
    Generates clean, high-contrast Matplotlib charts.
    All outputs are Base64-encoded PNG bytes suitable for direct embedding
    and multimodal LLM vision prompts.
    """

    def __init__(self, figsize: tuple[int, int] = (14, 8), dpi: int = 100):
        self.figsize = figsize
        self.dpi = dpi

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_executive_dashboard(
        self,
        dataset: DatasetBundle,
        metric_snapshots: list[MetricSnapshot],
        anomalies: list[AnomalyInsight],
        max_trend_metrics: int = 4,
    ) -> tuple[bytes, str]:
        """
        Generate a rich multi-panel executive dashboard:
          - Panel A: KPI trend lines (up to max_trend_metrics)
          - Panel B: Latest-value bar chart with trend coloring
          - Panel C: Metric share pie / donut chart
          - Panel D: Anomaly heat strip (or summary card when none)
        """
        _apply_safe_style()

        metrics = dataset.metric_columns[:max_trend_metrics]
        dates = pd.to_datetime(dataset.frame["date"])

        # ── figure layout ──────────────────────────────────────────────
        fig = plt.figure(figsize=(self.figsize[0], self.figsize[1] + 4), dpi=self.dpi)
        gs = gridspec.GridSpec(
            2, 2,
            figure=fig,
            hspace=0.52,
            wspace=0.38,
            left=0.07, right=0.96,
            top=0.91, bottom=0.07,
        )

        ax_trend = fig.add_subplot(gs[0, :])   # full-width top
        ax_bar   = fig.add_subplot(gs[1, 0])   # bottom-left
        ax_pie   = fig.add_subplot(gs[1, 1])   # bottom-right

        fig.suptitle(
            "Executive KPI Dashboard",
            fontsize=16, fontweight="bold", y=0.97,
        )

        # ── Panel A: Trend lines ───────────────────────────────────────
        self._plot_trend_lines(ax_trend, dataset, metrics, dates, anomalies)

        # ── Panel B: Bar comparison ────────────────────────────────────
        self._plot_bar_comparison(ax_bar, metric_snapshots[:8])

        # ── Panel C: Pie distribution ──────────────────────────────────
        self._plot_pie_distribution(ax_pie, metric_snapshots[:8])

        buf = io.BytesIO()
        return _buf_to_b64(buf, fig, self.dpi)

    # backward-compat wrappers kept for pipeline.py ------------------

    def generate_multiplot_dashboard(
        self,
        dataset: DatasetBundle,
        anomalies: list[AnomalyInsight],
        max_metrics: int = 4,
        metric_snapshots: list[MetricSnapshot] | None = None,
    ) -> tuple[bytes, str]:
        return self.generate_executive_dashboard(
            dataset=dataset,
            metric_snapshots=metric_snapshots or [],
            anomalies=anomalies,
            max_trend_metrics=max_metrics,
        )

    def generate_comparison_chart(
        self,
        dataset: DatasetBundle,
        metric_snapshots: list[MetricSnapshot],
        max_metrics: int = 6,
    ) -> tuple[bytes, str]:
        return self.generate_executive_dashboard(
            dataset=dataset,
            metric_snapshots=metric_snapshots,
            anomalies=[],
            max_trend_metrics=max_metrics,
        )

    # legacy single-metric chart (unchanged) -------------------------

    def generate_anomaly_chart(
        self,
        dataset: DatasetBundle,
        anomaly: AnomalyInsight,
    ) -> tuple[bytes, str]:
        _apply_safe_style()
        metric_name = anomaly.metric
        if metric_name not in dataset.frame.columns:
            raise ValueError(f"Metric '{metric_name}' not found in dataset")

        dates = pd.to_datetime(dataset.frame["date"])
        values = dataset.frame[metric_name].astype(float)

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        ax.plot(dates, values, linewidth=2.5, color="#4F8EF7",
                label="Actual Value", marker="o", markersize=5, alpha=0.85)

        if anomaly.anomalous_points:
            rm_vals = [pt.rolling_mean for pt in anomaly.anomalous_points]
            mean_baseline = sum(rm_vals) / len(rm_vals)
            ax.axhline(y=mean_baseline, color="#4FD1A5", linestyle="--",
                       linewidth=2, label=f"Baseline ({mean_baseline:,.0f})", alpha=0.8)

        for point in anomaly.anomalous_points:
            pd_date = pd.to_datetime(point.date)
            idx = dates[dates == pd_date].index
            if len(idx) > 0:
                actual_value = values.iloc[idx[0]]
                color = "#d62728" if abs(point.zscore) >= 3 else (
                    "#ff7f0e" if abs(point.zscore) >= 2.5 else "#ffd700"
                )
                marker = "X" if abs(point.zscore) >= 3 else (
                    "s" if abs(point.zscore) >= 2.5 else "D"
                )
                ax.scatter(pd_date, actual_value, color=color, marker=marker,
                           s=160, edgecolors="black", linewidth=1.5, zorder=5)

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.xticks(rotation=45, ha="right")
        ax.set_title(
            f"{metric_name}  |  Severity: {anomaly.severity.upper()}  "
            f"|  {len(anomaly.anomalous_points)} anomalous point(s)",
            fontsize=13, fontweight="bold", pad=14,
        )
        ax.set_xlabel("Date", fontsize=11)
        ax.set_ylabel("Value", fontsize=11)
        ax.legend(fontsize=9, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle=":", linewidth=0.8)
        plt.tight_layout()

        buf = io.BytesIO()
        return _buf_to_b64(buf, fig, self.dpi)

    # ------------------------------------------------------------------
    # Private panel renderers
    # ------------------------------------------------------------------

    def _plot_trend_lines(
        self,
        ax: plt.Axes,
        dataset: DatasetBundle,
        metrics: list[str],
        dates: pd.Series,
        anomalies: list[AnomalyInsight],
    ) -> None:
        anomaly_metrics = {a.metric for a in anomalies}

        for i, metric in enumerate(metrics):
            if metric not in dataset.frame.columns:
                continue
            values = dataset.frame[metric].astype(float)
            color = _PALETTE[i % len(_PALETTE)]
            label = metric.replace("_", " ").title()

            ax.plot(
                dates, values,
                linewidth=2.2 if metric not in anomaly_metrics else 2.8,
                color=color,
                label=label,
                marker="o", markersize=4, alpha=0.88,
            )

            # Shade anomalous points
            for anomaly in anomalies:
                if anomaly.metric != metric:
                    continue
                for pt in anomaly.anomalous_points:
                    pd_date = pd.to_datetime(pt.date)
                    ax.axvspan(
                        pd_date - pd.Timedelta(days=10),
                        pd_date + pd.Timedelta(days=10),
                        color="#F76E4F", alpha=0.12, linewidth=0,
                    )

        ax.set_title("KPI Trend Lines", fontsize=12, fontweight="bold", pad=10)
        ax.set_xlabel("Date", fontsize=10)
        ax.set_ylabel("Value", fontsize=10)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=35, ha="right", fontsize=8)
        ax.legend(fontsize=8.5, loc="upper left", ncol=min(4, len(metrics)),
                  framealpha=0.9, edgecolor="#cccccc")
        ax.grid(True, alpha=0.25, linestyle=":", linewidth=0.8)

    def _plot_bar_comparison(
        self,
        ax: plt.Axes,
        snapshots: list[MetricSnapshot],
    ) -> None:
        if not snapshots:
            ax.text(0.5, 0.5, "No data", ha="center", va="center",
                    transform=ax.transAxes, fontsize=11, color="gray")
            ax.set_title("Latest Values", fontsize=12, fontweight="bold")
            return

        metrics = [s.metric.replace("_", " ").title() for s in snapshots]
        latest = [s.latest_value for s in snapshots]
        prev   = [s.previous_value if s.previous_value is not None else 0 for s in snapshots]
        colors = [_TREND_COLORS.get(s.trend_direction, "#4F8EF7") for s in snapshots]

        x = np.arange(len(metrics))
        width = 0.38

        bars_latest = ax.bar(x - width / 2, latest, width, color=colors,
                             alpha=0.88, edgecolor="none", label="Latest")
        bars_prev   = ax.bar(x + width / 2, prev,   width, color=colors,
                             alpha=0.45, edgecolor="none", label="Previous")

        # Value labels
        for bar in bars_latest:
            h = bar.get_height()
            if h != 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    h * 1.01,
                    f"{h:,.0f}",
                    ha="center", va="bottom", fontsize=6.5, fontweight="bold",
                )

        ax.set_xticks(x)
        ax.set_xticklabels(metrics, rotation=38, ha="right", fontsize=7.5)
        ax.set_title("Latest vs Previous", fontsize=12, fontweight="bold", pad=8)
        ax.set_ylabel("Value", fontsize=9)
        ax.legend(fontsize=8, framealpha=0.9)
        ax.grid(True, axis="y", alpha=0.25, linestyle=":", linewidth=0.8)

    def _plot_pie_distribution(
        self,
        ax: plt.Axes,
        snapshots: list[MetricSnapshot],
    ) -> None:
        if not snapshots:
            ax.text(0.5, 0.5, "No data", ha="center", va="center",
                    transform=ax.transAxes, fontsize=11, color="gray")
            ax.set_title("Metric Distribution", fontsize=12, fontweight="bold")
            return

        # Use absolute latest values for proportions; skip zeros/negatives
        valid = [(s.metric.replace("_", " ").title(), abs(s.latest_value))
                 for s in snapshots if s.latest_value and abs(s.latest_value) > 0]
        if not valid:
            ax.text(0.5, 0.5, "All values zero", ha="center", va="center",
                    transform=ax.transAxes, fontsize=10, color="gray")
            ax.set_title("Metric Distribution", fontsize=12, fontweight="bold")
            return

        labels, sizes = zip(*valid)
        colors = [_PALETTE[i % len(_PALETTE)] for i in range(len(labels))]
        explode = [0.04] * len(labels)

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=None,
            colors=colors,
            explode=explode,
            autopct="%1.1f%%",
            pctdistance=0.78,
            startangle=90,
            wedgeprops={"linewidth": 1.2, "edgecolor": "white"},
        )
        for at in autotexts:
            at.set_fontsize(7)
            at.set_color("white")
            at.set_fontweight("bold")

        # Draw a white centre circle to make it a donut
        centre_circle = plt.Circle((0, 0), 0.52, fc="white")
        ax.add_artist(centre_circle)

        ax.legend(
            wedges, labels,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.22),
            ncol=2,
            fontsize=7,
            framealpha=0.85,
        )
        ax.set_title("Value Share (Donut)", fontsize=12, fontweight="bold", pad=8)
