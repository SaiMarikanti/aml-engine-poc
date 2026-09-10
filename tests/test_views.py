"""Test view imports, component interfaces, and page router definitions."""
import pytest

def test_view_imports():
    from aml_app.views import (
        render_dashboard,
        render_transactions,
        render_alerts,
        render_accounts,
        render_network,
        render_model_insights,
        render_audit,
        render_system_status,
    )
    assert callable(render_dashboard)
    assert callable(render_transactions)
    assert callable(render_alerts)
    assert callable(render_accounts)
    assert callable(render_network)
    assert callable(render_model_insights)
    assert callable(render_audit)
    assert callable(render_system_status)

def test_component_imports():
    from aml_app.components.sidebar import render_sidebar
    from aml_app.components.header import render_header
    from aml_app.components.kpi_card import render_kpi_card
    from aml_app.components.alert_card import render_evidence_chip
    from aml_app.components.network_graph import render_pyvis_network
    
    assert callable(render_sidebar)
    assert callable(render_header)
    assert callable(render_kpi_card)
    assert callable(render_evidence_chip)
    assert callable(render_pyvis_network)
