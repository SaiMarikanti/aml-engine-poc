"""Transactions Domain Service.
Provides business logic and data access for AML transactions.
"""
from typing import Any, Dict, Optional, Tuple
import pandas as pd
from aml_app.services.data_service import data_service

def search_transactions(
    tx_id: Optional[int] = None,
    sender_id: Optional[int] = None,
    receiver_id: Optional[int] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    is_fraud_only: bool = False,
    limit: int = 50,
    offset: int = 0
) -> Tuple[pd.DataFrame, int]:
    """Search and filter transactions with pagination."""
    return data_service.search_transactions(
        tx_id=tx_id,
        sender_id=sender_id,
        receiver_id=receiver_id,
        min_amount=min_amount,
        max_amount=max_amount,
        is_fraud_only=is_fraud_only,
        limit=limit,
        offset=offset
    )

def get_transaction_details(tx_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve detailed metadata and risk context for a transaction."""
    return data_service.get_transaction_details(tx_id=tx_id)
