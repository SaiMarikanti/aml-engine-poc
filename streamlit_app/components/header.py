"""Top Application Header for AML Intelligence Platform."""
import streamlit as st
from typing import Dict, Any, Optional
try:
    from config.settings import settings
    from services.data_service import data_service
except (ImportError, ModuleNotFoundError):
    from aml_app.config.settings import settings
    from aml_app.services.data_service import data_service


def render_header(pages_map: Optional[Dict[str, Any]] = None):
    """Render the global top bar with branding, instant surveillance search, and triage badge."""
    pages = pages_map or {}
    
    c_brand, c_search, c_bell = st.columns([1.8, 2.5, 1.2])

    with c_brand:
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px; padding: 2px 0;">
                <div style="width: 38px; height: 38px; border-radius: 10px; background: #1E3A8A; 
                            display: flex; align-items: center; justify-content: center; color: white; font-size: 1.2rem; font-weight: 800;
                            box-shadow: 3px 3px 6px #C5CBD4, -3px -3px 6px #FFFFFF;">
                    🛡️
                </div>
                <div>
                    <div style="font-size: 1.15rem; font-weight: 800; color: #1E3A8A; letter-spacing: -0.01em; line-height: 1.2;">
                        AML INTELLIGENCE
                    </div>
                    <div style="font-size: 0.75rem; color: #68707A; font-weight: 500;">
                        Lakehouse Surveillance
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c_search:
        search_query = st.text_input(
            "Global Surveillance Search",
            placeholder="🔍 Search Transaction / Account / Alert (e.g. TX82, ACC6976, AL193)...",
            label_visibility="collapsed",
            key="global_search_input"
        )
        if search_query:
            matches = data_service.global_search(search_query)
            if matches:
                m = matches[0]
                if m["type"] == "ALERT":
                    st.session_state.selected_alert = m["id"]
                    if "Alerts" in pages:
                        st.switch_page(pages["Alerts"])
                elif m["type"] == "TRANSACTION":
                    st.session_state.selected_transaction = m["id"]
                    if "Transactions" in pages:
                        st.switch_page(pages["Transactions"])
                elif m["type"] == "ACCOUNT":
                    st.session_state.selected_account = m["id"]
                    if "Accounts" in pages:
                        st.switch_page(pages["Accounts"])

    with c_bell:
        st.markdown(f"""
            <div style="text-align: right; padding: 2px 0;">
                <div style="display: inline-flex; align-items: center; gap: 6px; background: #FEF2F2; 
                            border: 1px solid #FECACA; padding: 4px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; color: #991B1B;">
                    🔔 <b>428</b> High-Risk Active
                </div>
                <div style="font-size: 0.72rem; color: #68707A; margin-top: 2px;">
                    User: <b>{settings.CURRENT_USER}</b>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height: 1px; background: #D4DAE2; margin: 10px 0 20px 0;"></div>', unsafe_allow_html=True)
