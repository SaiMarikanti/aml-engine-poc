"""Audit Log View - Enterprise Case Management Trail."""
import streamlit as st
import pandas as pd
try:
    from services.data_service import data_service
except (ImportError, ModuleNotFoundError):
    from aml_app.services.data_service import data_service


def render_audit():
    st.markdown("""
        <div style="margin-bottom: 18px;">
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 800; color: #1E3A8A;">INVESTIGATION AUDIT LOG</h2>
            <p style="margin: 4px 0 0 0; color: #68707A; font-size: 0.9rem;">
                Immutable trail of investigator actions, status transitions, comments, and regulatory triage decisions.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Filter Bar Card
    st.markdown('<div class="neo-card" style="padding: 16px 20px; margin-bottom: 20px;">', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        user_filter = st.selectbox("Filter by Investigator", ["ALL", "analyst_1", "investigator_lead", "compliance_officer_2"])
    with c2:
        st.write("")
        st.write("")
        refresh_clicked = st.button("REFRESH LOG", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    try:
        df_audit = data_service.get_audit_trail(
            limit=50,
            user_filter=None if user_filter == "ALL" else user_filter
        )
    except Exception as e:
        st.error(f"Failed to load audit trail: {e}")
        df_audit = pd.DataFrame()

    if df_audit.empty:
        st.info("No audit logs recorded for this filter.")
        return

    # Table Card
    st.markdown('<div class="neo-card" style="padding: 18px 22px;">', unsafe_allow_html=True)
    st.markdown("""
        <div style="display: grid; grid-template-columns: 1.2fr 1.2fr 1.4fr 1fr 1.2fr 1.2fr 1.2fr; 
                    font-size: 0.78rem; font-weight: 700; color: #68707A; text-transform: uppercase; 
                    border-bottom: 2px solid #D1D5DB; padding-bottom: 8px; margin-bottom: 8px;">
            <div>Timestamp</div>
            <div>User ID</div>
            <div>Action</div>
            <div>Entity</div>
            <div>Target ID</div>
            <div>Previous State</div>
            <div>New State</div>
        </div>
    """, unsafe_allow_html=True)

    for _, row in df_audit.iterrows():
        c1, c2, c3, c4, c5, c6, c7 = st.columns([1.2, 1.2, 1.4, 1, 1.2, 1.2, 1.2])
        with c1:
            st.markdown(f'<span style="font-size: 0.8rem; color: #4B5563;">{row["timestamp"]}</span>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<span style="font-weight: 600; font-size: 0.82rem;">{row["user_id"]}</span>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<span class="code-pill">{row["action"]}</span>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'{row["entity_type"]}')
        with c5:
            st.markdown(f'<b>{row["entity_id"]}</b>', unsafe_allow_html=True)
        with c6:
            st.markdown(f'<span style="color: #68707A; font-size: 0.82rem;">{row["old_value"] or "—"}</span>', unsafe_allow_html=True)
        with c7:
            st.markdown(f'<span style="font-weight: 600; color: #1E3A8A; font-size: 0.82rem;">{row["new_value"] or "—"}</span>', unsafe_allow_html=True)
        st.markdown('<div style="height: 1px; background: #EEF2F6; margin: 4px 0;"></div>', unsafe_allow_html=True)

    # Export audit trail
    csv_bytes = df_audit.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="EXPORT COMPLIANCE AUDIT LOG (CSV)",
        data=csv_bytes,
        file_name="aml_case_audit_trail.csv",
        mime="text/csv"
    )
    st.markdown('</div>', unsafe_allow_html=True)
