"""Alert Cards Component.
Exports alert rendering utilities and evidence chips.
"""
try:
    from components.alert_card import render_evidence_chip
    from utils.formatting import render_risk_badge, render_status_chip, format_currency
except (ImportError, ModuleNotFoundError):
    from aml_app.components.alert_card import render_evidence_chip
    from aml_app.utils.formatting import render_risk_badge, render_status_chip, format_currency


def render_alert_summary_card(alert: dict) -> str:
    """Generate HTML card for an alert summary."""
    alert_id = alert.get("ALERT_ID", "")
    risk_score = alert.get("RISK_SCORE", 0.0)
    rule_desc = alert.get("TRIGGERED_RULE", alert.get("RULE_TRIGGERED", "Suspicious Activity"))
    amount = alert.get("TRANSACTION_AMOUNT", alert.get("AMOUNT", 0))
    status = alert.get("STATUS", "OPEN")
    
    badge = render_risk_badge(risk_score)
    chip = render_status_chip(status)
    curr = format_currency(amount)
    
    return f"""
    <div class="neo-card" style="padding: 16px 20px; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 700; color: #1E293B;">Alert #{alert_id}</span>
            <div>{chip} {badge}</div>
        </div>
        <div style="margin-top: 8px; font-size: 0.9rem; color: #475569;">{rule_desc}</div>
        <div style="margin-top: 6px; font-weight: 700; color: #0F172A;">Amount: {curr}</div>
    </div>
    """
