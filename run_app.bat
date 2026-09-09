@echo off
echo Starting AML Transaction Monitoring and Investigation Platform...
if exist streamlit_app\app.py (
    python -m streamlit run streamlit_app/app.py --server.port 8501
) else (
    python -m streamlit run aml_app/app.py --server.port 8501
)
pause
