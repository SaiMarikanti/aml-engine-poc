"""Neumorphic KPI Cards Component.
Exports render_kpi_card and multi-card layouts.
"""
import streamlit as st
try:
    from components.kpi_card import render_kpi_card
except (ImportError, ModuleNotFoundError):
    from aml_app.components.kpi_card import render_kpi_card


def render_kpi_grid(kpis: list[dict]):
    """Render multiple KPI cards across standard responsive grid columns."""
    cols = st.columns(len(kpis))
    for col, item in zip(cols, kpis):
        with col:
            render_kpi_card(
                title=item.get("title", ""),
                value=str(item.get("value", "")),
                subtitle=item.get("subtitle", ""),
                trend_positive=item.get("trend_positive", True),
                alert_level=item.get("alert_level", "normal")
            )
