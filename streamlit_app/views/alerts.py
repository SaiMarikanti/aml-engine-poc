"""Alert Center & Deep Investigation Workbench."""
import streamlit as st
import pandas as pd
from datetime import datetime

from aml_app.services.data_service import data_service
from aml_app.components.breadcrumbs import render_breadcrumbs
from aml_app.components.alert_card import render_evidence_chip
from aml_app.utils.formatting import format_currency, render_risk_badge, render_status_chip
from aml_app.utils.constants import AlertStatus, DetectionEngine

def render_alerts():
    # Check if an alert is selected for deep investigation
    selected_alert_id = st.session_state.get("selected_alert")
    if selected_alert_id is not None:
        render_alert_investigation(selected_alert_id)
        return

    # Alert Center Work Queue
    st.markdown("""
        <div style="margin-bottom: 18px;">
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 800; color: #1E3A8A;">ALERT CENTER</h2>
            <p style="margin: 4px 0 0 0; color: #68707A; font-size: 0.9rem;">
                Triage queue and active investigation worklist populated by surveillance pipelines.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Filters Card
    st.markdown('<div class="neo-card" style="padding: 16px 20px; margin-bottom: 18px;">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        status_filter = st.selectbox(
            "Filter by Status", 
            ["ALL", "OPEN", "UNDER REVIEW", "CONFIRMED", "FALSE POSITIVE", "CLOSED"]
        )
    with c2:
        engine_filter = st.selectbox(
            "Detection Engine", 
            ["ALL", "Rule Engine", "Graph Analysis", "ML Model (XGBoost)"]
        )
    with c3:
        min_risk = st.slider("Minimum Risk Score", min_value=0.0, max_value=1.0, value=0.0, step=0.05)
    st.markdown('</div>', unsafe_allow_html=True)

    try:
        df_alerts, total = data_service.get_alerts(
            status=status_filter,
            detection_engine=engine_filter,
            min_risk=min_risk if min_risk > 0 else None,
            limit=30,
            offset=0
        )
    except Exception as e:
        st.markdown(f"""
            <div class="neo-warning-compact">
                <b style="color: #92400E;">⚠ Unable to load alerts from Databricks SQL Warehouse: {e}</b>
            </div>
        """, unsafe_allow_html=True)
        df_alerts = pd.DataFrame()
        total = 0

    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-weight: 600; font-size: 0.92rem; color: #4B5563;">
                Showing <b>{len(df_alerts)}</b> of <b>{total:,}</b> surveillance alerts
            </span>
        </div>
    """, unsafe_allow_html=True)

    if df_alerts.empty:
        st.info("No open alerts matching current filter parameters.")
        return

    # Alerts Table
    st.markdown('<div class="neo-card" style="padding: 16px 20px;">', unsafe_allow_html=True)
    st.markdown("""
        <div style="display: grid; grid-template-columns: 1fr 1fr 1.2fr 1.2fr 1.2fr 1fr 1fr 1.1fr; 
                    font-size: 0.78rem; font-weight: 700; color: #68707A; text-transform: uppercase; 
                    border-bottom: 2px solid #D1D5DB; padding-bottom: 8px; margin-bottom: 8px;">
            <div>Alert ID</div>
            <div>TX ID</div>
            <div>Topology Type</div>
            <div>Engine</div>
            <div>Amount (₹)</div>
            <div>Risk</div>
            <div>Status</div>
            <div style="text-align: right;">Action</div>
        </div>
    """, unsafe_allow_html=True)

    for idx, row in df_alerts.iterrows():
        a_id = int(row['ALERT_ID'])
        tx_id = int(row['TX_ID'])
        score = float(row['RISK_SCORE'])
        status = str(row['STATUS'])
        
        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1, 1, 1.2, 1.2, 1.2, 1, 1, 1.1])
        with c1:
            st.markdown(f'<span class="code-pill">AL{a_id}</span>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'TX{tx_id}')
        with c3:
            st.markdown(f'<b>{row["ALERT_TYPE"]}</b>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<span style="font-size: 0.8rem; color: #4B5563;">{row["DETECTION_ENGINE"]}</span>', unsafe_allow_html=True)
        with c5:
            st.markdown(f'₹{row["TX_AMOUNT"]:,.2f}')
        with c6:
            st.markdown(render_risk_badge("CRITICAL" if score >= 0.85 else ("HIGH" if score >= 0.65 else "MED")), unsafe_allow_html=True)
        with c7:
            st.markdown(render_status_chip(status), unsafe_allow_html=True)
        with c8:
            if st.button("Investigate", key=f"btn_investigate_{a_id}_{tx_id}_{idx}", use_container_width=True, type="primary"):
                st.session_state.selected_alert = a_id
                st.rerun()
        st.markdown('<div style="height: 1px; background: #EEF2F6; margin: 4px 0;"></div>', unsafe_allow_html=True)

    # Export button
    csv_data = df_alerts.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="EXPORT ALERTS REPORT (CSV)",
        data=csv_data,
        file_name="aml_alerts_report.csv",
        mime="text/csv"
    )
    st.markdown('</div>', unsafe_allow_html=True)

