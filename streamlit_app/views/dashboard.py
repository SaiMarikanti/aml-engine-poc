"""Dashboard View - AML Monitoring Center."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

try:
    from services.data_service import data_service
    from components.kpi_card import render_kpi_card
    from utils.formatting import format_number, render_risk_badge, render_status_chip
except (ImportError, ModuleNotFoundError):
    from aml_app.services.data_service import data_service
    from aml_app.components.kpi_card import render_kpi_card
    from aml_app.utils.formatting import format_number, render_risk_badge, render_status_chip


def render_dashboard():
    # 1. Title Area
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h2 style="margin: 0; font-size: 1.7rem; font-weight: 800; color: #1E3A8A; letter-spacing: -0.02em;">
                AML MONITORING CENTER
            </h2>
            <p style="margin: 4px 0 0 0; color: #68707A; font-size: 0.92rem;">
                Real-time surveillance of transaction risk, network anomalies, and investigation workload.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 2. Global Status / Metrics Availability Check
    kpis_loaded = True
    try:
        kpis = data_service.get_kpi_summary()
    except Exception:
        kpis_loaded = False
        kpis = {
            "total_transactions": 0,
            "total_alerts": 0,
            "high_risk_alerts": 0,
            "open_cases": 0,
            "suspicious_volume": 0.0
        }

    if not kpis_loaded:
        c_warn1, c_warn2 = st.columns([3, 1])
        with c_warn1:
            st.markdown("""
                <div class="neo-warning-compact">
                    <div>
                        <b style="color: #92400E; font-size: 0.9rem;">⚠ Dashboard metrics unavailable</b>
                        <div style="font-size: 0.82rem; color: #68707A; margin-top: 2px;">
                            Could not read aml_engine.aml_poc lakehouse tables.
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with c_warn2:
            if st.button("Check System Status →", key="dash_check_status_btn", use_container_width=True):
                pages_map = st.session_state.get("_pages_map", {})
                if "System Status" in pages_map:
                    st.switch_page(pages_map["System Status"])

    # 3. Four Primary KPI Cards
    total_alerts_cnt = kpis.get("total_alerts", 0)
    high_risk_cnt = kpis.get("high_risk_alerts", 0)
    suspicious_vol = kpis.get("suspicious_volume", 0.0)
    high_risk_pct = (high_risk_cnt / max(1, total_alerts_cnt) * 100) if total_alerts_cnt > 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card(
            "TOTAL TRANSACTIONS", 
            format_number(kpis.get("total_transactions", 0)), 
            "Live from silver_transactions", 
            trend_positive=True
        )
    with c2:
        render_kpi_card(
            "ACTIVE ALERTS", 
            format_number(total_alerts_cnt), 
            f"${suspicious_vol:,.2f} flagged", 
            trend_positive=False, 
            alert_level="warning"
        )
    with c3:
        render_kpi_card(
            "HIGH & CRITICAL", 
            format_number(high_risk_cnt), 
            f"{high_risk_pct:.1f}% of total alerts", 
            trend_positive=False, 
            alert_level="critical"
        )
    with c4:
        render_kpi_card(
            "OPEN CASES", 
            format_number(kpis.get("open_cases", 0)), 
            "Requires analyst triage", 
            trend_positive=True, 
            alert_level="normal"
        )

    # 4. Main Charts (Alert Trend & Risk Distribution)
    col_chart1, col_chart2 = st.columns([1.3, 1])
    
    with col_chart1:
        st.markdown('<div class="neo-card" style="padding: 16px 20px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight: 700; font-size: 0.95rem; color: #1E3A8A; margin-bottom: 10px;">ALERT TREND OVER TIME</div>', unsafe_allow_html=True)
        try:
            df_trends = data_service.get_alert_trends()
        except Exception:
            df_trends = pd.DataFrame({'time_step': [1, 2, 3, 4], 'alert_count': [0, 0, 0, 0], 'total_amount': [0, 0, 0, 0]})
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=df_trends['time_step'], 
            y=df_trends['alert_count'],
            mode='lines+markers',
            line=dict(color='#DC2626', width=2.5),
            marker=dict(size=6, color='#DC2626'),
            fill='tozeroy',
            fillcolor='rgba(220, 38, 38, 0.08)',
            name='Alert Volume'
        ))
        fig_trend.update_layout(
            margin=dict(l=20, r=20, t=10, b=20),
            height=250,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title="SURVEILLANCE STEP", showgrid=True, gridcolor="#DFE4EA"),
            yaxis=dict(title="ALERTS FLAGGED", showgrid=True, gridcolor="#DFE4EA"),
            hovermode="x unified"
        )
        st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_chart2:
        st.markdown('<div class="neo-card" style="padding: 16px 20px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight: 700; font-size: 0.95rem; color: #1E3A8A; margin-bottom: 10px;">RISK SEVERITY DISTRIBUTION</div>', unsafe_allow_html=True)
        try:
            df_risk = data_service.get_risk_distribution()
        except Exception:
            df_risk = pd.DataFrame({'risk_tier': ['LOW', 'MEDIUM', 'HIGH'], 'count': [0, 0, 0]})
        
        tier_color_map = {
            'CRITICAL': '#991B1B',
            'HIGH': '#DC2626',
            'MEDIUM': '#D97706',
            'LOW': '#059669'
        }
        colors = [tier_color_map.get(t, '#94A3B8') for t in df_risk['risk_tier']]
        
        fig_donut = go.Figure(data=[go.Pie(
            labels=df_risk['risk_tier'],
            values=df_risk['count'],
            hole=0.58,
            marker=dict(colors=colors),
            textinfo='label+percent',
            showlegend=False
        )])
        fig_donut.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=250,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # 5. Suspicious Amount Trend & Top Risky Accounts
    c_bot1, c_bot2 = st.columns([1.3, 1])
    
    with c_bot1:
        st.markdown('<div class="neo-card" style="padding: 16px 20px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight: 700; font-size: 0.95rem; color: #1E3A8A; margin-bottom: 10px;">SUSPICIOUS AMOUNT TREND (₹)</div>', unsafe_allow_html=True)
        
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(
            x=df_trends['time_step'],
            y=df_trends['total_amount'],
            marker_color='#1E3A8A',
            opacity=0.88,
            name='Suspicious ₹'
        ))
        fig_vol.update_layout(
            margin=dict(l=20, r=20, t=10, b=20),
            height=230,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title="SURVEILLANCE STEP", showgrid=False),
            yaxis=dict(title="VOLUME (₹)", showgrid=True, gridcolor="#DFE4EA")
        )
        st.plotly_chart(fig_vol, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c_bot2:
        st.markdown('<div class="neo-card" style="padding: 16px 20px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight: 700; font-size: 0.95rem; color: #1E3A8A; margin-bottom: 12px;">TOP RISKY ACCOUNTS</div>', unsafe_allow_html=True)
        try:
            df_top_acc = data_service.get_top_risky_accounts(limit=4)
        except Exception:
            df_top_acc = pd.DataFrame()
        
        pages_map = st.session_state.get("_pages_map", {})
        if not df_top_acc.empty:
            for idx, acc in df_top_acc.iterrows():
                acc_id = acc['ACCOUNT_ID']
                r_score = float(acc['RISK_SCORE'])
                open_a = acc['OPEN_ALERTS']
                
                c_a, c_b = st.columns([2.6, 1])
                with c_a:
                    st.markdown(f"""
                        <div style="font-size: 0.88rem; font-weight: 700; color: #20242A;">
                            ACC_{acc_id} <span style="font-size: 0.76rem; color: #68707A; font-weight: 500;">({acc.get('COUNTRY', 'US')} | {acc.get('ACCOUNT_TYPE', 'Individual')})</span>
                        </div>
                        <div style="font-size: 0.78rem; color: #68707A;">
                            Risk Score: <b>{r_score:.2f}</b> • Alerts: <b>{open_a}</b>
                        </div>
                    """, unsafe_allow_html=True)
                with c_b:
                    if st.button("Inspect", key=f"dash_inspect_acc_{acc_id}_{idx}", use_container_width=True):
                        st.session_state.selected_account = int(acc_id)
                        if "Accounts" in pages_map:
                            st.switch_page(pages_map["Accounts"])
                st.markdown('<div style="height: 1px; background: #DFE4EA; margin: 6px 0;"></div>', unsafe_allow_html=True)
        else:
            st.caption("No account risk rankings currently available.")
        st.markdown('</div>', unsafe_allow_html=True)

    # 6. Recent Alerts Table
    st.markdown('<div class="neo-card" style="padding: 18px 22px;">', unsafe_allow_html=True)
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-weight: 700; font-size: 1.05rem; color: #1E3A8A;">RECENT HIGH-RISK ALERTS</span>
            <span style="font-size: 0.8rem; color: #68707A;">Generated by Databricks Rule, Graph, and ML Pipelines</span>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        recent_alerts = data_service.get_recent_alerts(limit=6)
    except Exception:
        recent_alerts = pd.DataFrame()
    
    if not recent_alerts.empty:
        st.markdown("""
            <div style="display: grid; grid-template-columns: 1.1fr 1.2fr 1.2fr 1.1fr 1fr 1fr 1.1fr; 
                        font-size: 0.76rem; font-weight: 700; color: #68707A; text-transform: uppercase; 
                        border-bottom: 2px solid #D1D5DB; padding-bottom: 8px; margin-bottom: 8px;">
                <div>Alert ID</div>
                <div>Pattern Type</div>
                <div>Detection</div>
                <div>Amount (₹)</div>
                <div>Risk Score</div>
                <div>Status</div>
                <div style="text-align: right;">Action</div>
            </div>
        """, unsafe_allow_html=True)
        
        for idx, alert in recent_alerts.iterrows():
            a_id = alert['ALERT_ID']
            c_al1, c_al2, c_al3, c_al4, c_al5, c_al6, c_al7 = st.columns([1.1, 1.2, 1.2, 1.1, 1, 1, 1.1])
            
            with c_al1:
                st.markdown(f'<span class="code-pill">AL{a_id}</span>', unsafe_allow_html=True)
            with c_al2:
                st.markdown(f'<span style="font-weight: 600; font-size: 0.85rem;">{alert["ALERT_TYPE"]}</span>', unsafe_allow_html=True)
            with c_al3:
                st.markdown(f'<span style="font-size: 0.82rem; color: #4B5563;">{alert["DETECTION_ENGINE"]}</span>', unsafe_allow_html=True)
            with c_al4:
                st.markdown(f'<span style="font-weight: 600; font-size: 0.85rem;">₹{alert["TX_AMOUNT"]:,.2f}</span>', unsafe_allow_html=True)
            with c_al5:
                st.markdown(render_risk_badge("HIGH" if alert["RISK_SCORE"] >= 0.7 else "MED"), unsafe_allow_html=True)
            with c_al6:
                st.markdown(render_status_chip(alert["STATUS"]), unsafe_allow_html=True)
            with c_al7:
                if st.button("Investigate", key=f"dash_inv_{a_id}_{idx}", use_container_width=True):
                    st.session_state.selected_alert = int(a_id)
                    pages_map = st.session_state.get("_pages_map", {})
                    if "Alerts" in pages_map:
                        st.switch_page(pages_map["Alerts"])
            st.markdown('<div style="height: 1px; background: #EEF2F6; margin: 4px 0;"></div>', unsafe_allow_html=True)
    else:
        st.caption("No alerts currently recorded.")

    st.markdown('</div>', unsafe_allow_html=True)
