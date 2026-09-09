"""Transaction Explorer & Multi-Detector Transaction Details."""
import streamlit as st
import pandas as pd
from aml_app.services.data_service import data_service
from aml_app.components.breadcrumbs import render_breadcrumbs
from aml_app.components.alert_card import render_evidence_chip
from aml_app.utils.formatting import format_currency, render_risk_badge

def render_transactions():
    # If a specific transaction is selected, show Transaction Details
    selected_tx_id = st.session_state.get("selected_transaction")
    if selected_tx_id is not None:
        render_transaction_details(selected_tx_id)
        return

    # Otherwise show Transaction Explorer list
    st.markdown("""
        <div style="margin-bottom: 18px;">
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: #1E3A8A;">TRANSACTION EXPLORER</h2>
            <p style="margin: 4px 0 0 0; color: #68707A; font-size: 0.9rem;">
                Search across 1.32M surveillance transactions using indexed filters and multi-detector scoring.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Filter Bar Card
    st.markdown('<div class="neo-card" style="padding: 18px 22px; margin-bottom: 20px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-weight: 700; font-size: 0.88rem; color: #1E3A8A; margin-bottom: 12px; text-transform: uppercase;">Parameterized Search Filters</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        tx_input = st.text_input("Transaction ID (TX_ID)", placeholder="e.g. 82 or 22797")
    with c2:
        sender_input = st.text_input("Sender Account ID", placeholder="e.g. 6976")
    with c3:
        receiver_input = st.text_input("Receiver Account ID", placeholder="e.g. 9739")

    c4, c5, c6 = st.columns([1, 1, 1])
    with c4:
        min_amt = st.number_input("Min Amount (₹)", min_value=0.0, value=0.0, step=10.0)
    with c5:
        max_amt = st.number_input("Max Amount (₹)", min_value=0.0, value=0.0, step=100.0)
    with c6:
        is_fraud = st.checkbox("Flagged Anomalies Only", value=False)

    col_btn, col_exp = st.columns([1.5, 4.5])
    with col_btn:
        search_clicked = st.button("SEARCH TRANSACTIONS", type="primary", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Parse filters
    parsed_tx = int(tx_input.strip()) if tx_input.strip().isdigit() else None
    parsed_sender = int(sender_input.strip()) if sender_input.strip().isdigit() else None
    parsed_recv = int(receiver_input.strip()) if receiver_input.strip().isdigit() else None
    parsed_min = min_amt if min_amt > 0 else None
    parsed_max = max_amt if max_amt > 0 else None

    # Execute Search
    limit = 25
    try:
        df, total_matches = data_service.search_transactions(
            tx_id=parsed_tx,
            sender_id=parsed_sender,
            receiver_id=parsed_recv,
            min_amount=parsed_min,
            max_amount=parsed_max,
            is_fraud_only=is_fraud,
            limit=limit,
            offset=0
        )
    except Exception as e:
        st.error(f"Unable to load transaction data: Databricks SQL query failed ({e}). Check the System Status page for connection details.")
        df = pd.DataFrame()
        total_matches = 0

    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-weight: 600; font-size: 0.92rem; color: #4B5563;">
                Showing top <b>{len(df)}</b> of <b>{total_matches:,}</b> matching transactions
            </span>
        </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("No transactions match your search filters. Try clearing or expanding your criteria.")
        return

    # Table of Results
    st.markdown('<div class="neo-card" style="padding: 16px 20px;">', unsafe_allow_html=True)
    st.markdown("""
        <div style="display: grid; grid-template-columns: 1.2fr 1.2fr 1.2fr 1fr 1.2fr 1fr 1.2fr; 
                    font-size: 0.78rem; font-weight: 700; color: #68707A; text-transform: uppercase; 
                    border-bottom: 2px solid #D1D5DB; padding-bottom: 8px; margin-bottom: 8px;">
            <div>TX ID</div>
            <div>Sender Account</div>
            <div>Receiver Account</div>
            <div>Type</div>
            <div>Amount (₹)</div>
            <div>Flagged</div>
            <div style="text-align: right;">Action</div>
        </div>
    """, unsafe_allow_html=True)

    for idx, row in df.iterrows():
        txid = int(row['TX_ID'])
        sender = int(row['SENDER_ACCOUNT_ID'])
        recv = int(row['RECEIVER_ACCOUNT_ID'])
        amt = float(row['TX_AMOUNT'])
        fraud = bool(row['IS_FRAUD'])
        
        c1, c2, c3, c4, c5, c6, c7 = st.columns([1.2, 1.2, 1.2, 1, 1.2, 1, 1.2])
        with c1:
            st.markdown(f'<span class="code-pill">TX{txid}</span>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'ACC_{sender}')
        with c3:
            st.markdown(f'ACC_{recv}')
        with c4:
            st.markdown(row.get('TX_TYPE', 'TRANSFER'))
        with c5:
            st.markdown(f'<b>₹{amt:,.2f}</b>', unsafe_allow_html=True)
        with c6:
            st.markdown(render_risk_badge("HIGH" if fraud else "LOW"), unsafe_allow_html=True)
        with c7:
            if st.button("Details", key=f"btn_tx_{txid}_{idx}", use_container_width=True):
                st.session_state.selected_transaction = txid
                st.rerun()
        st.markdown('<div style="height: 1px; background: #EEF2F6; margin: 4px 0;"></div>', unsafe_allow_html=True)

    # Export filtered results
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="EXPORT FILTERED TRANSACTIONS (CSV)",
        data=csv_data,
        file_name="aml_filtered_transactions.csv",
        mime="text/csv"
    )
    st.markdown('</div>', unsafe_allow_html=True)

def render_transaction_details(tx_id: int):
    """Render comprehensive Transaction Details page."""
    render_breadcrumbs([("Dashboard", "Dashboard"), ("Transactions", "Transactions"), (f"TX{tx_id}", "")])
    
    tx = data_service.get_transaction_details(tx_id)
    if not tx:
        st.error(f"Transaction TX{tx_id} could not be located in surveillance storage.")
        if st.button("Back to Explorer"):
            st.session_state.selected_transaction = None
            st.rerun()
        return

    score = tx.get("RISK_SCORE", 0.08)
    risk_level = "CRITICAL" if score >= 0.85 else ("HIGH" if score >= 0.65 else ("MEDIUM" if score >= 0.40 else "LOW"))

    # Header Card
    st.markdown(f"""
        <div class="neo-card" style="padding: 20px 24px; border-left: 6px solid {'#DC2626' if score >= 0.65 else '#059669'};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700; color: #1E3A8A;">
                        TRANSACTION TX{tx_id}
                    </h2>
                    <span style="font-size: 0.86rem; color: #68707A;">Recorded Surveillance Timestamp: Step {tx.get('TIMESTAMP', 0)}</span>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.8rem; color: #68707A; font-weight: 600;">COMPOSITE RISK SCORE</div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: {'#DC2626' if score >= 0.65 else '#059669'};">
                        {score:.2f}
                    </div>
                    {render_risk_badge(risk_level)}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Core Transaction Fields
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div class="neo-card-sm">
                <div style="font-size: 0.75rem; color: #68707A; font-weight: 600;">SENDER ACCOUNT</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #20242A;">ACC_{tx['SENDER_ACCOUNT_ID']}</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="neo-card-sm">
                <div style="font-size: 0.75rem; color: #68707A; font-weight: 600;">RECEIVER ACCOUNT</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #20242A;">ACC_{tx['RECEIVER_ACCOUNT_ID']}</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="neo-card-sm">
                <div style="font-size: 0.75rem; color: #68707A; font-weight: 600;">TRANSACTION AMOUNT</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #20242A;">₹{tx['TX_AMOUNT']:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class="neo-card-sm">
                <div style="font-size: 0.75rem; color: #68707A; font-weight: 600;">TRANSFER TYPE</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #20242A;">{tx.get('TX_TYPE', 'WIRE')}</div>
            </div>
        """, unsafe_allow_html=True)

    # Detection Breakdown: Why was it flagged?
    st.markdown('<div class="neo-card" style="padding: 22px; margin-top: 14px;">', unsafe_allow_html=True)
    st.markdown("""
        <div style="font-size: 1.05rem; font-weight: 700; color: #1E3A8A; margin-bottom: 6px;">
            DETECTION ENGINE BREAKDOWN: WHY WAS IT FLAGGED?
        </div>
        <p style="font-size: 0.85rem; color: #68707A; margin-bottom: 16px;">
            Surveillance engines evaluate every transaction across heuristic rules, graph topology, and gradient boosting:
            <code>final_risk_score = 0.40 × rule_score + 0.60 × ml_probability</code>
        </p>
    """, unsafe_allow_html=True)

    r_score = tx.get("RULE_SCORE", 0.05)
    m_prob = tx.get("ML_PROBABILITY", 0.04)
    tr_rules = tx.get("TRIGGERED_RULES", "NONE")

    c_score1, c_score2, c_score3 = st.columns(3)
    with c_score1:
        st.markdown(f"""
            <div style="background: #F1F4F8; padding: 10px 14px; border-radius: 8px; font-size: 0.82rem;">
                Rule Engine Score (40% weight): <b style="color: #1E3A8A;">{r_score:.2f}</b>
            </div>
        """, unsafe_allow_html=True)
    with c_score2:
        st.markdown(f"""
            <div style="background: #F1F4F8; padding: 10px 14px; border-radius: 8px; font-size: 0.82rem;">
                XGBoost ML Probability (60% weight): <b style="color: #1E3A8A;">{m_prob:.2f}</b>
            </div>
        """, unsafe_allow_html=True)
    with c_score3:
        st.markdown(f"""
            <div style="background: #F1F4F8; padding: 10px 14px; border-radius: 8px; font-size: 0.82rem;">
                Active Rule Triggers: <b style="color: #DC2626;">{tr_rules}</b>
            </div>
        """, unsafe_allow_html=True)

    st.write("")
    det = tx["detectors"]
    cd1, cd2, cd3 = st.columns(3)
    with cd1:
        st.markdown(render_evidence_chip("Rule Engine", det["rule_engine"]["triggered"], det["rule_engine"]["reason"]), unsafe_allow_html=True)
    with cd2:
        st.markdown(render_evidence_chip("Graph Analysis", det["graph_analysis"]["triggered"], det["graph_analysis"]["reason"]), unsafe_allow_html=True)
    with cd3:
        st.markdown(render_evidence_chip("ML Model (XGBoost)", det["ml_model"]["triggered"], det["ml_model"]["reason"]), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Investigator Navigation Actions
    ca1, ca2, ca3, ca4 = st.columns(4)
    with ca1:
        if st.button(f"Inspect Sender ACC_{tx['SENDER_ACCOUNT_ID']}", use_container_width=True):
            st.session_state.selected_account = int(tx['SENDER_ACCOUNT_ID'])
            st.session_state.nav_section = "Accounts"
            st.rerun()
    with ca2:
        if st.button(f"Inspect Receiver ACC_{tx['RECEIVER_ACCOUNT_ID']}", use_container_width=True):
            st.session_state.selected_account = int(tx['RECEIVER_ACCOUNT_ID'])
            st.session_state.nav_section = "Accounts"
            st.rerun()
    with ca3:
        if st.button("Explore in Network Graph", use_container_width=True, type="primary"):
            st.session_state.selected_network_account = int(tx['SENDER_ACCOUNT_ID'])
            st.session_state.nav_section = "Network"
            st.rerun()
    with ca4:
        if st.button("← Back to Transactions", use_container_width=True):
            st.session_state.selected_transaction = None
            st.rerun()