def render_alert_investigation(alert_id: int):
    """Deep Alert Investigation Workbench."""
    # Top Return / Navigation bar
    col_back, col_trail = st.columns([1, 4])
    with col_back:
        if st.button("← Back to Alert Center", key="back_to_alert_center_btn"):
            st.session_state.selected_alert = None
            st.rerun()
    with col_trail:
        render_breadcrumbs([("Dashboard", "Dashboard"), ("Alert Center", "Alerts"), (f"Alert AL{alert_id}", "")])

    alert = data_service.get_alert_detail(alert_id)
    if not alert:
        st.error(f"Alert AL{alert_id} not found.")
        return

    score = alert.get("RISK_SCORE", 0.90)
    risk_tier = "CRITICAL" if score >= 0.85 else ("HIGH" if score >= 0.65 else "MEDIUM")
    curr_status = alert.get("STATUS", "OPEN")
    assigned_to = alert.get("ASSIGNED_TO", "analyst_1")

    # 1. Prominent Neumorphic Alert Header
    st.markdown(f"""
        <div class="neo-card" style="padding: 22px 26px; border-left: 6px solid {'#991B1B' if risk_tier == 'CRITICAL' else '#DC2626'};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
                        <span style="font-size: 1.8rem; font-weight: 800; color: #1E3A8A;">ALERT AL{alert_id}</span>
                        {render_risk_badge(risk_tier)}
                        {render_status_chip(curr_status)}
                    </div>
                    <div style="font-size: 0.9rem; color: #68707A;">
                        Topology Anomaly: <b style="color: #20242A;">{alert.get('ALERT_TYPE', 'Unknown').upper()}</b> 
                        • Surveillance Step: <b>{alert.get('TIMESTAMP', 0)}</b>
                        • Assignee: <b>{assigned_to}</b>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.78rem; font-weight: 700; color: #68707A; text-transform: uppercase;">Composite Confidence</div>
                    <div style="font-size: 2.4rem; font-weight: 800; color: #DC2626; line-height: 1;">
                        {score:.2f}
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Transaction Summary Row
    st.markdown('<div class="neo-card" style="padding: 20px 24px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 0.95rem; font-weight: 700; color: #1E3A8A; margin-bottom: 14px;">FLAGGED TRANSACTION SUMMARY</div>', unsafe_allow_html=True)
    
    ct1, ct2, ct3, ct4 = st.columns(4)
    with ct1:
        st.markdown(f"""
            <div style="font-size: 0.78rem; color: #68707A;">TRANSACTION ID</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #20242A;">TX{alert['TX_ID']}</div>
        """, unsafe_allow_html=True)
    with ct2:
        st.markdown(f"""
            <div style="font-size: 0.78rem; color: #68707A;">SENDER ACCOUNT</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #20242A;">ACC_{alert['SENDER_ACCOUNT_ID']}</div>
        """, unsafe_allow_html=True)
    with ct3:
        st.markdown(f"""
            <div style="font-size: 0.78rem; color: #68707A;">RECEIVER ACCOUNT</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #20242A;">ACC_{alert['RECEIVER_ACCOUNT_ID']}</div>
        """, unsafe_allow_html=True)
    with ct4:
        st.markdown(f"""
            <div style="font-size: 0.78rem; color: #68707A;">TRANSFER AMOUNT</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #DC2626;">₹{alert['TX_AMOUNT']:,.2f}</div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. Detection Evidence: 3 Physical Cards
    st.markdown('<div class="neo-card" style="padding: 22px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1rem; font-weight: 700; color: #1E3A8A; margin-bottom: 14px;">MULTIVARIATE DETECTION EVIDENCE</div>', unsafe_allow_html=True)
    
    ce1, ce2, ce3 = st.columns(3)
    atype = str(alert.get("ALERT_TYPE", "")).lower()

    with ce1:
        st.markdown("""
            <div class="evidence-card triggered">
                <div style="font-size: 0.76rem; font-weight: 700; color: #DC2626; text-transform: uppercase;">RULE ENGINE</div>
                <div style="font-size: 1.1rem; font-weight: 700; margin: 4px 0;">TRIGGERED</div>
                <div style="font-size: 0.82rem; color: #4B5563;">Deterministic threshold exceeded for high-velocity transfer burst.</div>
            </div>
        """, unsafe_allow_html=True)

    with ce2:
        st.markdown(f"""
            <div class="evidence-card {'triggered' if 'graph' in atype or 'cycle' in atype or 'fan' in atype else ''}">
                <div style="font-size: 0.76rem; font-weight: 700; color: {'#DC2626' if 'graph' in atype or 'cycle' in atype or 'fan' in atype else '#1E3A8A'}; text-transform: uppercase;">GRAPH TOPOLOGY</div>
                <div style="font-size: 1.1rem; font-weight: 700; margin: 4px 0;">{'TRIGGERED' if 'graph' in atype or 'cycle' in atype or 'fan' in atype else 'NORMAL'}</div>
                <div style="font-size: 0.82rem; color: #4B5563;">GraphFrames motifs: {alert.get('ALERT_TYPE', 'Transfer')}.</div>
            </div>
        """, unsafe_allow_html=True)

    with ce3:
        st.markdown(f"""
            <div class="evidence-card triggered">
                <div style="font-size: 0.76rem; font-weight: 700; color: #DC2626; text-transform: uppercase;">ML MODEL (XGBOOST)</div>
                <div style="font-size: 1.1rem; font-weight: 700; margin: 4px 0;">{score:.2f} RISK</div>
                <div style="font-size: 0.82rem; color: #4B5563;">Supervised probability of money laundering pattern.</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. Connected Network Jump Card
    st.markdown('<div class="neo-card" style="padding: 20px 24px;">', unsafe_allow_html=True)
    c_n1, c_n2 = st.columns([3, 1])
    with c_n1:
        st.markdown(f"""
            <div style="font-size: 0.95rem; font-weight: 700; color: #1E3A8A;">COUNTERPARTY GRAPH TOPOLOGY</div>
            <div style="font-size: 0.85rem; color: #4B5563; margin-top: 4px;">
                Direct GraphFrames connection between <b>ACC_{alert['SENDER_ACCOUNT_ID']}</b> ──(₹{alert['TX_AMOUNT']:,.2f})──► <b>ACC_{alert['RECEIVER_ACCOUNT_ID']}</b>
            </div>
        """, unsafe_allow_html=True)
    with c_n2:
        pages_map = st.session_state.get("_pages_map", {})
        if st.button("Open in Network Viewer →", key="btn_open_net_from_alert", use_container_width=True):
            st.session_state.selected_network_account = alert['SENDER_ACCOUNT_ID']
            if "Network" in pages_map:
                st.switch_page(pages_map["Network"])
    st.markdown('</div>', unsafe_allow_html=True)

    # 5. Investigation Workflow & Actions
    st.markdown('<div class="neo-card" style="padding: 22px 26px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1rem; font-weight: 700; color: #1E3A8A; margin-bottom: 14px;">INVESTIGATION DISPOSITION & ACTIONS</div>', unsafe_allow_html=True)
    
    col_act1, col_act2 = st.columns([1, 2])
    with col_act1:
        st.markdown(f"**Current Status:** {render_status_chip(curr_status)}", unsafe_allow_html=True)
        st.markdown(f"**Assigned Investigator:** `{assigned_to}`")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Change Disposition:**")
        c_b1, c_b2, c_b3 = st.columns(3)
        with c_b1:
            if st.button("CONFIRM", key="btn_confirm", use_container_width=True, type="primary"):
                data_service.update_alert_status(alert_id, "CONFIRMED", "analyst_1")
                st.rerun()
        with c_b2:
            if st.button("FALSE POSITIVE", key="btn_fp", use_container_width=True):
                data_service.update_alert_status(alert_id, "FALSE POSITIVE", "analyst_1")
                st.rerun()
        with c_b3:
            if st.button("ESCALATE", key="btn_esc", use_container_width=True):
                data_service.update_alert_status(alert_id, "UNDER REVIEW", "analyst_1")
                st.rerun()

    with col_act2:
        st.markdown("**Add Investigation Audit Note:**")
        note_text = st.text_area("Investigation Note", placeholder="Enter findings, regulatory rationale, or escalation notes...", label_visibility="collapsed")
        if st.button("Save Investigation Note", key="btn_save_note"):
            if note_text.strip():
                data_service.add_alert_comment(alert_id, note_text.strip(), "analyst_1")
                st.success("Note committed to Databricks compliance audit log!")
                st.rerun()

        # Audit History
        comments = alert.get("comments", [])
        if comments:
            st.markdown("<br><b>Prior Case Notes:</b>", unsafe_allow_html=True)
            for c in comments:
                st.markdown(f"""
                    <div style="background: #F4F6F9; border-radius: 8px; padding: 8px 12px; margin-bottom: 6px; font-size: 0.82rem;">
                        <span style="font-weight: 700; color: #1E3A8A;">{c.get('user_id', 'analyst')}</span> 
                        <span style="color: #68707A; font-size: 0.74rem;">({c.get('timestamp', '')})</span>: 
                        {c.get('comment_text', '')}
                    </div>
                """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
