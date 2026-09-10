"""Account Risk Profile - 360 Degree View."""
import streamlit as st
import pandas as pd
try:
    from services.data_service import data_service
    from components.breadcrumbs import render_breadcrumbs
    from utils.formatting import format_currency, render_risk_badge, render_status_chip
except (ImportError, ModuleNotFoundError):
    from aml_app.services.data_service import data_service
    from aml_app.components.breadcrumbs import render_breadcrumbs
    from aml_app.utils.formatting import format_currency, render_risk_badge, render_status_chip


def render_accounts():
    pages_map = st.session_state.get("_pages_map", {})
    
    st.markdown("""
        <div style="margin-bottom: 18px;">
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 800; color: #1E3A8A;">ACCOUNT RISK PROFILE</h2>
            <p style="margin: 4px 0 0 0; color: #68707A; font-size: 0.9rem;">
                Surveillance 360-degree account profile, counterparty exposure, and GraphFrames topology metrics.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Search Bar Card
    st.markdown('<div class="neo-card" style="padding: 16px 20px; margin-bottom: 20px;">', unsafe_allow_html=True)
    c_s1, c_s2 = st.columns([3, 1])
    with c_s1:
        default_val = str(st.session_state.get("selected_account", 6976))
        acc_input = st.text_input("Enter Account ID to Inspect", value=default_val, placeholder="e.g. 6976, 9739, 5776")
    with c_s2:
        st.write("")
        st.write("")
        search_clicked = st.button("LOAD ACCOUNT", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if not acc_input.strip().isdigit():
        st.warning("Please enter a valid numeric Account ID.")
        return

    account_id = int(acc_input.strip())
    st.session_state.selected_account = account_id
    
    acc = data_service.get_account_profile(account_id)
    if not acc:
        st.error(f"Account ACC_{account_id} not found in surveillance records.")
        return

    score = acc.get("RISK_SCORE", 0.15)
    risk_level = "CRITICAL" if score >= 0.85 else ("HIGH" if score >= 0.65 else ("MEDIUM" if score >= 0.40 else "LOW"))

    # Top Account Summary Card
    st.markdown(f"""
        <div class="neo-card" style="padding: 22px 26px; border-left: 6px solid {'#991B1B' if risk_level in ('HIGH', 'CRITICAL') else '#059669'};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                        <span style="font-size: 1.8rem; font-weight: 800; color: #1E3A8A;">ACCOUNT ACC_{account_id}</span>
                        {render_risk_badge(risk_level)}
                    </div>
                    <div style="font-size: 0.9rem; color: #68707A;">
                        Customer ID: <b>{acc.get('CUSTOMER_ID', 'C_UNKNOWN')}</b> 
                        • Domicile Country: <b>{acc.get('COUNTRY', 'US')}</b> 
                        • Type: <b>{acc.get('ACCOUNT_TYPE', 'Individual')}</b>
                        • Initial Deposit: <b>₹{acc.get('INIT_BALANCE', 0.0):,.2f}</b>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.78rem; font-weight: 700; color: #68707A; text-transform: uppercase;">Centrality Risk Score</div>
                    <div style="font-size: 2.5rem; font-weight: 800; color: {'#DC2626' if score >= 0.65 else '#059669'}; line-height: 1;">
                        {score:.2f}
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Core Metric Cards: Transactions, Open Alerts, Total Sent, Total Received, Suspicious Connections
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""
            <div class="neo-card-sm">
                <div style="font-size: 0.72rem; color: #68707A; font-weight: 700;">TRANSACTIONS</div>
                <div style="font-size: 1.3rem; font-weight: 800; color: #20242A;">{acc.get('INCOMING_COUNT', 0) + acc.get('OUTGOING_COUNT', 0)}</div>
            </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
            <div class="neo-card-sm">
                <div style="font-size: 0.72rem; color: #68707A; font-weight: 700;">OPEN ALERTS</div>
                <div style="font-size: 1.3rem; font-weight: 800; color: #DC2626;">{acc.get('OPEN_ALERTS', 0)}</div>
            </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
            <div class="neo-card-sm">
                <div style="font-size: 0.72rem; color: #68707A; font-weight: 700;">TOTAL SENT</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #DC2626;">₹{acc.get('TOTAL_SENT', 0.0):,.0f}</div>
            </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
            <div class="neo-card-sm">
                <div style="font-size: 0.72rem; color: #68707A; font-weight: 700;">TOTAL RECEIVED</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #059669;">₹{acc.get('TOTAL_RECEIVED', 0.0):,.0f}</div>
            </div>
        """, unsafe_allow_html=True)
    with m5:
        st.markdown(f"""
            <div class="neo-card-sm">
                <div style="font-size: 0.72rem; color: #68707A; font-weight: 700;">SUSPICIOUS CONNECTIONS</div>
                <div style="font-size: 1.3rem; font-weight: 800; color: #991B1B;">{acc.get('SUSPICIOUS_CONNECTIONS', 0)}</div>
            </div>
        """, unsafe_allow_html=True)

    # Risk Factors & Network Launch
    col_factors, col_netbtn = st.columns([2.2, 1])
    with col_factors:
        st.markdown('<div class="neo-card" style="padding: 20px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.95rem; font-weight: 700; color: #1E3A8A; margin-bottom: 12px;">SYSTEMIC RISK FACTORS DETECTED</div>', unsafe_allow_html=True)
        factors = acc.get("risk_factors", [])
        for f in factors:
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 8px; font-size: 0.86rem; color: #20242A; margin-bottom: 8px;">
                    <span style="color: #DC2626; font-weight: 700;">⚠</span> {f}
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_netbtn:
        st.markdown('<div class="neo-card" style="padding: 20px; text-align: center;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.95rem; font-weight: 700; color: #1E3A8A; margin-bottom: 8px;">NETWORK TOPOLOGY</div>', unsafe_allow_html=True)
        st.write("Explore connected transfer counterparties and circular routing in the GraphFrames canvas.")
        st.write("")
        if st.button("OPEN IN NETWORK ANALYSIS", type="primary", use_container_width=True):
            st.session_state.selected_network_account = account_id
            if "Network" in pages_map:
                st.switch_page(pages_map["Network"])
        st.markdown('</div>', unsafe_allow_html=True)

    # Sub-sections: Alerts, Transaction History, Connected Accounts
    t_alerts, t_txs = st.tabs(["Active Alerts", "Transaction History"])
    
    with t_alerts:
        rel_alerts = acc.get("related_alerts", [])
        if not rel_alerts:
            st.caption("No open alerts associated with this account.")
        else:
            for idx, ra in enumerate(rel_alerts):
                c1, c2, c3, c4, c5 = st.columns([1, 1.5, 1.2, 1, 1])
                with c1:
                    st.markdown(f'<span class="code-pill">AL{ra["ALERT_ID"]}</span>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'{ra["ALERT_TYPE"].upper()} ({ra["DETECTION_ENGINE"]})')
                with c3:
                    st.markdown(f'₹{ra["TX_AMOUNT"]:,.2f}')
                with c4:
                    st.markdown(render_status_chip(ra["STATUS"]), unsafe_allow_html=True)
                with c5:
                    if st.button("View Alert", key=f"btn_rel_al_{ra['ALERT_ID']}_{idx}", use_container_width=True):
                        st.session_state.selected_alert = int(ra['ALERT_ID'])
                        if "Alerts" in pages_map:
                            st.switch_page(pages_map["Alerts"])
                st.markdown('<div style="height: 1px; background: #EEF2F6; margin: 4px 0;"></div>', unsafe_allow_html=True)

    with t_txs:
        rel_txs = acc.get("recent_transactions", [])
        if not rel_txs:
            st.caption("No recent transactions recorded.")
        else:
            for idx, rt in enumerate(rel_txs):
                c1, c2, c3, c4 = st.columns([1.2, 2, 1.5, 1])
                with c1:
                    st.markdown(f'<span class="code-pill">TX{rt["TX_ID"]}</span>', unsafe_allow_html=True)
                with c2:
                    is_send = (rt['SENDER_ACCOUNT_ID'] == account_id)
                    direction = f"OUTGOING → ACC_{rt['RECEIVER_ACCOUNT_ID']}" if is_send else f"INCOMING ← ACC_{rt['SENDER_ACCOUNT_ID']}"
                    st.markdown(direction)
                with c3:
                    st.markdown(f'₹{rt["TX_AMOUNT"]:,.2f}')
                with c4:
                    if st.button("TX Details", key=f"btn_acc_tx_{rt['TX_ID']}_{idx}", use_container_width=True):
                        st.session_state.selected_transaction = int(rt['TX_ID'])
                        if "Transactions" in pages_map:
                            st.switch_page(pages_map["Transactions"])
                st.markdown('<div style="height: 1px; background: #EEF2F6; margin: 4px 0;"></div>', unsafe_allow_html=True)
