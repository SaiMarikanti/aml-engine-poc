try:
    from services.data_service import data_service
    from services.databricks import DatabricksService
except (ImportError, ModuleNotFoundError):
    from aml_app.services.data_service import data_service
    from aml_app.services.databricks import DatabricksService


__all__ = ["data_service", "DatabricksService"]
