"""Neumorphic KPI Card Component."""
import streamlit as st

def render_kpi_card(title: str, value: str, subtitle: str = "", trend_positive: bool = True, alert_level: str = "normal"):
    """Render a soft raised neumorphic KPI card."""
    border_indicator = ""
    if alert_level == "critical":
        border_indicator = "border-left: 4px solid #991B1B;"
    elif alert_level == "warning":
        border_indicator = "border-left: 4px solid #D97706;"
    elif alert_level == "success":
        border_indicator = "border-left: 4px solid #059669;"
    
    html = f"""
    <div class="neo-card" style="padding: 18px 22px; margin-bottom: 15px; {border_indicator}">
        <div class="neo-kpi-container">
            <span class="neo-kpi-title">{title}</span>
            <span class="neo-kpi-value">{value}</span>
            <span class="neo-kpi-delta" style="color: {'#059669' if trend_positive else '#DC2626'};">
                {subtitle}
            </span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
