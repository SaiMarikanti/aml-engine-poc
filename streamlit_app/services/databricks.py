"""Databricks SQL Warehouse Connector Service.
Connects via databricks-sql-connector to Unity Catalog tables.
Uses native parameterized queries to eliminate SQL injection vulnerabilities.
"""
import logging
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from aml_app.config.settings import settings

logger = logging.getLogger(__name__)

class DatabricksService:
    def __init__(self):
        self.host = settings.DATABRICKS_HOST
        self.token = settings.DATABRICKS_TOKEN
        self.http_path = settings.DATABRICKS_HTTP_PATH
        self.catalog = settings.DATABRICKS_CATALOG
        self.schema = settings.DATABRICKS_SCHEMA

    def is_configured(self) -> bool:
        """Check if connection credentials are provided."""
        return settings.is_cloud_configured

    def test_connection(self) -> Tuple[bool, str]:
        """Verify connection to Databricks SQL Warehouse."""
        if not self.is_configured():
            return False, "Databricks credentials not configured; running in Local Lakehouse Mode."
        try:
            from databricks import sql
            with sql.connect(
                server_hostname=self.host,
                http_path=self.http_path,
                access_token=self.token,
                catalog=self.catalog,
                schema=self.schema
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1 AS health_check")
                    res = cursor.fetchall()
                    if res:
                        return True, "Connected to Databricks SQL Warehouse successfully."
            return False, "No response from Databricks SQL Warehouse."
        except Exception as e:
            logger.error(f"Databricks connection check failed: {e}")
            return False, f"Connection failed: {str(e)}"

    def execute_query(self, query: str, params: Optional[Dict[str, Any] | Tuple[Any, ...]] = None) -> pd.DataFrame:
        """Execute parameterized SQL query and return a Pandas DataFrame."""
        if not self.is_configured():
            raise RuntimeError("Databricks is not configured.")
        
        from databricks import sql
        try:
            with sql.connect(
                server_hostname=self.host,
                http_path=self.http_path,
                access_token=self.token,
                catalog=self.catalog,
                schema=self.schema
            ) as connection:
                with connection.cursor() as cursor:
                    if params:
                        cursor.execute(query, parameters=params)
                    else:
                        cursor.execute(query)
                    
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    rows = cursor.fetchall()
                    return pd.DataFrame(rows, columns=columns)
        except Exception as e:
            logger.error(f"Databricks SQL Execution error: {e}")
            raise
