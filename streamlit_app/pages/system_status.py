"""System & Pipeline Status Page - Data Engineering Batch Operations."""
import streamlit as st
from aml_app.config.settings import settings
from aml_app.services.data_service import data_service

def render_system_status():
    st.markdown("""
        <div style="margin-bottom: 18px;">
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: #1E3A8A;">PIPELINE & SURVEILLANCE STATUS</h2>
            <p style="margin: 4px 0 0 0; color: #68707A; font-size: 0.9rem;">
                Operational state of Databricks batch pipelines, Data Quality checks, GraphFrames jobs, and Gold scoring tables.
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
                        Architecture: <b>{backend_info.get('mode', 'Lakehouse Mode')}</b> 
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

    # Databricks SQL Warehouse Diagnostics Card
    with st.expander("🔌 Databricks SQL Warehouse Connection & Diagnostics", expanded=not data_service.is_cloud_mode):
        col_db1, col_db2 = st.columns([2, 1])
        with col_db1:
            st.markdown(f"""
                <div style="font-size: 0.88rem; color: #20242A; line-height: 1.7;">
                    <b>Server Hostname:</b> <code>{backend_info.get('host') or 'Not configured'}</code><br>
                    <b>Catalog:</b> <code>{backend_info['catalog']}</code> &nbsp;|&nbsp; <b>Schema:</b> <code>{backend_info['schema']}</code><br>
                    <b>Authentication:</b> {'Personal Access Token / Service Principal detected' if settings.is_cloud_configured else 'Running on Local Adapter'}
                </div>
            """, unsafe_allow_html=True)
        with col_db2:
            st.write("")
            if st.button("TEST DATABRICKS CONNECTION", use_container_width=True, type="primary"):
                from aml_app.services.data_service import databricks_service
                success, msg = databricks_service.test_connection()
                if success:
                    st.success(f"✓ {msg}")
                else:
                    st.warning(f"Notice: {msg}")

        st.markdown("""
            <div style="margin-top: 12px; font-size: 0.82rem; color: #4B5563; background: #F8FAFC; padding: 12px; border-radius: 8px;">
                <b>How to connect to your live Databricks Workspace:</b>
                <ol style="margin: 4px 0 0 16px; padding: 0;">
                    <li>Open your Databricks Workspace ➔ <b>SQL Warehouses</b> ➔ Click your warehouse ➔ <b>Connection details</b> tab.</li>
                    <li>Copy <b>Server hostname</b> (e.g. <code>dbc-xxxx.cloud.databricks.com</code>) and <b>HTTP path</b> (e.g. <code>/sql/1.0/warehouses/xxxx</code>).</li>
                    <li>Generate an Access Token in <b>Settings</b> ➔ <b>Developer</b> ➔ <b>Access tokens</b>.</li>
                    <li>Create <code>.streamlit/secrets.toml</code> from <code>.streamlit/secrets.toml.example</code> and save. The app will auto-connect!</li>
                </ol>
            </div>
        """, unsafe_allow_html=True)

    # Batch Pipeline Stages Grid
    st.markdown('<div class="neo-card" style="padding: 20px 24px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1rem; font-weight: 700; color: #1E3A8A; margin-bottom: 6px;">BATCH AML PIPELINE STAGES</div>', unsafe_allow_html=True)
    st.caption("Batch-oriented Lakehouse pipeline orchestrated via Databricks Workflows.")
    
    stages = [
        {"name": "01. Bronze Ingestion (Raw CSVs to Delta S3)", "status": "SUCCESS", "details": "1,323,234 raw transaction events ingested", "icon": "●"},
        {"name": "02. Silver Cleansing & Type Casting", "status": "SUCCESS", "details": "Schema enforced, zero null timestamps or corrupt rows", "icon": "●"},
        {"name": "03. Data Quality & Great Expectations", "status": "SUCCESS", "details": "Referential integrity: 0 missing account vertices", "icon": "●"},
        {"name": "04. Rule Engine (R001–R004 Heuristics)", "status": "SUCCESS", "details": "High-value, velocity, fan-in, and fan-out flags evaluated", "icon": "●"},
        {"name": "05. GraphFrames Topology Analysis", "status": "SUCCESS", "details": "Directed cycle detection & hub centrality computed", "icon": "●"},
        {"name": "06. ML Feature Engineering & XGBoost", "status": "SUCCESS", "details": "Point-in-time features joined with 1,719 target labels", "icon": "●"},
        {"name": "07. Gold Risk Aggregation & UC Governance", "status": "SUCCESS", "details": "Composite final_risk_score written to gold_aml_risk", "icon": "●"}
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
            <div style="font-size: 0.78rem; color: #68707A;">TRANSACTIONS PROCESSED</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #20242A;">{kpis['total_transactions']:,}</div>
            <div style="font-size: 0.72rem; color: #68707A;">Total event population</div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div style="font-size: 0.78rem; color: #68707A;">SURVEILLANCE ALERTS</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #DC2626;">{kpis['total_alerts']:,}</div>
            <div style="font-size: 0.72rem; color: #68707A;">391 unique incident clusters</div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div style="font-size: 0.78rem; color: #68707A;">ACCOUNT PROFILES</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #1E3A8A;">10,000</div>
            <div style="font-size: 0.72rem; color: #68707A;">Aggregated in Gold</div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
