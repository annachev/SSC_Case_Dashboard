"""
Philips Supplier Sustainability - Threshold Decision Dashboard

An interactive Streamlit dashboard for MBA students to explore the trade-offs
between cost, risk, and fairness when choosing a sustainability assessment threshold.

This dashboard accompanies the case study about Sarah Chen's decision at Philips
regarding supplier sustainability assessment thresholds.
"""

import streamlit as st
import numpy as np

# Configure page - must be first Streamlit command
st.set_page_config(
    page_title="Philips Threshold Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Import after page config
from data.exhibits import (
    THRESHOLDS,
    GEOGRAPHIC_FAIRNESS,
    SAMPLE_SIZES,
    STANDARD_THRESHOLDS,
    STAKEHOLDER_PREFERENCES,
    TOTAL_SUPPLIERS
)
from utils.calculations import (
    get_metrics_for_threshold,
    get_geographic_rates_for_threshold,
    calculate_geographic_disparity,
    get_stakeholder_perspectives,
    get_delta_vs_reference,
    is_standard_threshold
)
from utils.visualizations import (
    create_cost_risk_chart,
    create_geographic_fairness_chart,
    COLORS
)


def render_header():
    """Render the dashboard header with title and context."""
    st.markdown(
        f"""
        <h1 style='color: {COLORS["primary"]}; margin-bottom: 0;'>
            PHILIPS SUPPLIER SUSTAINABILITY
        </h1>
        <h3 style='color: {COLORS["secondary"]}; margin-top: 0;'>
            Threshold Decision Dashboard
        </h3>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    Sarah Chen, VP of Sustainable Supply Chain at Philips, must decide what probability
    threshold to use for flagging suppliers for sustainability review. A lower threshold
    catches more problems but costs more; a higher threshold is cheaper but misses more risks.
    """)

    with st.expander("ℹ️ What is a threshold?"):
        st.markdown("""
        **Threshold** refers to the probability cutoff used by the predictive model to flag
        suppliers for detailed sustainability review.

        - **Lower threshold (e.g., 0.50)**: More suppliers flagged = higher cost, fewer missed risks
        - **Higher threshold (e.g., 0.70)**: Fewer suppliers flagged = lower cost, more missed risks

        The model outputs a probability (0-1) for each supplier. If the probability exceeds
        the threshold, that supplier is flagged for manual review.

        **Key terms:**
        - **False Positive (FP)**: A good supplier incorrectly flagged for review (wastes resources)
        - **False Negative (FN)**: A problematic supplier missed by the model (creates risk)
        """)


def render_threshold_selector() -> float:
    """Render the threshold selector with slider and quick-select buttons."""
    st.markdown("### Select Threshold")

    # Initialize session state for threshold if not exists
    if "threshold" not in st.session_state:
        st.session_state.threshold = 0.60

    # Quick select buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])

    with col1:
        if st.button("💰 CFO (0.50)", use_container_width=True, help="Cost-conscious: Lower threshold = lower cost"):
            st.session_state.threshold = 0.50

    with col2:
        if st.button("⚖️ Balanced (0.60)", use_container_width=True, help="Middle ground between cost and risk"):
            st.session_state.threshold = 0.60

    with col3:
        if st.button("🛡️ CSO (0.70)", use_container_width=True, help="Risk-averse: Higher threshold = fewer missed risks"):
            st.session_state.threshold = 0.70

    # Slider
    threshold = st.slider(
        "Threshold Value",
        min_value=0.45,
        max_value=0.75,
        value=st.session_state.threshold,
        step=0.01,
        format="%.2f",
        help="Drag to explore different threshold values",
        key="threshold_slider"
    )

    # Update session state
    st.session_state.threshold = threshold

    # Warning for non-standard thresholds
    if not is_standard_threshold(threshold):
        st.warning(
            "⚠️ **Interpolated values** - This threshold is not in the standard set "
            f"({', '.join(str(t) for t in STANDARD_THRESHOLDS)}). "
            "Displayed values are estimated through linear interpolation and do not represent actual model output."
        )

    return threshold


def render_metric_cards(threshold: float):
    """Render the key metrics cards."""
    st.markdown("### Key Metrics")

    metrics = get_metrics_for_threshold(threshold)
    deltas = get_delta_vs_reference(threshold, reference_threshold=0.60)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Suppliers Flagged",
            value=f"{metrics['flagged']:,} ({metrics['flagged_pct']:.1f}%)",
            delta=f"{deltas['flagged']:+d} vs 0.60",
            delta_color="off"
        )

    with col2:
        st.metric(
            label="Annual Cost",
            value=f"${metrics['cost']:.1f}M",
            delta=f"${deltas['cost']:+.1f}M vs 0.60",
            delta_color="inverse"  # Lower cost is better
        )

    with col3:
        st.metric(
            label="False Positives",
            value=f"{metrics['false_positives']}",
            delta=f"{deltas['false_positives']:+d} vs 0.60",
            delta_color="inverse",  # Fewer FP is better
            help="Good suppliers unnecessarily flagged for review"
        )

    with col4:
        st.metric(
            label="False Negatives",
            value=f"{metrics['false_negatives']}",
            delta=f"{deltas['false_negatives']:+d} vs 0.60",
            delta_color="inverse",  # Fewer FN is better
            help="Problematic suppliers missed by the model"
        )


