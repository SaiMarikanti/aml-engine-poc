"""AML Transaction Monitoring and Investigation Platform.
Main Application Shell, Navigation Router, and Neumorphic Design System.
"""
import os
import sys
import types

# Ensure app package and directories are on path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Provide namespace aliases for seamless root execution
for pkg_name in ("aml_app", "streamlit_app"):
    if pkg_name not in sys.modules:
        pkg = types.ModuleType(pkg_name)
        pkg.__path__ = [current_dir]
        sys.modules[pkg_name] = pkg

import streamlit as st

# Desktop-first wide layout
st.set_page_config(
    page_title="AML Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------
# Custom global styling
# ---------------------------
css_path = os.path.join(current_dir, "styles", "neumorphism.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------------
# Imports
# ---------------------------
from components.sidebar import render_sidebar
from components.header import render_header

from views.dashboard import render_dashboard
from views.transactions import render_transactions
from views.alerts import render_alerts
from views.accounts import render_accounts
from views.network import render_network
from views.model_insights import render_model_insights
from views.audit import render_audit
from views.system_status import render_system_status

# Initialize persistent session state
if "selected_alert" not in st.session_state:
    st.session_state.selected_alert = None
if "selected_transaction" not in st.session_state:
    st.session_state.selected_transaction = None
if "selected_account" not in st.session_state:
    st.session_state.selected_account = 6976
if "selected_network_account" not in st.session_state:
    st.session_state.selected_network_account = 6976

# ---------------------------
# Define Streamlit pages
# ---------------------------
dashboard = st.Page(
    render_dashboard,
    title="Dashboard",
    icon=":material/dashboard:",
    url_path="dashboard",
    default=True,
)

transactions = st.Page(
    render_transactions,
    title="Transactions",
    icon=":material/payments:",
    url_path="transactions",
)

alerts = st.Page(
    render_alerts,
    title="Alerts",
    icon=":material/notifications_active:",
    url_path="alerts",
)

accounts = st.Page(
    render_accounts,
    title="Accounts",
    icon=":material/person:",
    url_path="accounts",
)

network = st.Page(
    render_network,
    title="Network",
    icon=":material/hub:",
    url_path="network",
)

model_insights = st.Page(
    render_model_insights,
    title="Model Insights",
    icon=":material/monitoring:",
    url_path="model-insights",
)

audit = st.Page(
    render_audit,
    title="Audit Log",
    icon=":material/history:",
    url_path="audit",
)

system_status = st.Page(
    render_system_status,
    title="System Status",
    icon=":material/settings:",
    url_path="system-status",
)

pages_map = {
    "Dashboard": dashboard,
    "Transactions": transactions,
    "Alerts": alerts,
    "Accounts": accounts,
    "Network": network,
    "Model Insights": model_insights,
    "Audit Log": audit,
    "System Status": system_status,
}
st.session_state["_pages_map"] = pages_map

# ---------------------------
# Hide Streamlit navigation
# ---------------------------
pg = st.navigation(
    {
        "HOME": [dashboard],
        "INVESTIGATION": [
            transactions,
            alerts,
            accounts,
            network,
        ],
        "INTELLIGENCE": [
            model_insights,
        ],
        "ADMINISTRATION": [
            audit,
            system_status,
        ],
    },
    position="hidden",
)

# ---------------------------
# Render Header & Sidebar Shell
# ---------------------------
render_header(pages_map)
render_sidebar(pg, pages_map)

# ---------------------------
# Run selected page
# ---------------------------
pg.run()
