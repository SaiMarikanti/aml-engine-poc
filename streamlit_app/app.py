"""AML Transaction Monitoring and Investigation Platform.
Main Streamlit Application Shell, Routing, and Neumorphic Design System.
"""
import os
import sys

# Ensure app package and directories are on path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Provide namespace aliases for seamless root execution
import types
for pkg_name in ("aml_app", "streamlit_app"):
    if pkg_name not in sys.modules:
        pkg = types.ModuleType(pkg_name)
        pkg.__path__ = [current_dir]
        sys.modules[pkg_name] = pkg

import streamlit as st

# Set Desktop-first wide layout
st.set_page_config(
    page_title="AML Intelligence & Investigation Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
css_path = os.path.join(current_dir, "styles", "neumorphism.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from aml_app.config.settings import settings
from aml_app.services.data_service import data_service
from aml_app.pages import (
    render_dashboard,
    render_transactions,
    render_alerts,
    render_accounts,
    render_network,
    render_model_insights,
    render_audit,
    render_system_status
)

# Initialize Session State
if "nav_section" not in st.session_state:
    st.session_state.nav_section = "Dashboard"
if "selected_alert" not in st.session_state:
    st.session_state.selected_alert = None
if "selected_transaction" not in st.session_state:
    st.session_state.selected_transaction = None
if "selected_account" not in st.session_state:
    st.session_state.selected_account = 6976
if "selected_network_account" not in st.session_state:
    st.session_state.selected_network_account = 6976

# -------------------------------------------------------------
# TOP APP BAR (GLOBAL SEARCH & NOTIFICATIONS)
# -------------------------------------------------------------
c_brand, c_search, c_bell = st.columns([1.8, 2.5, 1.2])

with c_brand:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; padding: 4px 0;">
            <div style="width: 38px; height: 38px; border-radius: 10px; background: #1E3A8A; 
                        display: flex; align-items: center; justify-content: center; color: white; font-size: 1.2rem; font-weight: 800;">
                🛡️
            </div>
            <div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #1E3A8A; letter-spacing: -0.01em;">
                    AML INTELLIGENCE
                </div>
                <div style="font-size: 0.75rem; color: #68707A; font-weight: 500;">
                    Databricks Lakehouse Surveillance
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with c_search:
    search_query = st.text_input(
        "Global Surveillance Search",
        placeholder="🔍 Search Transaction / Account / Alert (e.g. TX82, ACC6976, AL193)...",
        label_visibility="collapsed"
    )
    if search_query:
        matches = data_service.global_search(search_query)
        if matches:
            m = matches[0]
            if m["type"] == "ALERT":
                st.session_state.selected_alert = m["id"]
                st.session_state.nav_section = "Alerts"
            elif m["type"] == "TRANSACTION":
                st.session_state.selected_transaction = m["id"]
                st.session_state.nav_section = "Transactions"
            elif m["type"] == "ACCOUNT":
                st.session_state.selected_account = m["id"]
                st.session_state.nav_section = "Accounts"
            st.rerun()

with c_bell:
    st.markdown(f"""
        <div style="text-align: right; padding: 4px 0;">
            <div style="display: inline-flex; align-items: center; gap: 6px; background: #FEF2F2; 
                        border: 1px solid #FECACA; padding: 4px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; color: #991B1B;">
                🔔 <b>428</b> High-Risk Active
            </div>
            <div style="font-size: 0.72rem; color: #68707A; margin-top: 2px;">
                User: <b>{settings.CURRENT_USER}</b>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div style="height: 1px; background: #D8DFE8; margin: 12px 0 20px 0;"></div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# PERMANENT LEFT SIDEBAR NAVIGATION
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="padding: 10px 12px 16px 12px;">
            <div style="font-size: 0.72rem; font-weight: 700; color: #68707A; text-transform: uppercase; letter-spacing: 0.08em;">
                INVESTIGATOR WORKSPACE
            </div>
            <div style="font-size: 1rem; font-weight: 800; color: #1E3A8A; margin-top: 2px;">
                FINCRIM CONTROL
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Section 1: HOME
    st.markdown('<div class="neo-nav-header">HOME</div>', unsafe_allow_html=True)
    if st.button("📊 Dashboard", use_container_width=True, type="primary" if st.session_state.nav_section == "Dashboard" else "secondary"):
        st.session_state.nav_section = "Dashboard"
        st.rerun()

    # Section 2: INVESTIGATION
    st.markdown('<div class="neo-nav-header">INVESTIGATION</div>', unsafe_allow_html=True)
    if st.button("💳 Transactions", use_container_width=True, type="primary" if st.session_state.nav_section == "Transactions" else "secondary"):
        st.session_state.nav_section = "Transactions"
        st.session_state.selected_transaction = None
        st.rerun()
    if st.button("🚨 Alerts", use_container_width=True, type="primary" if st.session_state.nav_section == "Alerts" else "secondary"):
        st.session_state.nav_section = "Alerts"
        st.session_state.selected_alert = None
        st.rerun()
    if st.button("👤 Accounts", use_container_width=True, type="primary" if st.session_state.nav_section == "Accounts" else "secondary"):
        st.session_state.nav_section = "Accounts"
        st.rerun()
    if st.button("🕸️ Network", use_container_width=True, type="primary" if st.session_state.nav_section == "Network" else "secondary"):
        st.session_state.nav_section = "Network"
        st.rerun()

    # Section 3: INTELLIGENCE
    st.markdown('<div class="neo-nav-header">INTELLIGENCE</div>', unsafe_allow_html=True)
    if st.button("📈 Model Insights", use_container_width=True, type="primary" if st.session_state.nav_section == "Model Insights" else "secondary"):
        st.session_state.nav_section = "Model Insights"
        st.rerun()

    # Section 4: ADMINISTRATION
    st.markdown('<div class="neo-nav-header">ADMINISTRATION</div>', unsafe_allow_html=True)
    if st.button("📝 Audit Log", use_container_width=True, type="primary" if st.session_state.nav_section == "Audit Log" else "secondary"):
        st.session_state.nav_section = "Audit Log"
        st.rerun()
    if st.button("⚙️ System Status", use_container_width=True, type="primary" if st.session_state.nav_section == "System Status" else "secondary"):
        st.session_state.nav_section = "System Status"
        st.rerun()

    st.markdown('<div style="height: 30px;"></div>', unsafe_allow_html=True)
    st.markdown("""
        <div style="background: #D9E1E8; padding: 12px; border-radius: 10px; font-size: 0.75rem; color: #4B5563;">
            <div style="font-weight: 700; color: #1E3A8A;">Databricks Lakehouse</div>
            <div>Delta Gold Analytics Ready</div>
            <div style="margin-top: 4px; color: #059669; font-weight: 600;">● SQL Warehouse Active</div>
        </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# PAGE ROUTING
# -------------------------------------------------------------
current_page = st.session_state.nav_section

if current_page == "Dashboard":
    render_dashboard()
elif current_page == "Transactions":
    render_transactions()
elif current_page == "Alerts":
    render_alerts()
elif current_page == "Accounts":
    render_accounts()
elif current_page == "Network":
    render_network()
elif current_page == "Model Insights":
    render_model_insights()
elif current_page == "Audit Log":
    render_audit()
elif current_page == "System Status":
    render_system_status()
else:
    render_dashboard()
