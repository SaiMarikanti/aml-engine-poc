"""Configuration settings for AML Investigation Platform."""
import os
from dataclasses import dataclass

@dataclass
class Settings:
    APP_NAME: str = "AML Intelligence & Investigation Platform"
    APP_VERSION: str = "2.4.0"
    ENVIRONMENT: str = os.getenv("AML_ENV", "development")
    
    # Databricks SQL Connector settings
    DATABRICKS_HOST: str = os.getenv("DATABRICKS_HOST", "")
    DATABRICKS_TOKEN: str = os.getenv("DATABRICKS_TOKEN", "")
    DATABRICKS_HTTP_PATH: str = os.getenv("DATABRICKS_HTTP_PATH", "")
    DATABRICKS_CATALOG: str = os.getenv("DATABRICKS_CATALOG", "main")
    DATABRICKS_SCHEMA: str = os.getenv("DATABRICKS_SCHEMA", "aml_gold")
    
    # Check st.secrets fallback if running inside Streamlit
    def __post_init__(self):
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "databricks" in st.secrets:
                db_sec = st.secrets["databricks"]
                self.DATABRICKS_HOST = self.DATABRICKS_HOST or db_sec.get("host", "")
                self.DATABRICKS_TOKEN = self.DATABRICKS_TOKEN or db_sec.get("token", "")
                self.DATABRICKS_HTTP_PATH = self.DATABRICKS_HTTP_PATH or db_sec.get("http_path", "")
                self.DATABRICKS_CATALOG = db_sec.get("catalog", self.DATABRICKS_CATALOG)
                self.DATABRICKS_SCHEMA = db_sec.get("schema", self.DATABRICKS_SCHEMA)
        except Exception:
            pass

    @property
    def is_cloud_configured(self) -> bool:
        """True if all 3 connection parameters exist and local mode is not forced."""
        force_local = os.getenv("FORCE_LOCAL_LAKEHOUSE", "false").lower() in ("true", "1", "yes")
        return bool(self.DATABRICKS_HOST and self.DATABRICKS_TOKEN and self.DATABRICKS_HTTP_PATH and not force_local)

    # Local workspace data paths
    DATA_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    WORKSPACE_DIR: str = os.path.dirname(DATA_DIR)
    LOCAL_DB_PATH: str = os.path.join(WORKSPACE_DIR, "aml_lakehouse.db")
    
    TRANSACTIONS_CSV: str = os.path.join(WORKSPACE_DIR, "transactions.csv")
    ALERTS_CSV: str = os.path.join(WORKSPACE_DIR, "alerts.csv")
    ACCOUNTS_CSV: str = os.path.join(WORKSPACE_DIR, "accounts.csv")
    
    # Current Investigator
    CURRENT_USER: str = os.getenv("AML_CURRENT_USER", "analyst_1")
    CURRENT_USER_ROLE: str = os.getenv("AML_CURRENT_ROLE", "Senior Financial Crime Investigator")

settings = Settings()
