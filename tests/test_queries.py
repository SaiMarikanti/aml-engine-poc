"""Unit tests for query execution, repository routing, and deterministic calculations."""
import pytest
from aml_app.services.data_service import data_service

def test_kpi_summary():
    kpis = data_service.get_kpi_summary()
    assert kpis["total_transactions"] >= 5
    assert kpis["total_alerts"] >= 5
    assert kpis["high_risk_alerts"] > 0
    assert kpis["open_cases"] > 0

def test_search_transactions():
    df, total = data_service.search_transactions(limit=10)
    assert len(df) > 0
    assert total >= len(df)
    assert "TX_ID" in df.columns
    assert "SENDER_ACCOUNT_ID" in df.columns

def test_get_transaction_details_deterministic():
    # Test existing alert transaction TX82
    tx = data_service.get_transaction_details(82)
    assert tx is not None
    assert tx["TX_ID"] == 82
    assert "detectors" in tx
    assert "RULE_SCORE" in tx
    assert "ML_PROBABILITY" in tx
    assert "RISK_SCORE" in tx
    assert "TRIGGERED_RULES" in tx
    # Final risk score must be composite calculation
    expected_composite = round(0.40 * tx["RULE_SCORE"] + 0.60 * tx["ML_PROBABILITY"], 2)
    assert tx["RISK_SCORE"] == expected_composite

def test_account_profile_deterministic():
    # Test existing account ACC_6976
    acc = data_service.get_account_profile(6976)
    assert acc is not None
    assert acc["ACCOUNT_ID"] == 6976
    assert "RISK_SCORE" in acc
    assert "risk_factors" in acc
    assert len(acc["risk_factors"]) > 0
    assert acc["INCOMING_COUNT"] >= 0
    assert acc["OUTGOING_COUNT"] >= 0

def test_global_search():
    results = data_service.global_search("TX82")
    assert len(results) >= 1
    assert results[0]["type"] == "TRANSACTION"
    assert results[0]["id"] == 82

def test_model_insights_schema():
    insights = data_service.get_model_insights()
    assert insights["model_version"] == "v1.0-batch"
    assert "feature_importance" in insights
    assert len(insights["feature_importance"]) == 8
    # Verify features match verified POC engineering
    feat_names = [f["feature"] for f in insights["feature_importance"]]
    assert "tx_amount" in feat_names
    assert "sender_velocity_count" in feat_names
    assert "cycle_participant_feature" in feat_names
