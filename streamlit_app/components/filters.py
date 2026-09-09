"""Reusable Filter Controls for AML Investigation Platform."""
from typing import Optional, Tuple
import streamlit as st

def render_risk_slider(default_min: float = 0.0, key: str = "filter_risk_slider") -> float:
    """Render a standard risk score threshold slider."""
    return st.slider(
        "Minimum Risk Score",
        min_value=0.0,
        max_value=1.0,
        value=default_min,
        step=0.05,
        key=key,
        help="Filter alerts or entities scoring at or above this threshold"
    )

def render_amount_range_filter(
    min_val: float = 0.0,
    max_val: float = 1_000_000.0,
    key_prefix: str = "tx_filter"
) -> Tuple[Optional[float], Optional[float]]:
    """Render min and max amount input fields."""
    col1, col2 = st.columns(2)
    with col1:
        min_amt = st.number_input("Min Amount ($)", min_value=0.0, value=min_val, step=1000.0, key=f"{key_prefix}_min")
    with col2:
        max_amt = st.number_input("Max Amount ($)", min_value=0.0, value=max_val, step=5000.0, key=f"{key_prefix}_max")
    return (min_amt if min_amt > 0 else None, max_amt if max_amt < 1_000_000.0 else None)

def render_status_selector(key: str = "filter_status_select") -> str:
    """Render standard investigation status dropdown."""
    return st.selectbox(
        "Triage Status",
        options=["ALL", "OPEN", "UNDER REVIEW", "ESCALATED", "CLOSED_SAR", "CLOSED_FALSE_POSITIVE"],
        key=key
    )
