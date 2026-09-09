"""Unit tests for alert state management and audit trail write-backs."""
import pytest
from aml_app.services.data_service import data_service

def test_alert_status_transition_and_audit():
    alert_id = 193
    # Update to UNDER REVIEW
    ok = data_service.update_alert_status(alert_id, "UNDER REVIEW", "test_analyst")
    assert ok is True

    # Verify detail reflects updated status
    alert = data_service.get_alert_detail(alert_id)
    assert alert is not None
    assert alert["STATUS"] == "UNDER REVIEW"

    # Verify audit log contains entry
    audit_df = data_service.get_audit_trail(limit=5)
    matching = audit_df[audit_df["entity_id"] == str(alert_id)]
    assert not matching.empty
    assert matching.iloc[0]["action"] == "UPDATE_STATUS"

def test_add_comment_and_audit():
    alert_id = 193
    comment_text = "Automated test case verification note."
    ok = data_service.add_alert_comment(alert_id, comment_text, "test_analyst")
    assert ok is True

    # Verify comment was stored
    alert = data_service.get_alert_detail(alert_id)
    comments = alert.get("comments", [])
    assert any(c["comment_text"] == comment_text for c in comments)
