"""Custom Neumorphic Sidebar Navigation Shell for Databricks AML Platform."""
import streamlit as st
from typing import Dict, Any, Optional

def render_sidebar(current_page: Optional[Any] = None, pages_map: Optional[Dict[str, Any]] = None):
    """Render the unified Neumorphic sidebar navigation.
    
    Args:
        current_page: The active st.Page object returned by st.navigation()
        pages_map: Dictionary mapping page titles to st.Page objects
    """
    current_title = getattr(current_page, "title", "Dashboard") if current_page else "Dashboard"
    pages = pages_map or {}

    with st.sidebar:
        # 1. Branding Header
        st.markdown("""
            <div style="padding: 10px 8px 18px 8px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 36px; height: 36px; border-radius: 9px; background: #1E3A8A; 
                                display: flex; align-items: center; justify-content: center; color: white; font-size: 1.15rem; font-weight: 800;
                                box-shadow: 3px 3px 6px #C5CBD4, -3px -3px 6px #FFFFFF;">
                        🛡️
                    </div>
                    <div>
                        <div style="font-size: 1.05rem; font-weight: 800; color: #1E3A8A; letter-spacing: -0.01em; line-height: 1.2;">
                            AML INTELLIGENCE
                        </div>
                        <div style="font-size: 0.72rem; color: #68707A; font-weight: 500; letter-spacing: 0.02em;">
                            Lakehouse Surveillance
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Helper for rendering page buttons
        def nav_button(title: str, icon_label: str, page_key: str):
            is_active = (current_title == title)
            button_type = "primary" if is_active else "secondary"
            target_page = pages.get(title)
            
            if st.button(f"{icon_label}  {title}", key=f"nav_{page_key}", type=button_type, use_container_width=True):
                if target_page is not None:
                    st.switch_page(target_page)

        # Section 1: HOME
        st.markdown('<div class="neo-sidebar-header">HOME</div>', unsafe_allow_html=True)
        nav_button("Dashboard", "◼", "dashboard")

        # Section 2: INVESTIGATION
        st.markdown('<div class="neo-sidebar-header">INVESTIGATION</div>', unsafe_allow_html=True)
        nav_button("Transactions", "▣", "transactions")
        nav_button("Alerts", "!", "alerts")
        nav_button("Accounts", "●", "accounts")
        nav_button("Network", "◈", "network")

        # Section 3: INTELLIGENCE
        st.markdown('<div class="neo-sidebar-header">INTELLIGENCE</div>', unsafe_allow_html=True)
        nav_button("Model Insights", "◫", "model_insights")

        # Section 4: ADMINISTRATION
        st.markdown('<div class="neo-sidebar-header">ADMINISTRATION</div>', unsafe_allow_html=True)
        nav_button("Audit Log", "◇", "audit")
        nav_button("System Status", "⚙", "system_status")

        # Bottom Widget: Databricks Lakehouse Health Status
        st.markdown("""
            <div class="neo-lakehouse-status">
                <div class="brand-title">DATABRICKS LAKEHOUSE</div>
                <div style="margin-top: 6px; display: flex; flex-direction: column; gap: 4px;">
                    <div style="display: flex; align-items: center; gap: 6px; font-weight: 600; color: #059669;">
                        <span style="font-size: 0.7rem;">●</span> SQL Warehouse
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px; font-weight: 600; color: #059669;">
                        <span style="font-size: 0.7rem;">●</span> Data Connected
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
