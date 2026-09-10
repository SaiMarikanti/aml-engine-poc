"""Custom Pure Neumorphic Sidebar Navigation Shell for Databricks AML Platform."""
import streamlit as st
from typing import Dict, Any, Optional

try:
    from config.settings import settings
except (ImportError, ModuleNotFoundError):
    from aml_app.config.settings import settings


def render_sidebar(current_page: Optional[Any] = None, pages_map: Optional[Dict[str, Any]] = None):
    """Render the pure Neumorphic sidebar navigation.
    
    Args:
        current_page: The active st.Page object returned by st.navigation()
        pages_map: Dictionary mapping page titles to st.Page objects
    """
    current_title = getattr(current_page, "title", "Dashboard") if current_page else "Dashboard"
    pages = pages_map or {}

    with st.sidebar:
        # 1. Branding Header - Soft Raised Panel
        st.markdown(f"""
            <div class="neo-sidebar-brand">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div class="neo-sidebar-brand-icon">
                        🛡️
                    </div>
                    <div>
                        <div style="font-size: 1.05rem; font-weight: 800; color: #1E3A8A; letter-spacing: -0.01em; line-height: 1.2;">
                            AML ENGINE
                        </div>
                        <div style="font-size: 0.72rem; color: #64748B; font-weight: 600; letter-spacing: 0.02em;">
                            Lakehouse Intelligence
                        </div>
                    </div>
                </div>
                <div class="neo-sidebar-pill">
                    <span style="color: #1E3A8A; font-weight: 700;">👤 {settings.CURRENT_USER}</span>
                    <span style="color: #059669; font-weight: 700;">● Online</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Helper for rendering page buttons (compatible across Streamlit versions)
        def nav_button(page_title: str, label: str, page_key: str):
            is_active = (current_title == page_title)
            button_type = "primary" if is_active else "secondary"
            target_page = pages.get(page_title)
            
            if st.button(label, key=f"nav_{page_key}", type=button_type, use_container_width=True):
                if target_page is not None:
                    st.switch_page(target_page)

        # Section 1: HOME
        st.markdown('<div class="neo-sidebar-header">HOME</div>', unsafe_allow_html=True)
        nav_button("Dashboard", "📊 Dashboard", "dashboard")

        # Section 2: INVESTIGATION
        st.markdown('<div class="neo-sidebar-groove"></div>', unsafe_allow_html=True)
        st.markdown('<div class="neo-sidebar-header">INVESTIGATION</div>', unsafe_allow_html=True)
        nav_button("Transactions", "💳 Transactions", "transactions")
        nav_button("Alerts", "🚨 Alerts", "alerts")
        nav_button("Accounts", "🏛 Accounts", "accounts")
        nav_button("Network", "🕸 Network", "network")

        # Section 3: INTELLIGENCE
        st.markdown('<div class="neo-sidebar-groove"></div>', unsafe_allow_html=True)
        st.markdown('<div class="neo-sidebar-header">INTELLIGENCE</div>', unsafe_allow_html=True)
        nav_button("Model Insights", "🧠 Model Insights", "model_insights")

        # Section 4: ADMINISTRATION
        st.markdown('<div class="neo-sidebar-groove"></div>', unsafe_allow_html=True)
        st.markdown('<div class="neo-sidebar-header">ADMINISTRATION</div>', unsafe_allow_html=True)
        nav_button("Audit Log", "📜 Audit Log", "audit")
        nav_button("System Status", "⚡ System Status", "system_status")

        # Bottom Widget: Databricks Lakehouse Health Status Plate
        st.markdown(f"""
            <div class="neo-lakehouse-status">
                <div class="brand-title">DATABRICKS PLATFORM</div>
                <div class="neo-status-row">
                    <span style="font-weight: 600; color: #334155;">
                        <span class="neo-status-dot"></span>SQL Warehouse
                    </span>
                    <span style="font-weight: 700; color: #059669;">Online</span>
                </div>
                <div class="neo-status-row">
                    <span style="font-weight: 600; color: #334155;">
                        <span class="neo-status-dot"></span>Unity Catalog
                    </span>
                    <span style="font-weight: 700; color: #1E3A8A;">{settings.CATALOG}</span>
                </div>
                <div class="neo-status-row">
                    <span style="font-weight: 600; color: #334155;">
                        <span class="neo-status-dot"></span>Data Connected
                    </span>
                    <span style="font-weight: 700; color: #059669;">{settings.DATA_SCHEMA}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