def render_cost_risk_chart(threshold: float):
    """Render the cost vs. risk trade-off chart."""
    st.markdown("### Cost vs. Risk Trade-off")

    fig = create_cost_risk_chart(threshold)
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "⚡ **KEY INSIGHT:** No 'perfect' threshold exists - all involve trade-offs. "
        "Moving right on this chart (higher cost) generally means moving down (fewer missed risks), "
        "but the relationship isn't linear."
    )


def render_geographic_fairness_chart(threshold: float):
    """Render the geographic fairness chart."""
    st.markdown("### Geographic Fairness Analysis")

    fig = create_geographic_fairness_chart(threshold)
    st.plotly_chart(fig, use_container_width=True)

    # Calculate and display disparity
    rates = get_geographic_rates_for_threshold(threshold)
    disparity = max(rates.values()) - min(rates.values())

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        **Current Regional Rates (threshold ≈ {threshold:.2f}):**
        - China: {rates.get('China', rates.get(list(rates.keys())[0])):.1f}%
        - India: {rates.get('India', rates.get(list(rates.keys())[1])):.1f}%
        - Other: {rates.get('Other', rates.get(list(rates.keys())[2])):.1f}%

        **Maximum Disparity:** {disparity:.1f} percentage points
        """)

    with col2:
        if disparity > 20:
            st.error(
                f"⚠️ **High Disparity Warning:** The {disparity:.1f}pp difference in flagging rates "
                "between regions may indicate disparate impact. This could expose Philips to "
                "regulatory scrutiny or reputational risk."
            )
        elif disparity > 10:
            st.warning(
                f"⚠️ **Moderate Disparity:** The {disparity:.1f}pp difference in flagging rates "
                "between regions warrants monitoring."
            )
        else:
            st.success(
                f"✅ **Low Disparity:** The {disparity:.1f}pp difference in flagging rates "
                "indicates relatively balanced treatment across regions."
            )

    st.caption(
        "**Note:** The 'Other' region has only n=14 suppliers. "
        "Results for this region should be interpreted with caution due to small sample size."
    )


def render_stakeholder_perspectives(threshold: float):
    """Render neutral stakeholder perspective cards without status indicators."""
    st.markdown(
        f"### Stakeholder Perspectives at Threshold {threshold:.2f}",
    )

    perspectives = get_stakeholder_perspectives(threshold)

    # Create two rows of two columns each for the four stakeholders
    col1, col2 = st.columns(2)

    # First row: CFO and CSO
    with col1:
        render_cfo_card(perspectives["cfo"], threshold)

    with col2:
        render_cso_card(perspectives["cso"], threshold)

    col3, col4 = st.columns(2)

    # Second row: Supplier Relations and General Counsel
    with col3:
        render_relations_card(perspectives["relations"])

    with col4:
        render_counsel_card(perspectives["counsel"])

    # Key insight at bottom
    st.markdown("---")
    st.info(
        "**KEY INSIGHT:** No single threshold satisfies all stakeholders. "
        "Explore different thresholds to understand the trade-offs."
    )


def render_cfo_card(cfo: dict, threshold: float):
    """Render the CFO perspective card."""
    st.markdown(
        f"""
        <div style='
            border: 1px solid {COLORS["neutral"]};
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            background-color: white;
        '>
            <div style='font-size: 16px; font-weight: bold; color: {COLORS["primary"]}; border-bottom: 1px solid {COLORS["neutral"]}; padding-bottom: 8px; margin-bottom: 10px;'>
                {cfo["role"]} ({cfo["name"]}) - {cfo["focus"]}
            </div>
            <div style='font-size: 14px; color: {COLORS["primary"]}; margin-bottom: 6px;'>
                <strong>Prefers:</strong> Threshold {cfo["preferred_threshold"]:.2f} (${cfo["preferred_cost"]:.1f}M)
            </div>
            <div style='font-size: 14px; color: {COLORS["primary"]}; margin-bottom: 6px;'>
                <strong>Current:</strong> Threshold {threshold:.2f} (${cfo["current_cost"]:.1f}M)
            </div>
            <div style='font-size: 14px; color: {COLORS["primary"]}; margin-bottom: 12px;'>
                <strong>Gap:</strong> +${cfo["cost_gap"]:.1f}M (+{cfo["cost_gap_pct"]:.0f}% more expensive)
            </div>
            <div style='
                font-size: 14px;
                color: #555;
                font-style: italic;
                border-left: 3px solid {COLORS["secondary"]};
                padding-left: 10px;
            '>
                "{cfo["quote"]}"
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_cso_card(cso: dict, threshold: float):
    """Render the CSO perspective card."""
    st.markdown(
        f"""
        <div style='
            border: 1px solid {COLORS["neutral"]};
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            background-color: white;
        '>
            <div style='font-size: 16px; font-weight: bold; color: {COLORS["primary"]}; border-bottom: 1px solid {COLORS["neutral"]}; padding-bottom: 8px; margin-bottom: 10px;'>
                {cso["role"]} ({cso["name"]}) - {cso["focus"]}
            </div>
            <div style='font-size: 14px; color: {COLORS["primary"]}; margin-bottom: 6px;'>
                <strong>Prefers:</strong> Threshold {cso["preferred_threshold"]:.2f} ({cso["preferred_fn"]} false negatives)
            </div>
            <div style='font-size: 14px; color: {COLORS["primary"]}; margin-bottom: 6px;'>
                <strong>Current:</strong> Threshold {threshold:.2f} ({cso["current_fn"]} false negatives)
            </div>
            <div style='font-size: 14px; color: {COLORS["primary"]}; margin-bottom: 12px;'>
                <strong>Gap:</strong> +{cso["fn_gap"]} missed risks (+{cso["fn_gap_pct"]:.0f}% more)
            </div>
            <div style='
                font-size: 14px;
                color: #555;
                font-style: italic;
                border-left: 3px solid {COLORS["secondary"]};
                padding-left: 10px;
            '>
                "{cso["quote"]}"
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_relations_card(relations: dict):
    """Render the Supplier Relations perspective card."""
    st.markdown(
        f"""
        <div style='
            border: 1px solid {COLORS["neutral"]};
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            background-color: white;
        '>
            <div style='font-size: 16px; font-weight: bold; color: {COLORS["primary"]}; border-bottom: 1px solid {COLORS["neutral"]}; padding-bottom: 8px; margin-bottom: 10px;'>
                {relations["role"]} ({relations["name"]}) - {relations["focus"]}
            </div>
            <div style='font-size: 14px; color: {COLORS["primary"]}; margin-bottom: 12px;'>
                <strong>Current:</strong> {relations["flagged_pct"]:.0f}% flagged ({relations["flagged_count"]} suppliers)
            </div>
            <div style='
                font-size: 14px;
                color: #555;
                font-style: italic;
                border-left: 3px solid {COLORS["secondary"]};
                padding-left: 10px;
            '>
                "{relations["quote"]}"
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_counsel_card(counsel: dict):
    """Render the General Counsel perspective card."""
    st.markdown(
        f"""
        <div style='
            border: 1px solid {COLORS["neutral"]};
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            background-color: white;
        '>
            <div style='font-size: 16px; font-weight: bold; color: {COLORS["primary"]}; border-bottom: 1px solid {COLORS["neutral"]}; padding-bottom: 8px; margin-bottom: 10px;'>
                {counsel["role"]} ({counsel["name"]}) - {counsel["focus"]}
            </div>
            <div style='font-size: 14px; color: {COLORS["primary"]}; margin-bottom: 6px;'>
                <strong>Geographic disparity:</strong> {counsel["disparity"]:.1f} percentage points
            </div>
            <div style='font-size: 13px; color: {COLORS["primary"]}; margin-bottom: 4px;'>
                (China: {counsel["china_rate"]:.1f}% | n=1,172)
            </div>
            <div style='font-size: 13px; color: {COLORS["primary"]}; margin-bottom: 4px;'>
                (India: {counsel["india_rate"]:.1f}% | n=60)
            </div>
            <div style='font-size: 13px; color: {COLORS["primary"]}; margin-bottom: 12px;'>
                (Other: {counsel["other_rate"]:.1f}% | n=14)
            </div>
            <div style='
                font-size: 14px;
                color: #555;
                font-style: italic;
                border-left: 3px solid {COLORS["secondary"]};
                padding-left: 10px;
            '>
                "{counsel["quote"]}"
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_discussion_prompts():
    """Render the case discussion prompts."""
    with st.expander("📝 Discussion Questions"):
        st.markdown("""
        Use these questions to guide your case analysis:

        1. **Stakeholder Priorities:** Which stakeholder's concerns should matter most to Philips?
           How would you weigh cost savings against risk mitigation?

        2. **Geographic Fairness:** Is the disparity in flagging rates between regions acceptable?
           Why or why not? What are the ethical implications?

        3. **Regional Thresholds:** Should Philips consider using different thresholds by region
           to achieve more equitable outcomes? What are the trade-offs?

        4. **Worst Case Scenario:** What would happen if Philips misses a major sustainability
           violation at a supplier? How should this risk factor into the threshold decision?

        5. **Board Justification:** How would you justify your recommended threshold to the
           Philips board of directors? What data would you present?

        6. **Implementation:** Beyond the threshold, what other safeguards or processes should
           Philips implement to manage supplier sustainability risk?

        7. **Model Limitations:** What are the limitations of using a predictive model for this
           decision? When might human judgment be more appropriate?
        """)


def main():
    """Main application entry point."""
    # Render header
    render_header()

    st.markdown("---")

    # Threshold selector
    threshold = render_threshold_selector()

    st.markdown("---")

    # Key metrics
    render_metric_cards(threshold)

    st.markdown("---")

    # Charts in two columns
    col_left, col_right = st.columns(2)

    with col_left:
        render_cost_risk_chart(threshold)

    with col_right:
        render_geographic_fairness_chart(threshold)

    st.markdown("---")

    # Stakeholder perspectives (neutral comparison cards)
    render_stakeholder_perspectives(threshold)

    st.markdown("---")

    # Discussion prompts
    render_discussion_prompts()

    # Footer
    st.markdown("---")
    st.caption(
        "📊 Philips Supplier Sustainability Threshold Dashboard | "
        "Built for MBA Case Study Analysis | "
        "Data based on case exhibits"
    )


if __name__ == "__main__":
    main()
