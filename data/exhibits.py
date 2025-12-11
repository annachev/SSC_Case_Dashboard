"""
Hardcoded case data for Philips Supplier Sustainability Threshold Dashboard.

This data comes from Exhibit 1 of the MBA case study and represents
the threshold scenario analysis for supplier sustainability assessment.
"""

from typing import Dict, Any

# Exhibit 1: Threshold Scenario Analysis
# Maps threshold values (0.50-0.70) to their corresponding metrics
THRESHOLDS: Dict[float, Dict[str, Any]] = {
    0.50: {
        "flagged": 571,           # Number of suppliers flagged for review
        "flagged_pct": 57.1,      # Percentage of total suppliers flagged
        "cost": 4.6,              # Annual cost in millions USD
        "false_positives": 113,   # Good suppliers incorrectly flagged
        "false_negatives": 159,   # Problematic suppliers missed
        "accuracy": 72.6          # Model accuracy percentage
    },
    0.55: {
        "flagged": 747,
        "flagged_pct": 74.7,
        "cost": 6.0,
        "false_positives": 65,
        "false_negatives": 186,
        "accuracy": 74.8
    },
    0.60: {
        "flagged": 861,
        "flagged_pct": 86.1,
        "cost": 6.9,
        "false_positives": 46,
        "false_negatives": 205,
        "accuracy": 74.8
    },
    0.65: {
        "flagged": 967,
        "flagged_pct": 96.7,
        "cost": 7.7,
        "false_positives": 13,
        "false_negatives": 173,
        "accuracy": 81.3
    },
    0.70: {
        "flagged": 994,
        "flagged_pct": 99.4,
        "cost": 8.0,
        "false_positives": 5,
        "false_negatives": 119,
        "accuracy": 87.5
    }
}

# Geographic fairness data: flagging rates by region at different thresholds
# Shows potential disparate impact across regions
GEOGRAPHIC_FAIRNESS: Dict[str, Dict[float, float]] = {
    "China": {0.50: 49.9, 0.60: 67.2, 0.70: 85.1},
    "India": {0.50: 51.7, 0.60: 68.3, 0.70: 90.0},
    "Other": {0.50: 42.9, 0.60: 84.6, 0.70: 92.9}
}

# Sample sizes by region - important for statistical significance
# Note: "Other" has very small sample size (n=14)
SAMPLE_SIZES: Dict[str, int] = {
    "China": 1172,
    "India": 60,
    "Other": 14
}

# Standard thresholds that have actual model output (not interpolated)
STANDARD_THRESHOLDS = [0.50, 0.55, 0.60, 0.65, 0.70]

# Stakeholder preference thresholds
STAKEHOLDER_PREFERENCES = {
    "CFO": 0.50,      # Cost-conscious: lower threshold = lower cost
    "CSO": 0.70,      # Risk-averse: higher threshold = fewer missed risks
    "Balanced": 0.60  # Middle ground between cost and risk
}

# Total number of suppliers in the assessment
TOTAL_SUPPLIERS = 1000
