"""
Correlation analysis service for detecting relationships between metrics.
Supports Pearson correlation, lag detection, and interpretation.
"""

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from app.models.schemas import CorrelationInsight, CorrelationPair
from app.services.ingestion import DatasetBundle

logger = logging.getLogger(__name__)


class CorrelationAnalyzer:
    """
    Analyzes relationships between metrics in a dataset.

    Computes Pearson correlation matrix, identifies strong pairs,
    detects lagged correlations, and generates interpretations.
    """

    def __init__(
        self,
        correlation_threshold: float = 0.7,
        max_pairs: int = 10,
        lag_range: int = 1,
        min_observations: int = 4,
    ):
        """
        Args:
            correlation_threshold: Minimum correlation strength to flag (0-1)
            max_pairs: Maximum number of correlation pairs to return
            lag_range: Number of periods to check for lagged correlations
            min_observations: Minimum data points required for correlation
        """
        self.correlation_threshold = correlation_threshold
        self.max_pairs = max_pairs
        self.lag_range = lag_range
        self.min_observations = min_observations

    def identify_strong_pairs(
        self, dataset: DatasetBundle
    ) -> Optional[CorrelationInsight]:
        """
        Identify strong correlation pairs in the dataset.

        Args:
            dataset: DatasetBundle with pivoted metrics as columns

        Returns:
            CorrelationInsight with detected pairs and interpretation
        """
        try:
            if len(dataset.metric_columns) < 2:
                logger.info("Insufficient metrics for correlation analysis")
                return None

            if len(dataset.frame) < self.min_observations:
                logger.info(f"Insufficient observations (need {self.min_observations}, have {len(dataset.frame)})")
                return None

            # Compute correlation matrix
            corr_matrix = self.compute_correlation_matrix(dataset)
            if corr_matrix is None:
                return None

            # Identify strong pairs
            pairs = self._extract_strong_pairs(corr_matrix, dataset.metric_columns)

            if not pairs:
                logger.info("No strong correlations detected")
                return None

            # Detect lagged correlations
            pairs_with_lags = self._detect_lags(dataset, pairs)

            # Generate interpretation
            dominant_drivers = self._identify_drivers(pairs_with_lags)
            counter_indicators = [p for p in pairs_with_lags if p.relationship_type == "negative"]

            return CorrelationInsight(
                pairs=pairs_with_lags,
                dominant_drivers=dominant_drivers,
                counter_indicators=counter_indicators,
            )

        except Exception as e:
            logger.warning(f"Correlation analysis failed: {e}")
            return None

    def compute_correlation_matrix(self, dataset: DatasetBundle) -> Optional[np.ndarray]:
        """
        Compute Pearson correlation matrix for all metrics.

        Args:
            dataset: DatasetBundle with pivoted metrics

        Returns:
            Correlation matrix or None if computation fails
        """
        try:
            # Select only numeric columns
            numeric_cols = dataset.frame.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) < 2:
                return None

            # Filter to known metrics (exclude extra columns)
            metrics_to_use = [col for col in numeric_cols if col in dataset.metric_columns]
            if len(metrics_to_use) < 2:
                return None

            # Compute correlation
            corr_matrix = dataset.frame[metrics_to_use].corr(method="pearson").values
            return corr_matrix

        except Exception as e:
            logger.warning(f"Correlation matrix computation failed: {e}")
            return None

    def _extract_strong_pairs(self, corr_matrix: np.ndarray, metric_names: list[str]) -> list[CorrelationPair]:
        """
        Extract correlation pairs above threshold.

        Args:
            corr_matrix: Correlation matrix (NxN)
            metric_names: List of metric names

        Returns:
            List of CorrelationPair objects sorted by strength
        """
        pairs = []

        # Iterate through upper triangle (avoid duplicates)
        for i in range(len(metric_names)):
            for j in range(i + 1, len(metric_names)):
                corr_strength = corr_matrix[i, j]

                # Skip NaN or weak correlations
                if np.isnan(corr_strength) or abs(corr_strength) < self.correlation_threshold:
                    continue

                # Classify relationship type
                if corr_strength > 0:
                    relationship = "positive"
                    interpretation = f"As {metric_names[i]} increases, {metric_names[j]} tends to increase"
                else:
                    relationship = "negative"
                    interpretation = f"As {metric_names[i]} increases, {metric_names[j]} tends to decrease"

                pair = CorrelationPair(
                    metric_a=metric_names[i],
                    metric_b=metric_names[j],
                    correlation_strength=float(corr_strength),
                    relationship_type=relationship,
                    lag_periods=0,
                    interpretation=interpretation,
                )
                pairs.append(pair)

        # Sort by absolute correlation strength (descending)
        pairs.sort(key=lambda p: abs(p.correlation_strength), reverse=True)

        # Limit to max_pairs
        return pairs[: self.max_pairs]

    def _detect_lags(self, dataset: DatasetBundle, pairs: list[CorrelationPair]) -> list[CorrelationPair]:
        """
        Detect lagged correlations between metric pairs.

        Args:
            dataset: DatasetBundle with metric data
            pairs: List of correlation pairs to check for lags

        Returns:
            Updated pairs with optimal lag_periods set
        """
        pairs_with_lags = []

        for pair in pairs:
            best_lag = 0
            best_corr = abs(pair.correlation_strength)

            # Check if metrics exist in frame
            if pair.metric_a not in dataset.frame.columns or pair.metric_b not in dataset.frame.columns:
                pairs_with_lags.append(pair)
                continue

            # Test lagged correlations
            try:
                for lag in range(1, self.lag_range + 1):
                    # Correlate metric_a(t) with metric_b(t+lag)
                    corr_forward = dataset.frame[pair.metric_a].corr(dataset.frame[pair.metric_b].shift(lag))
                    if abs(corr_forward) > best_corr:
                        best_corr = abs(corr_forward)
                        best_lag = lag

                    # Correlate metric_a(t+lag) with metric_b(t)
                    corr_backward = dataset.frame[pair.metric_a].shift(lag).corr(dataset.frame[pair.metric_b])
                    if abs(corr_backward) > best_corr:
                        best_corr = abs(corr_backward)
                        best_lag = -lag

            except Exception as e:
                logger.debug(f"Lag detection failed for {pair.metric_a}/{pair.metric_b}: {e}")

            # Update pair with best lag
            updated_pair = CorrelationPair(
                metric_a=pair.metric_a,
                metric_b=pair.metric_b,
                correlation_strength=best_corr,
                relationship_type=pair.relationship_type,
                lag_periods=best_lag,
                interpretation=self._update_interpretation(pair, best_lag),
            )
            pairs_with_lags.append(updated_pair)

        return pairs_with_lags

    def _update_interpretation(self, pair: CorrelationPair, lag_periods: int) -> str:
        """Update interpretation string to include lag information."""
        if lag_periods == 0:
            return pair.interpretation

        direction = "leads" if lag_periods > 0 else "lags behind"
        lag_text = f"{abs(lag_periods)} period(s)"

        if pair.relationship_type == "positive":
            return f"{pair.metric_a} {direction} {pair.metric_b} by {lag_text}. As {pair.metric_a} increases, {pair.metric_b} tends to follow."
        else:
            return f"{pair.metric_a} {direction} {pair.metric_b} by {lag_text}. As {pair.metric_a} increases, {pair.metric_b} tends to decrease."

    def _identify_drivers(self, pairs: list[CorrelationPair]) -> list[str]:
        """
        Identify dominant driver metrics (metrics that correlate with many others).

        Args:
            pairs: List of correlation pairs

        Returns:
            List of driver metric names
        """
        # Count how many times each metric appears as primary driver
        driver_count = {}
        for pair in pairs:
            # Metric A is considered a driver if it leads or has positive correlation
            driver_count[pair.metric_a] = driver_count.get(pair.metric_a, 0) + 1

        # Sort by occurrence and return top drivers
        if not driver_count:
            return []

        sorted_drivers = sorted(driver_count.items(), key=lambda x: x[1], reverse=True)
        return [metric for metric, _ in sorted_drivers[:3]]
