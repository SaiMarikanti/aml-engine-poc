"""Alerts Domain Service.
Provides business logic and data access for AML alerts.
"""
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from aml_app.services.data_service import data_service

def get_alerts(
    status: Optional[str] = None,
    detection_engine: Optional[str] = None,
    min_risk: Optional[float] = None,
    limit: int = 50,
    offset: int = 0
) -> Tuple[pd.DataFrame, int]:
    """Retrieve filtered alerts."""
    return data_service.get_alerts(
        status=status,
        detection_engine=detection_engine,
        min_risk=min_risk,
        limit=limit,
        offset=offset
    )

def get_alert_detail(alert_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve full detail for an individual alert."""
    return data_service.get_alert_detail(alert_id=alert_id)

def update_alert_status(alert_id: int, new_status: str, user_id: str) -> bool:
    """Update workflow status of an alert."""
    return data_service.update_alert_status(alert_id=alert_id, new_status=new_status, user_id=user_id)

def assign_alert(alert_id: int, assigned_to: str, user_id: str) -> bool:
    """Assign an alert to an investigator."""
    return data_service.assign_alert(alert_id=alert_id, assigned_to=assigned_to, user_id=user_id)

def add_alert_comment(alert_id: int, comment_text: str, user_id: str) -> bool:
    """Append an investigation comment."""
    return data_service.add_alert_comment(alert_id=alert_id, comment_text=comment_text, user_id=user_id)
