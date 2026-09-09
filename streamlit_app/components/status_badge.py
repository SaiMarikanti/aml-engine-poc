"""Status badges and risk indicators."""
from aml_app.utils.formatting import render_risk_badge, render_status_chip

def risk_badge_html(risk: str) -> str:
    return render_risk_badge(risk)

def status_chip_html(status: str) -> str:
    return render_status_chip(status)
