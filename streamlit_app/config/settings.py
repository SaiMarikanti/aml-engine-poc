"""Configuration settings for AML Investigation Platform.
Calibrated for Databricks Apps runtime, Unity Catalog (aml_engine.aml_poc), and Serverless SQL Warehouse.
"""
import os
from dataclasses import dataclass

@dataclass
class Settings:
    APP_NAME: str = "AML Intelligence & Investigation Platform"
    APP_VERSION: str = "2.5.0"
    ENVIRONMENT: str = os.getenv("AML_ENV", "production")
    
    # Target Unity Catalog & Schemas
    CATALOG: str = os.getenv("DATABRICKS_CATALOG", "aml_engine")
    DATA_SCHEMA: str = os.getenv("DATABRICKS_DATA_SCHEMA", os.getenv("DATABRICKS_SCHEMA", "aml_poc"))
    APP_SCHEMA: str = os.getenv("DATABRICKS_APP_SCHEMA", "aml_app")

    # Backward compatibility aliases
    DATABRICKS_CATALOG: str = CATALOG
    DATABRICKS_SCHEMA: str = DATA_SCHEMA
    DATABRICKS_DATA_SCHEMA: str = DATA_SCHEMA
    DATABRICKS_APP_SCHEMA: str = APP_SCHEMA
    
    # Databricks SQL Warehouse Resource settings
    DATABRICKS_WAREHOUSE_ID: str = os.getenv("DATABRICKS_WAREHOUSE_ID", "")
    DATABRICKS_HOST: str = os.getenv("DATABRICKS_HOST", "")
    DATABRICKS_TOKEN: str = os.getenv("DATABRICKS_TOKEN", "")
    DATABRICKS_HTTP_PATH: str = os.getenv("DATABRICKS_HTTP_PATH", "")

    # Mode: "databricks" (default for Databricks Apps) or "local" (for offline unit tests)
    AML_MODE: str = os.getenv("AML_MODE", "databricks")

    def __post_init__(self):
        # Resolve HTTP path from resource-backed DATABRICKS_WAREHOUSE_ID if HTTP path is not explicit
        if not self.DATABRICKS_HTTP_PATH and self.DATABRICKS_WAREHOUSE_ID:
            self.DATABRICKS_HTTP_PATH = f"/sql/1.0/warehouses/{self.DATABRICKS_WAREHOUSE_ID}"

    @property
    def is_databricks_app_runtime(self) -> bool:
        """True if running inside Databricks Apps container."""
        return bool(
            os.getenv("DATABRICKS_APP_NAME") or
            os.getenv("DATABRICKS_WAREHOUSE_ID") or
            os.getenv("DATABRICKS_RUNTIME_VERSION") or
            os.path.exists("/app/python")
        )

    @property
    def is_cloud_configured(self) -> bool:
        """True if Databricks connection parameters exist or running in Databricks Apps."""
        force_local = os.getenv("FORCE_LOCAL_LAKEHOUSE", "false").lower() in ("true", "1", "yes")
        if force_local or self.AML_MODE == "local":
            return False
        if self.is_databricks_app_runtime:
            return True
        return bool(self.DATABRICKS_HOST and (self.DATABRICKS_TOKEN or self.is_databricks_app_runtime) and (self.DATABRICKS_HTTP_PATH or self.DATABRICKS_WAREHOUSE_ID))

    # Local workspace data paths (only used in local testing mode)
    DATA_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    WORKSPACE_DIR: str = os.path.dirname(DATA_DIR)
    LOCAL_DB_PATH: str = os.path.join(WORKSPACE_DIR, "aml_lakehouse.db")
    TRANSACTIONS_CSV: str = os.path.join(WORKSPACE_DIR, "transactions.csv")
    ALERTS_CSV: str = os.path.join(WORKSPACE_DIR, "alerts.csv")
    ACCOUNTS_CSV: str = os.path.join(WORKSPACE_DIR, "accounts.csv")
    
    # Current Investigator Identity
    CURRENT_USER: str = os.getenv("AML_CURRENT_USER", "analyst_1")
    CURRENT_USER_ROLE: str = os.getenv("AML_CURRENT_ROLE", "Senior Financial Crime Investigator")

settings = Settings()
