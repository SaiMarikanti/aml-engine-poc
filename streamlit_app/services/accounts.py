"""Accounts Domain Service.
Provides business logic and 360-degree profile analysis for customer accounts.
"""
from typing import Any, Dict, Optional
try:
    from services.data_service import data_service
except (ImportError, ModuleNotFoundError):
    from aml_app.services.data_service import data_service


def get_account_profile(account_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve 360-degree account KYC, transaction history, and risk breakdown."""
    return data_service.get_account_profile(account_id=account_id)
