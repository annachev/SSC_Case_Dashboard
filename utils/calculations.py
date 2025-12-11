"""
Metric calculations and interpolation logic for the Philips Threshold Dashboard.

This module handles:
- Linear interpolation for non-standard threshold values
- Neutral stakeholder perspective data (no status indicators)
- Metric retrieval and caching
"""

from typing import Dict, Any, Tuple, Optional
import numpy as np
import streamlit as st

from data.exhibits import (
    THRESHOLDS,
    GEOGRAPHIC_FAIRNESS,
    STANDARD_THRESHOLDS,
    TOTAL_SUPPLIERS
)


def is_standard_threshold(threshold: float) -> bool:
    """
    Check if a threshold value is in the standard set with actual model output.

    Args:
        threshold: The threshold value to check

    Returns:
        True if threshold is a standard value, False otherwise
    """
    return threshold in STANDARD_THRESHOLDS


def get_neighboring_thresholds(threshold: float) -> Tuple[float, float]:
    """
    Find the two standard thresholds that bracket the given threshold.

    Args:
        threshold: The threshold value to find neighbors for

    Returns:
        Tuple of (lower_threshold, upper_threshold)
    """
    sorted_thresholds = sorted(STANDARD_THRESHOLDS)

    # Handle edge cases
    if threshold <= sorted_thresholds[0]:
        return sorted_thresholds[0], sorted_thresholds[1]
    if threshold >= sorted_thresholds[-1]:
        return sorted_thresholds[-2], sorted_thresholds[-1]

    # Find bracketing thresholds
    for i in range(len(sorted_thresholds) - 1):
        if sorted_thresholds[i] <= threshold <= sorted_thresholds[i + 1]:
            return sorted_thresholds[i], sorted_thresholds[i + 1]

    # Fallback (shouldn't reach here)
    return sorted_thresholds[0], sorted_thresholds[-1]


def interpolate_value(
    threshold: float,
    lower_thresh: float,
    upper_thresh: float,
    lower_val: float,
    upper_val: float
) -> float:
    """
    Perform linear interpolation between two values.

    Args:
        threshold: The target threshold
        lower_thresh: The lower bounding threshold
        upper_thresh: The upper bounding threshold
        lower_val: The value at the lower threshold
        upper_val: The value at the upper threshold

    Returns:
        Interpolated value at the target threshold
    """
    if upper_thresh == lower_thresh:
        return lower_val

    ratio = (threshold - lower_thresh) / (upper_thresh - lower_thresh)
    return lower_val + ratio * (upper_val - lower_val)


@st.cache_data
def get_metrics_for_threshold(threshold: float) -> Dict[str, Any]:
    """
    Get all metrics for a given threshold, using interpolation if needed.

    Args:
        threshold: The threshold value (0.45 to 0.75)

    Returns:
        Dictionary with all metrics for the threshold
    """
    # If it's a standard threshold, return exact values
    if is_standard_threshold(threshold):
        return THRESHOLDS[threshold].copy()

    # Otherwise, interpolate
    lower_thresh, upper_thresh = get_neighboring_thresholds(threshold)
    lower_metrics = THRESHOLDS[lower_thresh]
    upper_metrics = THRESHOLDS[upper_thresh]

    interpolated = {}
    for key in lower_metrics:
        interpolated[key] = interpolate_value(
            threshold,
            lower_thresh,
            upper_thresh,
            lower_metrics[key],
            upper_metrics[key]
        )
        # Round certain metrics to integers
        if key in ["flagged", "false_positives", "false_negatives"]:
            interpolated[key] = int(round(interpolated[key]))

    return interpolated


def get_geographic_rates_for_threshold(threshold: float) -> Dict[str, float]:
    """
    Get geographic flagging rates for a given threshold.
    Uses interpolation for non-standard thresholds.

    Args:
        threshold: The threshold value

    Returns:
        Dictionary mapping region to flagging rate
    """
    geo_thresholds = [0.50, 0.60, 0.70]

    # If exact match, return directly
    if threshold in geo_thresholds:
        return {region: rates[threshold] for region, rates in GEOGRAPHIC_FAIRNESS.items()}

    # Find neighboring thresholds
    if threshold < 0.50:
        lower_thresh, upper_thresh = 0.50, 0.60
    elif threshold > 0.70:
        lower_thresh, upper_thresh = 0.60, 0.70
    elif threshold < 0.60:
        lower_thresh, upper_thresh = 0.50, 0.60
    else:
        lower_thresh, upper_thresh = 0.60, 0.70

    result = {}
    for region, rates in GEOGRAPHIC_FAIRNESS.items():
        result[region] = interpolate_value(
            threshold,
            lower_thresh,
            upper_thresh,
            rates[lower_thresh],
            rates[upper_thresh]
        )

    return result


