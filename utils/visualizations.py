"""
Plotly visualization functions for the Philips Threshold Dashboard.

This module provides chart generation functions for:
- Cost vs. Risk Trade-off scatter plot
- Geographic Fairness horizontal bar chart
"""

from typing import Dict, List, Optional
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from data.exhibits import (
    THRESHOLDS,
    GEOGRAPHIC_FAIRNESS,
    SAMPLE_SIZES,
    STANDARD_THRESHOLDS
)
from utils.calculations import (
    get_metrics_for_threshold,
    get_geographic_rates_for_threshold
)

# Philips brand colors
COLORS = {
    "primary": "#0E1C36",      # Philips dark blue
    "secondary": "#00629B",    # Philips light blue
    "positive": "#00A651",     # Green
    "negative": "#E4002B",     # Red
    "neutral": "#F0F0F0",      # Light gray
    "warning": "#FFC107",      # Yellow/amber
    "highlight": "#00629B",    # Highlight color (light blue)
}


@st.cache_data
def create_cost_risk_chart(selected_threshold: float) -> go.Figure:
    """
    Create a scatter plot showing the cost vs. risk trade-off.

    X-axis: Annual Cost ($M)
    Y-axis: False Negatives (missed risks)
    Points represent all standard thresholds with the selected one highlighted.

    Args:
        selected_threshold: The currently selected threshold value

    Returns:
        Plotly Figure object
    """
    # Prepare data for all standard thresholds
    costs = []
    false_negatives = []
    thresholds = []

    for thresh in sorted(STANDARD_THRESHOLDS):
        metrics = THRESHOLDS[thresh]
        costs.append(metrics["cost"])
        false_negatives.append(metrics["false_negatives"])
        thresholds.append(thresh)

    # Create figure
    fig = go.Figure()

    # Add line connecting all points (trade-off frontier)
    fig.add_trace(go.Scatter(
        x=costs,
        y=false_negatives,
        mode="lines",
        line=dict(color=COLORS["neutral"], width=2, dash="dot"),
        showlegend=False,
        hoverinfo="skip"
    ))

    # Add points for all thresholds
    for i, thresh in enumerate(thresholds):
        is_selected = abs(thresh - selected_threshold) < 0.01
        marker_size = 20 if is_selected else 12
        marker_color = COLORS["highlight"] if is_selected else COLORS["primary"]
        marker_symbol = "star" if is_selected else "circle"

        fig.add_trace(go.Scatter(
            x=[costs[i]],
            y=[false_negatives[i]],
            mode="markers+text",
            marker=dict(
                size=marker_size,
                color=marker_color,
                symbol=marker_symbol,
                line=dict(width=2, color="white")
            ),
            text=[f"{thresh:.2f}"],
            textposition="top center",
            textfont=dict(size=12, color=COLORS["primary"]),
            name=f"Threshold {thresh:.2f}",
            hovertemplate=(
                f"<b>Threshold: {thresh:.2f}</b><br>"
                f"Cost: ${costs[i]:.1f}M<br>"
                f"False Negatives: {false_negatives[i]}<br>"
                "<extra></extra>"
            )
        ))

    # Add selected threshold if it's not a standard one
    if selected_threshold not in STANDARD_THRESHOLDS:
        sel_metrics = get_metrics_for_threshold(selected_threshold)
        fig.add_trace(go.Scatter(
            x=[sel_metrics["cost"]],
            y=[sel_metrics["false_negatives"]],
            mode="markers+text",
            marker=dict(
                size=20,
                color=COLORS["highlight"],
                symbol="star",
                line=dict(width=2, color="white")
            ),
            text=[f"{selected_threshold:.2f}*"],
            textposition="top center",
            textfont=dict(size=12, color=COLORS["highlight"]),
            name=f"Selected: {selected_threshold:.2f} (interpolated)",
            hovertemplate=(
                f"<b>Threshold: {selected_threshold:.2f} (interpolated)</b><br>"
                f"Cost: ${sel_metrics['cost']:.1f}M<br>"
                f"False Negatives: {sel_metrics['false_negatives']}<br>"
                "<extra></extra>"
            )
        ))

    # Update layout
    fig.update_layout(
        title=dict(
            text="Cost vs. Risk Trade-off",
            font=dict(size=18, color=COLORS["primary"])
        ),
        xaxis=dict(
            title=dict(text="Annual Cost ($M)", font=dict(size=14)),
            range=[4, 8.5],
            gridcolor=COLORS["neutral"],
            tickformat="$.1f"
        ),
        yaxis=dict(
            title=dict(text="False Negatives (Missed Risks)", font=dict(size=14)),
            range=[100, 230],
            gridcolor=COLORS["neutral"]
        ),
        showlegend=False,
        plot_bgcolor="white",
        margin=dict(l=60, r=40, t=60, b=60),
        hovermode="closest"
    )

    # Add annotation for key insight
    fig.add_annotation(
        text="Lower is better on both axes<br>(but impossible to optimize both)",
        xref="paper", yref="paper",
        x=0.98, y=0.02,
        showarrow=False,
        font=dict(size=11, color=COLORS["primary"]),
        align="right",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor=COLORS["neutral"],
        borderwidth=1
    )

    return fig


