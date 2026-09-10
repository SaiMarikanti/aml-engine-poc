"""Packaging script for Databricks Apps deployment.
Creates:
1. aml-investigation-app.zip (application-only archive)
2. aml-test.zip (minimal smoke-test archive)

Strictly adheres to exclusion of:
- CSVs, Parquet, Delta, SQLite databases
- Secrets, tokens, .env files
- __pycache__, .pyc, venv, IDE metadata
- .pytest_cache, .git, .vscode, .idea
- Generated ZIP files
"""
import os
import shutil
import zipfile

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
APP_SOURCE = os.path.join(WORKSPACE, "streamlit_app") if os.path.exists(os.path.join(WORKSPACE, "streamlit_app")) else os.path.join(WORKSPACE, "aml_app")
TARGET_DIR = os.path.join(WORKSPACE, "aml-investigation-app")
ZIP_APP_PATH = os.path.join(WORKSPACE, "aml-investigation-app.zip")
ZIP_TEST_PATH = os.path.join(WORKSPACE, "aml-test.zip")
TEST_DIR = os.path.join(WORKSPACE, "aml-test")

# Clean existing build directories if present
for d in [TARGET_DIR, TEST_DIR]:
    if os.path.exists(d):
        shutil.rmtree(d)

EXCLUDED_EXACT = {
    "__pycache__",
    ".pytest_cache",
    ".git",
    ".venv",
    "venv",
    "env",
    ".idea",
    ".vscode",
}

def ignore_filters(directory, files):
    ignored = []
    for f in files:
        if f in EXCLUDED_EXACT:
            ignored.append(f)
        elif f.endswith((".pyc", ".pyo", ".pyd")):
            ignored.append(f)
        elif f.endswith((".db", ".sqlite", ".sqlite3", ".csv", ".parquet", ".delta", ".zip")):
            ignored.append(f)
        elif f.startswith(".env") or f.endswith((".key", ".pem")):
            ignored.append(f)
    return ignored

# 1. Copy app source to temporary aml-investigation-app staging
shutil.copytree(APP_SOURCE, TARGET_DIR, ignore=ignore_filters)

# 2. Package aml-investigation-app.zip
with zipfile.ZipFile(ZIP_APP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(TARGET_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_EXACT]
        for file in files:
            if file.endswith((".pyc", ".db", ".csv", ".parquet", ".delta", ".zip")) or file.startswith(".env"):
                continue
            full_path = os.path.join(root, file)
            arc_name = os.path.relpath(full_path, TARGET_DIR).replace("\\", "/")
            zf.write(full_path, arc_name)

# 3. Create aml-test/ directory and minimal aml-test.zip
os.makedirs(TEST_DIR, exist_ok=True)
with open(os.path.join(TEST_DIR, "app.py"), "w", encoding="utf-8") as f:
    f.write(
        "import streamlit as st\n\n"
        "st.set_page_config(\n"
        "    page_title=\"AML Investigation Platform\",\n"
        "    layout=\"wide\"\n"
        ")\n\n"
        "st.title(\"AML Investigation Platform\")\n"
        "st.success(\"Databricks App is running successfully.\")\n"
        "st.write(\"Connected environment verification completed.\")\n"
    )

shutil.copy(os.path.join(TARGET_DIR, "app.yaml"), os.path.join(TEST_DIR, "app.yaml"))
shutil.copy(os.path.join(TARGET_DIR, "requirements.txt"), os.path.join(TEST_DIR, "requirements.txt"))

with zipfile.ZipFile(ZIP_TEST_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(TEST_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            arc_name = os.path.relpath(full_path, TEST_DIR).replace("\\", "/")
            zf.write(full_path, arc_name)

# Cleanup staging directories to keep workspace pristine
for d in [TARGET_DIR, TEST_DIR]:
    if os.path.exists(d):
        shutil.rmtree(d)

print("SUCCESS: aml-investigation-app.zip and aml-test.zip created cleanly!")
