"""Unified Data Service Facade for AML Investigation Platform.
Routes cleanly to DatabricksRepository in production or LocalRepository in local/test mode.
Eliminates architectural inconsistencies and guarantees deterministic calculations.
"""
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from aml_app.services.databricks import DatabricksService
from aml_app.services.repository_base import RepositoryBase
from aml_app.services.local_repository import LocalRepository
from aml_app.services.databricks_repository import DatabricksRepository

databricks_service = DatabricksService()

class AMLDataService:
    def __init__(self):
        if databricks_service.is_configured():
            self.repo: RepositoryBase = DatabricksRepository(databricks_service)
        else:
            self.repo: RepositoryBase = LocalRepository()

    @property
    def is_cloud_mode(self) -> bool:
        return databricks_service.is_configured()

    def get_system_backend_info(self) -> Dict[str, str]:
        return self.repo.get_backend_info()

    def get_kpi_summary(self) -> Dict[str, Any]:
        return self.repo.get_kpi_summary()

    def get_alert_trends(self) -> pd.DataFrame:
        return self.repo.get_alert_trends()

    def get_risk_distribution(self) -> pd.DataFrame:
        return self.repo.get_risk_distribution()

    def get_top_risky_accounts(self, limit: int = 5) -> pd.DataFrame:
        return self.repo.get_top_risky_accounts(limit=limit)

    def get_recent_alerts(self, limit: int = 8) -> pd.DataFrame:
        return self.repo.get_recent_alerts(limit=limit)

    def search_transactions(
        self,
        tx_id: Optional[int] = None,
        sender_id: Optional[int] = None,
        receiver_id: Optional[int] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        is_fraud_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[pd.DataFrame, int]:
        return self.repo.search_transactions(
            tx_id=tx_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            min_amount=min_amount,
            max_amount=max_amount,
            is_fraud_only=is_fraud_only,
            limit=limit,
            offset=offset
        )

    def get_transaction_details(self, tx_id: int) -> Optional[Dict[str, Any]]:
        return self.repo.get_transaction_details(tx_id=tx_id)

    def get_alerts(
        self,
        status: Optional[str] = None,
        detection_engine: Optional[str] = None,
        min_risk: Optional[float] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[pd.DataFrame, int]:
        return self.repo.get_alerts(
            status=status,
            detection_engine=detection_engine,
            min_risk=min_risk,
            limit=limit,
            offset=offset
        )

    def get_alert_detail(self, alert_id: int) -> Optional[Dict[str, Any]]:
        return self.repo.get_alert_detail(alert_id=alert_id)

    def update_alert_status(self, alert_id: int, new_status: str, user_id: str) -> bool:
        return self.repo.update_alert_status(alert_id=alert_id, new_status=new_status, user_id=user_id)

    def assign_alert(self, alert_id: int, assigned_to: str, user_id: str) -> bool:
        return self.repo.assign_alert(alert_id=alert_id, assigned_to=assigned_to, user_id=user_id)

    def add_alert_comment(self, alert_id: int, comment_text: str, user_id: str) -> bool:
        return self.repo.add_alert_comment(alert_id=alert_id, comment_text=comment_text, user_id=user_id)

    def get_account_profile(self, account_id: int) -> Optional[Dict[str, Any]]:
        return self.repo.get_account_profile(account_id=account_id)

    def get_network_graph(self, root_account_id: int, depth: int = 1) -> Dict[str, Any]:
        return self.repo.get_network_graph(root_account_id=root_account_id, depth=depth)

    def get_model_insights(self) -> Dict[str, Any]:
        return self.repo.get_model_insights()

    def get_audit_trail(self, limit: int = 50, user_filter: Optional[str] = None) -> pd.DataFrame:
        return self.repo.get_audit_trail(limit=limit, user_filter=user_filter)

    def global_search(self, term: str) -> List[Dict[str, Any]]:
        return self.repo.global_search(term=term)

data_service = AMLDataService()
