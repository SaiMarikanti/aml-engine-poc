"""Formatting utilities for numbers, currency, timestamps, and badges."""
from datetime import datetime
from aml_app.utils.constants import RiskLevel, AlertStatus, RISK_COLORS

def format_currency(amount: float, symbol: str = "₹") -> str:
    """Format monetary amount with thousands separators and symbol."""
    if amount is None:
        return f"{symbol}0.00"
    if amount >= 10_000_000:
        return f"{symbol}{amount / 10_000_000:.2f} Cr"
    if amount >= 100_000:
        return f"{symbol}{amount / 100_000:.2f} L"
    if amount >= 1_000:
        return f"{symbol}{amount:,.2f}"
    return f"{symbol}{amount:.2f}"

def format_number(val: int | float) -> str:
    """Format standard counts with commas."""
    if val is None:
        return "0"
    return f"{val:,}"

def score_to_risk_level(score: float) -> RiskLevel:
    """Map numeric risk score [0, 1] to RiskLevel."""
    if score is None:
        return RiskLevel.LOW
    if score >= 0.85:
        return RiskLevel.CRITICAL
    if score >= 0.65:
        return RiskLevel.HIGH
    if score >= 0.40:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW

def render_risk_badge(risk: str | RiskLevel) -> str:
    """Generate HTML risk badge."""
    val = str(risk).upper()
    if "CRIT" in val:
        cls = "risk-critical"
    elif "HIGH" in val:
        cls = "risk-high"
    elif "MED" in val:
        cls = "risk-medium"
    else:
        cls = "risk-low"
    return f'<span class="risk-badge {cls}">{val}</span>'

def render_status_chip(status: str | AlertStatus) -> str:
    """Generate HTML status chip."""
    val = str(status).upper()
    if "CONFIRM" in val:
        cls = "status-confirmed"
    elif "REVIEW" in val:
        cls = "status-review"
    elif "FALSE" in val:
        cls = "status-false_positive"
    elif "CLOSE" in val:
        cls = "status-closed"
    else:
        cls = "status-open"
    return f'<span class="status-chip {cls}">{val}</span>'
