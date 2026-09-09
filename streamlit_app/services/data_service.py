"""Unified Data Service Facade for AML Investigation Platform.
Routes cleanly to DatabricksRepository in production (Databricks Apps) or LocalRepository in local/test mode.
"""
import os
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from aml_app.config.settings import settings
from aml_app.services.databricks import DatabricksService
from aml_app.services.repository_base import RepositoryBase
from aml_app.services.local_repository import LocalRepository
from aml_app.services.databricks_repository import DatabricksRepository

databricks_service = DatabricksService()

class AMLDataService:
    def __init__(self):
        mode = os.getenv("AML_MODE", "databricks").lower()
        
        # Explicit local override
        if mode == "local":
            self.repo: RepositoryBase = LocalRepository()
        elif settings.is_databricks_app_runtime:
            # Running inside Databricks Apps container: ALWAYS use DatabricksRepository
            self.repo: RepositoryBase = DatabricksRepository(databricks_service)
        elif databricks_service.is_configured():
            # Configured with host & credentials
            self.repo: RepositoryBase = DatabricksRepository(databricks_service)
        else:
            # Offline local developer workstation fallback
            self.repo: RepositoryBase = LocalRepository()

    @property
    def is_cloud_mode(self) -> bool:
        return isinstance(self.repo, DatabricksRepository)

    def get_system_backend_info(self) -> Dict[str, str]:
        return self.repo.get_backend_info()

    def get_discovered_tables(self) -> List[str]:
        if isinstance(self.repo, DatabricksRepository):
            return self.repo.get_available_tables()
        return ["gold_alerts", "gold_transactions", "gold_accounts", "gold_network", "app_alert_status", "app_alert_comments", "app_audit_log"]

    def describe_table(self, table_name: str) -> pd.DataFrame:
        if isinstance(self.repo, DatabricksRepository):
            return self.repo.client.describe_table(table_name)
        return pd.DataFrame([{"col_name": "N/A", "data_type": "N/A", "comment": "Local mode"}])

    def get_sample_rows(self, table_name: str, limit: int = 10) -> pd.DataFrame:
        if isinstance(self.repo, DatabricksRepository):
            return self.repo.client.execute_query(f"SELECT * FROM {settings.DATABRICKS_CATALOG}.{settings.DATABRICKS_SCHEMA}.{table_name} LIMIT {limit}")
        return pd.DataFrame()

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
