"""Abstract Base Class for AML Data Repositories.
Enforces a uniform interface across Databricks Unity Catalog and Local Lakehouse backends.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

class RepositoryBase(ABC):

    @abstractmethod
    def get_backend_info(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_kpi_summary(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_alert_trends(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_risk_distribution(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_top_risky_accounts(self, limit: int = 5) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_recent_alerts(self, limit: int = 8) -> pd.DataFrame:
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def get_transaction_details(self, tx_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_alerts(
        self,
        status: Optional[str] = None,
        detection_engine: Optional[str] = None,
        min_risk: Optional[float] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[pd.DataFrame, int]:
        pass

    @abstractmethod
    def get_alert_detail(self, alert_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def update_alert_status(self, alert_id: int, new_status: str, user_id: str) -> bool:
        pass

    @abstractmethod
    def assign_alert(self, alert_id: int, assigned_to: str, user_id: str) -> bool:
        pass

    @abstractmethod
    def add_alert_comment(self, alert_id: int, comment_text: str, user_id: str) -> bool:
        pass

    @abstractmethod
    def get_account_profile(self, account_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_network_graph(self, root_account_id: int, depth: int = 1) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_model_insights(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_audit_trail(self, limit: int = 50, user_filter: Optional[str] = None) -> pd.DataFrame:
        pass

    @abstractmethod
    def global_search(self, term: str) -> List[Dict[str, Any]]:
        pass
