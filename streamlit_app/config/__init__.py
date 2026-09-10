try:
    from config.settings import settings
except (ImportError, ModuleNotFoundError):
    from aml_app.config.settings import settings

__all__ = ["settings"]
