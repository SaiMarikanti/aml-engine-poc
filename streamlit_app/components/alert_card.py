"""Alert Triage Card Component."""
import streamlit as st
try:
    from utils.formatting import format_currency, render_risk_badge, render_status_chip
except (ImportError, ModuleNotFoundError):
    from aml_app.utils.formatting import format_currency, render_risk_badge, render_status_chip


def render_evidence_chip(engine_name: str, triggered: bool, label: str):
    """Render a clean evidence card for Rule / Graph / ML."""
    status_icon = "✓" if triggered else "○"
    border_color = "#DC2626" if triggered else "#9CA3AF"
    text_color = "#991B1B" if triggered else "#4B5563"
    bg_color = "#FEF2F2" if triggered else "#F3F4F6"
    
    return f"""
    <div style="flex: 1; min-width: 160px; background: {bg_color}; border-left: 4px solid {border_color}; 
                padding: 12px 14px; border-radius: 10px; margin: 4px;">
        <div style="font-size: 0.72rem; font-weight: 700; color: #6B7280; text-transform: uppercase;">{engine_name}</div>
        <div style="font-size: 0.88rem; font-weight: 700; color: {text_color}; margin-top: 4px;">
            {status_icon} {label}
        </div>
    </div>
    """
