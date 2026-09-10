"""Databricks SQL Warehouse Connector Service.
Connects via databricks-sql-connector to Unity Catalog tables in aml_engine.aml_poc.
Uses Databricks Apps OAuth credentials provider via Databricks SDK Config and DATABRICKS_WAREHOUSE_ID.
"""
import logging
import os
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

try:
    from databricks import sql
except ImportError:
    sql = None

try:
    from databricks.sdk.core import Config
    cfg = Config()
except Exception as e:
    Config = None
    cfg = None

try:
    from config.settings import settings
except (ImportError, ModuleNotFoundError):
    from aml_app.config.settings import settings


logger = logging.getLogger(__name__)


def get_connection(catalog: Optional[str] = None, schema: Optional[str] = None):
    warehouse_id = os.environ.get("DATABRICKS_WAREHOUSE_ID") or settings.DATABRICKS_WAREHOUSE_ID
    if not warehouse_id:
        raise KeyError("DATABRICKS_WAREHOUSE_ID environment variable not found.")

    server_hostname = cfg.host if (cfg and hasattr(cfg, "host") and cfg.host) else (settings.DATABRICKS_HOST or "")
    if server_hostname:
        server_hostname = server_hostname.replace("https://", "").replace("http://", "").rstrip("/")

    connect_kwargs = {
        "server_hostname": server_hostname,
        "http_path": f"/sql/1.0/warehouses/{warehouse_id}",
    }

    cat = catalog or settings.DATABRICKS_CATALOG
    sch = schema or settings.DATABRICKS_SCHEMA
    if cat:
        connect_kwargs["catalog"] = cat
    if sch:
        connect_kwargs["schema"] = sch

    if cfg:
        connect_kwargs["credentials_provider"] = lambda: cfg.authenticate
    elif settings.DATABRICKS_TOKEN:
        connect_kwargs["access_token"] = settings.DATABRICKS_TOKEN

    return sql.connect(**connect_kwargs)


class DatabricksService:
    def __init__(self):
        self.catalog = settings.DATABRICKS_CATALOG
        self.schema = settings.DATABRICKS_SCHEMA

    def is_configured(self) -> bool:
        """Check if Databricks connection parameters exist or running in Databricks Apps."""
        return bool(
            os.getenv("DATABRICKS_WAREHOUSE_ID")
            or settings.is_cloud_configured
        )

    def _get_connection(self):
        """Build an authenticated databricks.sql connection."""
        return get_connection(catalog=self.catalog, schema=self.schema)

    def test_connection(self) -> Tuple[bool, str]:
        """Verify connection to Databricks SQL Warehouse and return diagnostic status."""
        if not self.is_configured():
            return False, "Databricks parameters not configured; running in local adapter mode."
        try:
            with self._get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT current_catalog() AS catalog, current_schema() AS schema, current_user() AS current_user")
                    row = cursor.fetchone()
                    if row:
                        cat, sch, usr = row[0], row[1], row[2]
                        return True, f"Connected to Databricks SQL Warehouse! Active Namespace: {cat}.{sch} (Identity: {usr})"
            return False, "No response from Databricks SQL Warehouse."
        except Exception as e:
            logger.error(f"Databricks connection check failed: {e}")
            return False, f"Connection failed: {str(e)}"

    def get_identity_info(self) -> Dict[str, str]:
        """Fetch current_catalog(), current_schema(), and current_user() from Databricks."""
        try:
            df = self.execute_query("SELECT current_catalog() AS catalog, current_schema() AS schema, current_user() AS identity")
            if not df.empty:
                return {
                    "catalog": str(df.iloc[0].get("catalog", self.catalog)),
                    "schema": str(df.iloc[0].get("schema", self.schema)),
                    "identity": str(df.iloc[0].get("identity", "Service Principal / User"))
                }
        except Exception as e:
            logger.warning(f"Could not query identity: {e}")
        return {"catalog": self.catalog, "schema": self.schema, "identity": "Unverified"}

    def execute_query(self, query: str, params: Optional[Dict[str, Any] | Tuple[Any, ...]] = None) -> pd.DataFrame:
        """Execute parameterized SQL query and return a Pandas DataFrame."""
        try:
            with self._get_connection() as connection:
                with connection.cursor() as cursor:
                    if params:
                        cursor.execute(query, parameters=params)
                    else:
                        cursor.execute(query)
                    
                    if cursor.description:
                        columns = [desc[0] for desc in cursor.description]
                        rows = cursor.fetchall()
                        return pd.DataFrame(rows, columns=columns)
                    return pd.DataFrame()
        except Exception as e:
            logger.error(f"Databricks SQL Execution error: {e} | Query: {query}")
            raise

    def execute_statement(self, statement: str, params: Optional[Dict[str, Any] | Tuple[Any, ...]] = None) -> bool:
        """Execute DDL/DML statement (CREATE, INSERT, UPDATE, MERGE) without returning a dataframe."""
        try:
            with self._get_connection() as connection:
                with connection.cursor() as cursor:
                    if params:
                        cursor.execute(statement, parameters=params)
                    else:
                        cursor.execute(statement)
            return True
        except Exception as e:
            logger.warning(f"Databricks DDL/DML execution notice: {e} | Statement: {statement}")
            raise

    def get_tables(self) -> List[str]:
        """Discover available tables in aml_engine.aml_poc."""
        try:
            df = self.execute_query(f"SHOW TABLES IN {self.catalog}.{self.schema}")
            if "tableName" in df.columns:
                return df["tableName"].tolist()
            elif "table_name" in df.columns:
                return df["table_name"].tolist()
            elif len(df.columns) > 1:
                return df.iloc[:, 1].tolist()
            return []
        except Exception as e:
            logger.warning(f"Failed to fetch tables: {e}")
            return []

    def describe_table(self, table_name: str) -> pd.DataFrame:
        """Get column schema and types for a table."""
        return self.execute_query(f"DESCRIBE TABLE {self.catalog}.{self.schema}.{table_name}")
