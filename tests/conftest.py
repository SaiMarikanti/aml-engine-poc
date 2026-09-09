"""Pytest configuration and test path setup."""
import os
import sys
import types

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Support both streamlit_app and aml_app directories
streamlit_app_dir = os.path.join(root_dir, "streamlit_app")
aml_app_dir = os.path.join(root_dir, "aml_app")

target_app_dir = streamlit_app_dir if os.path.exists(streamlit_app_dir) else aml_app_dir
if target_app_dir not in sys.path:
    sys.path.insert(0, target_app_dir)

for name in ("aml_app", "streamlit_app"):
    if name not in sys.modules and os.path.exists(target_app_dir):
        mod = types.ModuleType(name)
        mod.__path__ = [target_app_dir]
        sys.modules[name] = mod
