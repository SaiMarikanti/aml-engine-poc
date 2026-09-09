"""System & Pipeline Status Page - Data Engineering Batch Operations & Unity Catalog Diagnostics."""
import streamlit as st
import pandas as pd
from aml_app.config.settings import settings
from aml_app.services.data_service import data_service, databricks_service

def render_system_status():
    st.markdown("""
        <div style="margin-bottom: 18px;">
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: #1E3A8A;">PIPELINE & SURVEILLANCE STATUS</h2>
            <p style="margin: 4px 0 0 0; color: #68707A; font-size: 0.9rem;">
                Operational state of Databricks batch pipelines, Unity Catalog namespace verification, and table schema explorer.
            </p>
        </div>
    """, unsafe_allow_html=True)

    backend_info = data_service.get_system_backend_info()

    # Backend Connection Architecture Banner
    st.markdown(f"""
        <div class="neo-card" style="padding: 20px 24px; border-left: 6px solid {'#059669' if data_service.is_cloud_mode else '#1E3A8A'};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #1E3A8A;">
                        Active Engine: {backend_info['backend']}
                    </h3>
                    <div style="color: #68707A; font-size: 0.88rem; margin-top: 4px;">
                        Architecture: <b>{backend_info.get('mode', 'Databricks Apps Production')}</b> 
                        • Catalog: <code>{backend_info['catalog']}</code> 
                        • Schema: <code>{backend_info['schema']}</code>
                    </div>
                </div>
                <div style="text-align: right;">
                    <span class="status-chip {'status-closed' if data_service.is_cloud_mode else 'status-review'}">
                        ● {backend_info['status']}
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Unity Catalog & SQL Warehouse Live Diagnostics
    st.markdown('<div class="neo-card" style="padding: 20px 24px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1.05rem; font-weight: 700; color: #1E3A8A; margin-bottom: 12px;">UNITY CATALOG & SQL WAREHOUSE DIAGNOSTICS</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.8, 1.2])
    with col1:
        st.markdown(f"""
            <div style="font-size: 0.88rem; color: #20242A; line-height: 1.8;">
                <b>Target Catalog:</b> <code>{settings.DATABRICKS_CATALOG}</code> &nbsp;|&nbsp; <b>Schema:</b> <code>{settings.DATABRICKS_SCHEMA}</code><br>
                <b>Warehouse Resource:</b> <code>{settings.DATABRICKS_WAREHOUSE_ID or 'Serverless Starter Warehouse'}</code><br>
                <b>Authentication:</b> {'Databricks App OAuth Service Principal / Resource Binding' if settings.is_cloud_configured else 'Local Development Adapter'}
            </div>
        """, unsafe_allow_html=True)
    with col2:
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            test_conn = st.button("TEST CONNECTION", use_container_width=True, type="primary")
        with c_btn2:
            discover_btn = st.button("SHOW TABLES", use_container_width=True)

    if test_conn:
        with st.spinner("Connecting to Databricks SQL Warehouse..."):
            success, msg = databricks_service.test_connection()
            if success:
                st.success(f"✓ {msg}")
            else:
                st.warning(f"Connection Notice: {msg}")

    # Live Table Discovery Explorer
    tables = data_service.get_discovered_tables()
    if tables or discover_btn:
        st.markdown("---")
        st.markdown(f"**Discovered Tables in `{settings.DATABRICKS_CATALOG}.{settings.DATABRICKS_SCHEMA}` ({len(tables)} tables total):**")
        
        # Display badges for discovered tables
        badges_html = " ".join([f'<span style="background: #E0E7FF; color: #3730A3; padding: 4px 10px; border-radius: 6px; font-size: 0.82rem; font-weight: 600; margin: 3px; display: inline-block;">{t}</span>' for t in tables])
        st.markdown(f"<div>{badges_html}</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_sel, col_action = st.columns([2, 1])
        with col_sel:
            selected_table = st.selectbox("Select table to inspect schema and live sample data:", options=tables, index=0 if tables else None)
        with col_action:
            st.write("")
            inspect_btn = st.button("PREVIEW 10 ROWS", use_container_width=True)

        if inspect_btn and selected_table:
            with st.spinner(f"Querying {selected_table}..."):
                try:
                    df_sample = data_service.get_sample_rows(selected_table, limit=10)
                    if not df_sample.empty:
                        st.markdown(f"**Sample data from `{settings.DATABRICKS_CATALOG}.{settings.DATABRICKS_SCHEMA}.{selected_table}` (First 10 rows):**")
                        st.dataframe(df_sample, use_container_width=True)
                    else:
                        st.info(f"Table `{selected_table}` is currently empty or returned 0 rows.")
                except Exception as e:
                    st.error(f"Error querying `{selected_table}`: {e}")

    st.markdown("""
        <div style="margin-top: 14px; font-size: 0.82rem; color: #4B5563; background: #F8FAFC; padding: 12px; border-radius: 8px;">
            <b>Databricks Apps Resource Binding:</b><br>
            • In Databricks Workspace ➔ <b>Compute</b> ➔ <b>Apps</b> ➔ Open your App ➔ <b>Resources</b> ➔ Add <b>Serverless Starter Warehouse</b> with permission <code>CAN USE</code> and Resource key <code>sql-warehouse</code>.<br>
            • Databricks automatically injects <code>DATABRICKS_WAREHOUSE_ID</code> and app service principal OAuth credentials into the runtime.
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Batch Pipeline Stages Grid
    st.markdown('<div class="neo-card" style="padding: 20px 24px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1rem; font-weight: 700; color: #1E3A8A; margin-bottom: 6px;">BATCH AML PIPELINE STAGES</div>', unsafe_allow_html=True)
    st.caption(f"Batch-oriented Lakehouse pipeline orchestrated via Databricks Workflows in {settings.DATABRICKS_CATALOG}.{settings.DATABRICKS_SCHEMA}.")
    
    stages = [
        {"name": "01. Bronze Ingestion (Raw CSVs to Delta)", "status": "AVAILABLE", "details": "bronze_accounts, bronze_alerts, bronze_transactions", "icon": "●"},
        {"name": "02. Silver Cleansing & Type Casting", "status": "AVAILABLE", "details": "silver_accounts, silver_transactions validated", "icon": "●"},
        {"name": "03. Data Quality & Checks", "status": "SUCCESS", "details": "Referential integrity and schema checks enforced", "icon": "●"},
        {"name": "04. Rule Engine (R001–R005 Heuristics)", "status": "AVAILABLE", "details": "rule_results, rule_transaction_scores computed", "icon": "●"},
        {"name": "05. GraphFrames Topology Analysis", "status": "AVAILABLE", "details": "graph_results, graph_account_features generated", "icon": "●"},
        {"name": "06. ML Feature Engineering & Scoring", "status": "AVAILABLE", "details": "Features joined with target labels and scored", "icon": "●"},
        {"name": "07. Unity Catalog Governance", "status": "ACTIVE", "details": f"Tables governed under {settings.DATABRICKS_CATALOG}.{settings.DATABRICKS_SCHEMA}", "icon": "●"}
    ]

    c_s1, c_s2 = st.columns(2)
    for i, s in enumerate(stages):
        target_col = c_s1 if i % 2 == 0 else c_s2
        with target_col:
            st.markdown(f"""
                <div style="background: #F1F4F8; border-radius: 10px; padding: 12px 16px; margin-bottom: 10px; 
                            display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 700; font-size: 0.88rem; color: #20242A;">{s['name']}</div>
                        <div style="font-size: 0.78rem; color: #68707A;">{s['details']}</div>
                    </div>
                    <div>
                        <span style="color: #059669; font-weight: 700; font-size: 0.85rem;">{s['icon']} {s['status']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Operational Surveillance Summary
    st.markdown('<div class="neo-card" style="padding: 20px 24px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1rem; font-weight: 700; color: #1E3A8A; margin-bottom: 14px;">SURVEILLANCE OPERATIONS SUMMARY</div>', unsafe_allow_html=True)
    
    kpis = data_service.get_kpi_summary()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div style="font-size: 0.78rem; color: #68707A;">ORCHESTRATION</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #20242A;">Databricks Jobs</div>
            <div style="font-size: 0.72rem; color: #059669;">Daily Scheduled Batch</div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div style="font-size: 0.78rem; color: #68707A;">TOTAL TRANSACTIONS</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #20242A;">{kpis['total_transactions']:,}</div>
            <div style="font-size: 0.72rem; color: #059669;">Batch Synchronized</div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div style="font-size: 0.78rem; color: #68707A;">SECURITY & AUDIT</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #20242A;">Unity Catalog</div>
            <div style="font-size: 0.72rem; color: #059669;">Fine-Grained RBAC</div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div style="font-size: 0.78rem; color: #68707A;">STORAGE LAYER</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #20242A;">Delta Lake S3</div>
            <div style="font-size: 0.72rem; color: #059669;">ACID Reliability</div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
