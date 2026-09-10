"""Network Domain Service.
Provides multi-hop transaction topology and graph risk metrics for accounts.
"""
from typing import Any, Dict
try:
    from services.data_service import data_service
except (ImportError, ModuleNotFoundError):
    from aml_app.services.data_service import data_service


def get_network_graph(root_account_id: int, depth: int = 1) -> Dict[str, Any]:
    """Extract ego-network subgraph for an account up to the specified degree of separation."""
    return data_service.get_network_graph(root_account_id=root_account_id, depth=depth)
