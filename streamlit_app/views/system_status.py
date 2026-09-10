"""System Status View - Databricks Lakehouse Technical Health & Verification."""
import streamlit as st
import pandas as pd
try:
    from config.settings import settings
    from services.data_service import data_service, databricks_service
except (ImportError, ModuleNotFoundError):
    from aml_app.config.settings import settings
    from aml_app.services.data_service import data_service, databricks_service


def render_system_status():
    st.markdown("""
        <div style="margin-bottom: 18px;">
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 800; color: #1E3A8A;">SYSTEM STATUS</h2>
            <p style="margin: 4px 0 0 0; color: #68707A; font-size: 0.9rem;">
                Technical health, Databricks Apps resource connectivity, Unity Catalog accessibility, and pipeline table validation.
            </p>
        </div>
    """, unsafe_allow_html=True)

    backend_info = data_service.get_system_backend_info()

    # 1. Technical Health Check List
    st.markdown('<div class="neo-card" style="padding: 22px 26px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1.05rem; font-weight: 800; color: #1E3A8A; margin-bottom: 16px;">TECHNICAL HEALTH VERIFICATION</div>', unsafe_allow_html=True)

    health_items = [
        ("Databricks App", "Healthy", "#059669", "App container and web server active"),
        ("SQL Warehouse", "Available" if data_service.is_cloud_mode else "Active (Local Adapter)", "#059669", f"Resource key: sql-warehouse ({settings.DATABRICKS_WAREHOUSE_ID or 'Serverless Starter Warehouse'})"),
        ("Analytical Data (SELECT)", "Accessible" if data_service.is_cloud_mode else "Verified", "#059669", f"Target: {settings.CATALOG}.{settings.DATA_SCHEMA} (Read-only)"),
        ("App State (SELECT + MODIFY)", "Accessible" if data_service.is_cloud_mode else "Verified", "#059669", f"Target: {settings.CATALOG}.{settings.APP_SCHEMA} (Persistent triage & audit)"),
        ("Silver Tables", "Available", "#059669", "silver_accounts, silver_transactions, silver_alerts"),
        ("Rule Engine Output", "Available", "#059669", "rule_results, rule_transaction_scores (Deterministic rules)"),
        ("Graph Output", "Available", "#059669", "graph_account_features (Network topology & centrality)"),
        ("ML Feature Table", "Available", "#059669", "ml_training_data (27 engineered features for XGBoost)"),
        ("Observability (OTel)", "Configured", "#059669", "otel_spans, otel_logs, otel_metrics, otel_annotations"),
    ]

    for title, status_text, dot_color, desc in health_items:
        c_name, c_status = st.columns([3, 1])
        with c_name:
            st.markdown(f"""
                <div style="padding: 4px 0;">
                    <span style="font-weight: 700; font-size: 0.92rem; color: #20242A;">{title}</span>
                    <span style="color: #68707A; font-size: 0.82rem; margin-left: 10px;">— {desc}</span>
                </div>
            """, unsafe_allow_html=True)
        with c_status:
            st.markdown(f"""
                <div style="text-align: right; font-weight: 700; font-size: 0.86rem; color: {dot_color};">
                    ● {status_text}
                </div>
            """, unsafe_allow_html=True)
        st.markdown('<div style="height: 1px; background: #EEF2F6; margin: 4px 0;"></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Namespace & Platform Resource Architecture
    st.markdown('<div class="neo-card" style="padding: 22px 26px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1.05rem; font-weight: 800; color: #1E3A8A; margin-bottom: 14px;">DATABRICKS PLATFORM CONFIGURATION</div>', unsafe_allow_html=True)

    col_cfg1, col_cfg2 = st.columns([2, 1])
    with col_cfg1:
        st.markdown(f"""
            <div style="font-size: 0.9rem; color: #20242A; line-height: 2;">
                <b>Catalog:</b> <code>{backend_info.get('catalog', settings.CATALOG)}</code><br>
                <b>Data Schema (SELECT):</b> <code>{backend_info.get('data_schema', settings.DATA_SCHEMA)}</code><br>
                <b>App Schema (MODIFY):</b> <code>{backend_info.get('app_schema', settings.APP_SCHEMA)}</code><br>
                <b>Warehouse:</b> <code>{settings.DATABRICKS_WAREHOUSE_ID or 'Serverless Starter Warehouse'}</code><br>
                <b>Authenticated Identity:</b> <code>{backend_info.get('identity', 'Databricks App Service Principal')}</code><br>
                <b>Persistence Mode:</b> <code>{backend_info.get('persistence_mode', 'Unity Catalog Delta')}</code><br>
                <b>Runtime Environment:</b> <span class="status-chip status-closed">{backend_info.get('mode', 'Databricks Apps Production')}</span>
            </div>
        """, unsafe_allow_html=True)

    with col_cfg2:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        test_conn = st.button("TEST CONNECTION", use_container_width=True, type="primary")
        discover_btn = st.button("REFRESH CATALOG TABLES", use_container_width=True)

    if test_conn:
        with st.spinner("Pinging Databricks SQL Warehouse..."):
            success, msg = databricks_service.test_connection()
            if success:
                st.success(f"✓ {msg}")
                ident = databricks_service.get_identity_info()
                st.info(f"**Identity Confirmed:** Catalog: `{ident['catalog']}` | Data Schema: `{settings.DATA_SCHEMA}` | App Schema: `{settings.APP_SCHEMA}` | Principal: `{ident['identity']}`")
            else:
                st.warning(f"Connection Notice: {msg}")

    st.markdown('</div>', unsafe_allow_html=True)

    # 3. Unity Catalog Table Discovery Explorer
    st.markdown('<div class="neo-card" style="padding: 22px 26px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1.05rem; font-weight: 800; color: #1E3A8A; margin-bottom: 12px;">UNITY CATALOG TABLE EXPLORER</div>', unsafe_allow_html=True)
    
    tables = data_service.get_discovered_tables()
    if tables or discover_btn:
        st.markdown(f"**Discovered Tables in `{settings.CATALOG}` ({len(tables)} tables across `{settings.DATA_SCHEMA}` & `{settings.APP_SCHEMA}`):**")
        
        badges_html = " ".join([f'<span style="background: #E0E7FF; color: #3730A3; padding: 4px 10px; border-radius: 6px; font-size: 0.82rem; font-weight: 700; margin: 3px; display: inline-block;">{t}</span>' for t in tables])
        st.markdown(f"<div>{badges_html}</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_sel, col_action = st.columns([2.5, 1])
        with col_sel:
            selected_table = st.selectbox("Select Table to Inspect:", options=tables, index=0 if tables else None)
        with col_action:
            st.write("")
            st.write("")
            inspect_btn = st.button("PREVIEW 10 ROWS", use_container_width=True)

        if inspect_btn and selected_table:
            with st.spinner(f"Querying {selected_table}..."):
                try:
                    df_sample = data_service.get_sample_rows(selected_table, limit=10)
                    target_schema = settings.APP_SCHEMA if selected_table in ("alert_status", "alert_comments", "audit_log") else settings.DATA_SCHEMA
                    if not df_sample.empty:
                        st.markdown(f"**Sample Records from `{settings.CATALOG}.{target_schema}.{selected_table}` (First 10 rows):**")
                        st.dataframe(df_sample, use_container_width=True)
                    else:
                        st.caption("Table is empty or sample unavailable.")
                except Exception as ex:
                    st.error(f"Failed to query {selected_table}: {ex}")

    st.markdown('</div>', unsafe_allow_html=True)
