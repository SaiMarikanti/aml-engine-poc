"""Views package for Databricks AML Intelligence Platform."""
from aml_app.views.dashboard import render_dashboard
from aml_app.views.transactions import render_transactions
from aml_app.views.alerts import render_alerts
from aml_app.views.accounts import render_accounts
from aml_app.views.network import render_network
from aml_app.views.model_insights import render_model_insights
from aml_app.views.audit import render_audit
from aml_app.views.system_status import render_system_status

__all__ = [
    "render_dashboard",
    "render_transactions",
    "render_alerts",
    "render_accounts",
    "render_network",
    "render_model_insights",
    "render_audit",
    "render_system_status",
]
