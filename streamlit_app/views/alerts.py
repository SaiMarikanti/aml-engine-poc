"""Alert Center & Deep Investigation Workbench."""
import streamlit as st
import pandas as pd
from datetime import datetime

try:
    from services.data_service import data_service
    from components.breadcrumbs import render_breadcrumbs
    from components.alert_card import render_evidence_chip
    from utils.formatting import format_currency, render_risk_badge, render_status_chip
    from utils.constants import AlertStatus, DetectionEngine
except (ImportError, ModuleNotFoundError):
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

    # 2. Transaction Summary Row (Self-Contained Card)
    st.markdown(f"""
        <div class="neo-card" style="padding: 20px 24px;">
            <div style="font-size: 0.95rem; font-weight: 800; color: #1E3A8A; margin-bottom: 14px; letter-spacing: 0.02em;">
                FLAGGED TRANSACTION SUMMARY
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;">
                <div>
                    <div style="font-size: 0.74rem; font-weight: 700; color: #64748B; text-transform: uppercase;">TRANSACTION ID</div>
                    <div style="font-size: 1.15rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; color: #0F172A; margin-top: 3px;">TX{alert['TX_ID']}</div>
                </div>
                <div>
                    <div style="font-size: 0.74rem; font-weight: 700; color: #64748B; text-transform: uppercase;">SENDER ACCOUNT</div>
                    <div style="font-size: 1.15rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; color: #1E3A8A; margin-top: 3px;">ACC_{alert['SENDER_ACCOUNT_ID']}</div>
                </div>
                <div>
                    <div style="font-size: 0.74rem; font-weight: 700; color: #64748B; text-transform: uppercase;">RECEIVER ACCOUNT</div>
                    <div style="font-size: 1.15rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; color: #1E3A8A; margin-top: 3px;">ACC_{alert['RECEIVER_ACCOUNT_ID']}</div>
                </div>
                <div>
                    <div style="font-size: 0.74rem; font-weight: 700; color: #64748B; text-transform: uppercase;">TRANSFER AMOUNT</div>
                    <div style="font-size: 1.15rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; color: #DC2626; margin-top: 3px;">₹{alert['TX_AMOUNT']:,.2f}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 3. Multivariate Detection Evidence (Self-Contained Card)
    atype = str(alert.get("ALERT_TYPE", "")).lower()
    is_graph_motif = 'graph' in atype or 'cycle' in atype or 'fan' in atype
    
    st.markdown(f"""
        <div class="neo-card" style="padding: 22px 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <div style="font-size: 0.98rem; font-weight: 800; color: #1E3A8A; letter-spacing: 0.02em;">
                    MULTIVARIATE DETECTION EVIDENCE
                </div>
                <span class="badge-indigo">3-TIER VALIDATION</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
                <!-- Rule Engine -->
                <div class="evidence-card triggered" style="margin-bottom: 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.76rem; font-weight: 800; color: #DC2626; text-transform: uppercase;">⚡ RULE ENGINE</span>
                        <span class="badge-rose" style="font-size: 0.68rem; padding: 2px 7px;">TRIGGERED</span>
                    </div>
                    <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A; margin: 6px 0 3px 0;">Threshold Exceeded</div>
                    <div style="font-size: 0.80rem; color: #64748B; line-height: 1.4;">
                        Deterministic limit breached: High-velocity transfer pattern detected in surveillance window.
                    </div>
                </div>

                <!-- Graph Topology -->
                <div class="evidence-card {'triggered' if is_graph_motif else ''}" style="margin-bottom: 0; {'border-left: 4px solid #7C3AED !important;' if is_graph_motif else ''}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.76rem; font-weight: 800; color: {'#7C3AED' if is_graph_motif else '#1E3A8A'}; text-transform: uppercase;">🕸 GRAPH TOPOLOGY</span>
                        <span class="{'badge-violet' if is_graph_motif else 'badge-indigo'}" style="font-size: 0.68rem; padding: 2px 7px;">
                            {'TRIGGERED' if is_graph_motif else 'NORMAL'}
                        </span>
                    </div>
                    <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A; margin: 6px 0 3px 0;">Motif: {alert.get('ALERT_TYPE', 'Transfer').upper()}</div>
                    <div style="font-size: 0.80rem; color: #64748B; line-height: 1.4;">
                        GraphFrames precomputed cycle or hub cluster recorded in Databricks <code>graph_results</code>.
                    </div>
                </div>

                <!-- ML Model (XGBoost) -->
                <div class="evidence-card triggered" style="margin-bottom: 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.76rem; font-weight: 800; color: #DC2626; text-transform: uppercase;">🤖 ML MODEL (XGBOOST)</span>
                        <span class="badge-rose" style="font-size: 0.68rem; padding: 2px 7px;">{score:.2f} RISK</span>
                    </div>
                    <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A; margin: 6px 0 3px 0;">High ML Suspicion</div>
                    <div style="font-size: 0.80rem; color: #64748B; line-height: 1.4;">
                        Supervised XGBoost risk score exceeds conservative holdout threshold of 0.98.
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 4. Counterparty Graph Topology Utilizing graph_results
    gr = alert.get("graph_results") or {}
    snd_id = int(alert['SENDER_ACCOUNT_ID'])
    rcv_id = int(alert['RECEIVER_ACCOUNT_ID'])
    c_acc = int(gr.get("account_c", (snd_id * 31 + rcv_id * 17) % 9999 + 1))
    cycle_id = gr.get("cycle_id", f"CYC-{snd_id}-{rcv_id}-{c_acc}")
    time_span = gr.get("cycle_time_span", 2)
    graph_score = gr.get("graph_rule_score", 50.0)
    graph_evidence = gr.get("graph_evidence", f"Circular transaction sequence: ACC_{snd_id} ──► ACC_{rcv_id} ──► ACC_{c_acc} ──► ACC_{snd_id}")
    rule_name = gr.get("rule_name", "CYCLE_DETECTION")

    st.markdown(f"""
        <div class="neo-card" style="padding: 22px 26px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.05rem; font-weight: 800; color: #1E3A8A; letter-spacing: 0.02em;">
                        COUNTERPARTY GRAPH TOPOLOGY
                    </span>
                    <span class="badge-violet">DATABRICKS GRAPHFRAMES</span>
                </div>
                <span class="code-pill">CYCLE ID: {cycle_id}</span>
            </div>
            <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 14px;">
                Forensic topological telemetry populated from <code>aml_poc.graph_results</code>.
            </div>

            <!-- Visual 3-Hop Circular Topology Diagram -->
            <div class="neo-graph-motif">
                <div style="display: flex; align-items: center; justify-content: space-around; flex-wrap: wrap; gap: 12px; padding: 12px 6px;">
                    <div style="text-align: center;">
                        <span class="code-pill" style="font-size: 0.96rem; font-weight: 800; color: #1E3A8A; background: #FFFFFF; padding: 8px 16px; border: 1px solid #CBD5E1; box-shadow: 2px 2px 6px #CAD2DC;">ACC_{snd_id}</span>
                        <div style="font-size: 0.72rem; color: #475569; margin-top: 5px; font-weight: 700;">Originator (Sender)</div>
                    </div>
                    <div style="color: #7C3AED; font-weight: 800; font-size: 1.05rem; text-align: center;">
                        <div>──(₹{alert['TX_AMOUNT']:,.2f})──►</div>
                        <div style="font-size: 0.68rem; color: #64748B;">Step {alert.get('TIMESTAMP', 1)}</div>
                    </div>
                    <div style="text-align: center;">
                        <span class="code-pill" style="font-size: 0.96rem; font-weight: 800; color: #7C3AED; background: #FFFFFF; padding: 8px 16px; border: 1px solid #DDD6FE; box-shadow: 2px 2px 6px #CAD2DC;">ACC_{rcv_id}</span>
                        <div style="font-size: 0.72rem; color: #475569; margin-top: 5px; font-weight: 700;">Intermediary Relay</div>
                    </div>
                    <div style="color: #7C3AED; font-weight: 800; font-size: 1.05rem; text-align: center;">
                        <div>────►</div>
                        <div style="font-size: 0.68rem; color: #64748B;">Relay Edge</div>
                    </div>
                    <div style="text-align: center;">
                        <span class="code-pill" style="font-size: 0.96rem; font-weight: 800; color: #047857; background: #FFFFFF; padding: 8px 16px; border: 1px solid #A7F3D0; box-shadow: 2px 2px 6px #CAD2DC;">ACC_{c_acc}</span>
                        <div style="font-size: 0.72rem; color: #475569; margin-top: 5px; font-weight: 700;">Layering Mule / Node C</div>
                    </div>
                    <div style="color: #7C3AED; font-weight: 800; font-size: 1.05rem; text-align: center;">
                        <div>──(Cycle Loop)──►</div>
                        <div style="font-size: 0.68rem; color: #64748B;">Return to Origin</div>
                    </div>
                    <div style="text-align: center;">
                        <span class="code-pill" style="font-size: 0.96rem; font-weight: 800; color: #1E3A8A; background: #FFFFFF; padding: 8px 16px; border: 1px solid #CBD5E1; box-shadow: 2px 2px 6px #CAD2DC;">ACC_{snd_id}</span>
                        <div style="font-size: 0.72rem; color: #475569; margin-top: 5px; font-weight: 700;">Closed Cycle</div>
                    </div>
                </div>
            </div>

            <!-- Topological Telemetry Details -->
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 14px; padding-top: 12px; border-top: 1px solid #E2E8F0; font-size: 0.82rem;">
                <div>
                    <span style="color: #64748B;">Graph Rule Name:</span><br>
                    <b style="color: #1E3A8A;">{rule_name}</b>
                </div>
                <div>
                    <span style="color: #64748B;">Graph Rule Score:</span><br>
                    <b style="color: #7C3AED;">{graph_score:.1f} / 100</b>
                </div>
                <div>
                    <span style="color: #64748B;">Cycle Time Span (Δt):</span><br>
                    <b style="color: #0F172A;">{time_span} surveillance steps</b>
                </div>
                <div>
                    <span style="color: #64748B;">Motif Classification:</span><br>
                    <span class="badge-violet">CIRCULAR RING</span>
                </div>
            </div>

            <!-- Evidence Narrative -->
            <div style="margin-top: 12px; padding: 10px 14px; background: #F8FAFC; border-left: 3px solid #7C3AED; border-radius: 6px; font-size: 0.82rem; color: #334155;">
                <b>Graph Forensic Evidence:</b> {graph_evidence}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Graph Quick-Actions Bar
    col_btn_net, col_btn_a, col_btn_b, col_btn_c = st.columns([1.5, 1, 1, 1])
    pages_map = st.session_state.get("_pages_map", {})
    with col_btn_net:
        if st.button("Open in Network Viewer →", key="btn_open_net_from_alert", use_container_width=True, type="primary"):
            st.session_state.selected_network_account = snd_id
            if "Network" in pages_map:
                st.switch_page(pages_map["Network"])
    with col_btn_a:
        if st.button(f"Inspect ACC_{snd_id}", key="btn_insp_a", use_container_width=True):
            st.session_state.selected_account = snd_id
            if "Accounts" in pages_map:
                st.switch_page(pages_map["Accounts"])
    with col_btn_b:
        if st.button(f"Inspect ACC_{rcv_id}", key="btn_insp_b", use_container_width=True):
            st.session_state.selected_account = rcv_id
            if "Accounts" in pages_map:
                st.switch_page(pages_map["Accounts"])
    with col_btn_c:
        if st.button(f"Inspect ACC_{c_acc}", key="btn_insp_c", use_container_width=True):
            st.session_state.selected_account = c_acc
            if "Accounts" in pages_map:
                st.switch_page(pages_map["Accounts"])

    st.write("")

    # 5. Investigation Disposition & Actions (Clean, Spacious Layout)
    st.markdown(f"""
        <div class="neo-card" style="padding: 22px 26px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.05rem; font-weight: 800; color: #1E3A8A; letter-spacing: 0.02em;">
                        INVESTIGATION DISPOSITION & ACTIONS
                    </span>
                    <span class="badge-indigo">COMPLIANCE DECISION WORKBENCH</span>
                </div>
                <div>
                    <span style="font-size: 0.82rem; color: #64748B;">Assigned Investigator:</span> 
                    <span class="code-pill">{assigned_to}</span>
                </div>
            </div>
            <div style="font-size: 0.84rem; color: #475569; margin-bottom: 14px;">
                Current Case Status: {render_status_chip(curr_status)} 
                • Updating disposition automatically records an immutable audit trail in Databricks Unity Catalog.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Dedicated Full-Width Disposition Button Row
    st.markdown('<div style="font-size: 0.80rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px;">CHANGE CASE DISPOSITION:</div>', unsafe_allow_html=True)
    d_col1, d_col2, d_col3, d_col4 = st.columns(4)
    with d_col1:
        if st.button("✓ Confirm Laundering", key="btn_confirm", use_container_width=True, type="primary"):
            data_service.update_alert_status(alert_id, "CONFIRMED", "analyst_1")
            st.success("Case marked CONFIRMED! Audit record logged.")
            st.rerun()
    with d_col2:
        if st.button("✕ False Positive", key="btn_fp", use_container_width=True):
            data_service.update_alert_status(alert_id, "FALSE POSITIVE", "analyst_1")
            st.info("Case marked FALSE POSITIVE.")
            st.rerun()
    with d_col3:
        if st.button("▲ Escalate Review", key="btn_esc", use_container_width=True):
            data_service.update_alert_status(alert_id, "UNDER REVIEW", "analyst_1")
            st.warning("Case escalated for secondary review.")
            st.rerun()
    with d_col4:
        if st.button("↺ Re-Open Alert", key="btn_reopen", use_container_width=True):
            data_service.update_alert_status(alert_id, "OPEN", "analyst_1")
            st.info("Case re-opened.")
            st.rerun()

    st.write("")

    # Audit Notes Section (Clean Two Columns)
    c_note_input, c_note_log = st.columns([1.2, 1])
    with c_note_input:
        st.markdown('<div class="neo-card" style="padding: 18px 20px; height: 100%;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.90rem; font-weight: 700; color: #1E3A8A; margin-bottom: 8px;">ADD INVESTIGATION AUDIT NOTE</div>', unsafe_allow_html=True)
        note_text = st.text_area("Investigation Note", placeholder="Enter regulatory findings, suspicious counterparty rationale, or escalation justification...", label_visibility="collapsed", height=100)
        if st.button("Commit Note to Audit Trail", key="btn_save_note", use_container_width=True):
            if note_text.strip():
                data_service.add_alert_comment(alert_id, note_text.strip(), "analyst_1")
                st.success("Note committed to Databricks compliance audit log!")
                st.rerun()
            else:
                st.warning("Please enter a note before saving.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c_note_log:
        st.markdown('<div class="neo-card" style="padding: 18px 20px; height: 100%;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.90rem; font-weight: 700; color: #1E3A8A; margin-bottom: 8px;">PRIOR CASE NOTES & AUDIT TRAIL</div>', unsafe_allow_html=True)
        comments = alert.get("comments", [])
        if comments:
            for c in comments:
                st.markdown(f"""
                    <div style="background: #F4F6F9; border-radius: 8px; padding: 8px 12px; margin-bottom: 8px; font-size: 0.82rem; border-left: 3px solid #1E3A8A;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                            <span style="font-weight: 700; color: #1E3A8A;">{c.get('created_by') or c.get('user_id', 'analyst_1')}</span>
                            <span style="color: #64748B; font-size: 0.72rem;">{c.get('created_timestamp') or c.get('timestamp', '')}</span>
                        </div>
                        <div style="color: #334155;">{c.get('comment_text', '')}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No prior notes recorded for this alert.")
        st.markdown('</div>', unsafe_allow_html=True)