def calculate_geographic_disparity(threshold: float) -> float:
    """
    Calculate the maximum disparity in flagging rates across regions.

    Args:
        threshold: The threshold value

    Returns:
        The difference between max and min regional flagging rates
    """
    rates = get_geographic_rates_for_threshold(threshold)
    return max(rates.values()) - min(rates.values())


def get_stakeholder_perspectives(threshold: float) -> Dict[str, Dict[str, Any]]:
    """
    Get neutral stakeholder perspective data for a given threshold.

    This provides factual comparisons without any status indicators,
    suggestions, or value judgments about which threshold is better.

    Args:
        threshold: The threshold value

    Returns:
        Dictionary with perspective data for each stakeholder
    """
    metrics = get_metrics_for_threshold(threshold)
    disparity = calculate_geographic_disparity(threshold)
    geo_rates = get_geographic_rates_for_threshold(threshold)

    # CFO reference values (prefers threshold 0.50)
    cfo_preferred_cost = 4.6  # Cost at threshold 0.50
    cfo_cost_gap = metrics["cost"] - cfo_preferred_cost
    cfo_cost_gap_pct = (cfo_cost_gap / cfo_preferred_cost) * 100 if cfo_preferred_cost > 0 else 0

    # CSO reference values (prefers threshold 0.70)
    cso_preferred_fn = 119  # False negatives at threshold 0.70
    cso_fn_gap = metrics["false_negatives"] - cso_preferred_fn
    cso_fn_gap_pct = (cso_fn_gap / cso_preferred_fn) * 100 if cso_preferred_fn > 0 else 0

    return {
        "cfo": {
            "name": "Hans Verhoeven",
            "role": "CFO",
            "focus": "Cost Minimization",
            "preferred_threshold": 0.50,
            "preferred_cost": cfo_preferred_cost,
            "current_cost": metrics["cost"],
            "cost_gap": cfo_cost_gap,
            "cost_gap_pct": cfo_cost_gap_pct,
            "quote": "I prefer closer to the $4-5M range we discussed. Have you considered threshold 0.50?"
        },
        "cso": {
            "name": "Dr. Amelia Okonkwo",
            "role": "CSO",
            "focus": "Risk Mitigation",
            "preferred_threshold": 0.70,
            "preferred_fn": cso_preferred_fn,
            "current_fn": metrics["false_negatives"],
            "fn_gap": cso_fn_gap,
            "fn_gap_pct": cso_fn_gap_pct,
            "quote": "When we miss problematic suppliers and that becomes a front-page story, what's the cost to our brand? I'd push for 0.70 to catch more."
        },
        "relations": {
            "name": "James Park",
            "role": "Supplier Relations",
            "focus": "Partnership",
            "flagged_pct": metrics["flagged_pct"],
            "flagged_count": metrics["flagged"],
            "quote": f"We've spent five years building collaborative relationships through the SSP program. Flagging {metrics['flagged_pct']:.0f}% of suppliers sends a message about the partnership approach."
        },
        "counsel": {
            "name": "Lisa Martinez",
            "role": "General Counsel",
            "focus": "Fairness",
            "disparity": disparity,
            "china_rate": geo_rates.get("China", 0),
            "india_rate": geo_rates.get("India", 0),
            "other_rate": geo_rates.get("Other", 0),
            "quote": "If the model systematically flags certain regions at higher rates not because of actual sustainability differences but because of training data limitations, we have both a legal risk and an ethical problem."
        }
    }


def get_delta_vs_reference(
    current_threshold: float,
    reference_threshold: float = 0.60
) -> Dict[str, float]:
    """
    Calculate the delta (change) in metrics vs a reference threshold.

    Args:
        current_threshold: The current threshold value
        reference_threshold: The reference threshold to compare against

    Returns:
        Dictionary with delta values for key metrics
    """
    current = get_metrics_for_threshold(current_threshold)
    reference = get_metrics_for_threshold(reference_threshold)

    return {
        "flagged": current["flagged"] - reference["flagged"],
        "flagged_pct": current["flagged_pct"] - reference["flagged_pct"],
        "cost": current["cost"] - reference["cost"],
        "false_positives": current["false_positives"] - reference["false_positives"],
        "false_negatives": current["false_negatives"] - reference["false_negatives"],
        "accuracy": current["accuracy"] - reference["accuracy"]
    }