@st.cache_data
def create_geographic_fairness_chart(selected_threshold: float) -> go.Figure:
    """
    Create a horizontal bar chart showing geographic flagging rates.

    Groups bars by region, with different colors for each threshold level.
    Highlights the selected threshold.

    Args:
        selected_threshold: The currently selected threshold value

    Returns:
        Plotly Figure object
    """
    regions = list(GEOGRAPHIC_FAIRNESS.keys())
    geo_thresholds = [0.50, 0.60, 0.70]

    # Colors for each threshold (gradient from light to dark)
    threshold_colors = {
        0.50: "#B3D9E8",  # Light blue
        0.60: "#5BA3C6",  # Medium blue
        0.70: "#0E1C36",  # Dark blue (Philips primary)
    }

    fig = go.Figure()

    # Add bars for each threshold
    for thresh in geo_thresholds:
        rates = [GEOGRAPHIC_FAIRNESS[region][thresh] for region in regions]

        # Determine if this threshold should be highlighted
        is_selected = abs(thresh - selected_threshold) < 0.06

        fig.add_trace(go.Bar(
            y=regions,
            x=rates,
            name=f"Threshold {thresh:.2f}",
            orientation="h",
            marker=dict(
                color=threshold_colors[thresh],
                line=dict(
                    width=3 if is_selected else 0,
                    color=COLORS["highlight"]
                )
            ),
            text=[f"{r:.1f}%" for r in rates],
            textposition="auto",
            textfont=dict(color="white" if thresh == 0.70 else COLORS["primary"]),
            hovertemplate=(
                f"<b>Threshold: {thresh:.2f}</b><br>"
                "%{y}: %{x:.1f}%<br>"
                "<extra></extra>"
            )
        ))

    # Update layout
    fig.update_layout(
        title=dict(
            text="Geographic Flagging Rates by Threshold",
            font=dict(size=18, color=COLORS["primary"])
        ),
        xaxis=dict(
            title=dict(text="Flagging Rate (%)", font=dict(size=14)),
            range=[0, 100],
            gridcolor=COLORS["neutral"]
        ),
        yaxis=dict(
            title="",
            categoryorder="array",
            categoryarray=regions[::-1]  # Reverse for better display
        ),
        barmode="group",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        plot_bgcolor="white",
        margin=dict(l=80, r=40, t=80, b=60),
        bargap=0.15,
        bargroupgap=0.1
    )

    # Add sample size annotations
    for i, region in enumerate(regions[::-1]):
        n = SAMPLE_SIZES[region]
        warning = " ⚠️" if n < 30 else ""
        fig.add_annotation(
            text=f"n={n}{warning}",
            x=98,
            y=region,
            showarrow=False,
            font=dict(
                size=10,
                color=COLORS["negative"] if n < 30 else COLORS["primary"]
            ),
            xanchor="right"
        )

    return fig


