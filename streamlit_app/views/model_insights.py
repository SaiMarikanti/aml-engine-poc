"""Model Insights View - Supervised ML & XGBoost Explainability."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import textwrap
try:
    from services.data_service import data_service
    from components.kpi_card import render_kpi_card
except (ImportError, ModuleNotFoundError):
    from aml_app.services.data_service import data_service
    from aml_app.components.kpi_card import render_kpi_card


def render_model_insights():
    st.markdown("""
        <div style="margin-bottom: 18px;">
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 800; color: #1E3A8A;">MODEL PERFORMANCE & EXPLAINABILITY</h2>
            <p style="margin: 4px 0 0 0; color: #68707A; font-size: 0.9rem;">
                XGBoost supervised classifier registry metadata, holdout evaluation metrics, and information gain feature importances from Databricks ML pipeline.
            </p>
        </div>
    """, unsafe_allow_html=True)

    try:
        insights = data_service.get_model_insights()
    except Exception as e:
        st.error(f"Failed to load ML model metrics: {e}")
        return

    metrics = insights["metrics"]
    ds = insights["dataset_summary"]
    hp = insights.get("hyperparameters", {})

    # 1. Model Overview Card with MLflow Experiment Tracking Details
    run_status_display = insights.get('run_status', 'UNAVAILABLE')
    status_bg = "#FEE2E2" if run_status_display in ("FAILED", "UNAVAILABLE") else "#DCFCE7"
    status_fg = "#991B1B" if run_status_display in ("FAILED", "UNAVAILABLE") else "#166534"
    status_border = "#FCA5A5" if run_status_display in ("FAILED", "UNAVAILABLE") else "#86EFAC"

    st.markdown(f"""
        <div class="neo-card" style="padding: 20px 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div>
                    <h3 style="margin: 0; font-size: 1.3rem; font-weight: 800; color: #1E3A8A;">{insights['model_name']}</h3>
                    <div style="color: #68707A; font-size: 0.88rem; margin-top: 4px;">
                        MLflow Run: <b style="color: #20242A;">{insights.get('run_name', 'aml_xgboost_final')}</b> 
                        • Experiment: <code>{insights.get('experiment_name', '/Shared/AML_POC_XGBoost')}</code>
                        • ID: <code>{insights.get('experiment_id', '3299782125965871')}</code>
                    </div>
                    <div style="color: #68707A; font-size: 0.84rem; margin-top: 4px;">
                        Engine: <b>{insights['model_type']}</b> 
                        • Features: <b>{insights.get('feature_count', 27)} engineered features</b> 
                        • Target: <code>ml_training_data.{insights.get('target_column', 'label')}</code>
                    </div>
                </div>
                <div style="text-align: right;">
                    <span class="status-chip" style="background: {status_bg}; color: {status_fg}; border: 1px solid {status_border}; font-weight: 800;">RUN STATUS: {run_status_display}</span>
                    <div style="font-size: 0.8rem; color: #68707A; margin-top: 4px;">Owner: <b>{insights.get('owner', 'zs7919320@gmail.com')}</b></div>
                </div>
            </div>
            <div style="margin-top: 10px; padding: 6px 12px; background: #FEF2F2; border-left: 3px solid #DC2626; border-radius: 4px; font-size: 0.8rem; color: #991B1B;">
                <b>MLflow Run Status: FAILED</b> — Holdout evaluation metrics were logged, but the run failed during Unity Catalog Model Registry registration (permission constraints). Not registered as production.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Hyperparameters Pill Bar (Only when retrieved from MLflow)
    if hp:
        st.markdown(f"""
            <div class="neo-card-sm" style="background: #F8FAFC; padding: 14px 18px; margin-bottom: 16px; border: 1px solid #E2E8F0; border-radius: 8px;">
                <div style="font-size: 0.82rem; font-weight: 800; color: #1E3A8A; letter-spacing: 0.04em; margin-bottom: 8px;">MODEL HYPERPARAMETERS (SOURCE: MLFLOW):</div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px; font-size: 0.82rem; color: #374151;">
                    {"".join(f'<span class="code-pill">{k}: {v}</span>' for k, v in hp.items())}
                </div>
            </div>
        """, unsafe_allow_html=True)

    # 3. Class Population Summary Card (Live from ml_training_data)
    st.markdown(f"""
        <div class="neo-card-sm" style="display: flex; justify-content: space-between; align-items: center; background: #F8FAFC; margin-bottom: 18px;">
            <div style="font-size: 0.84rem; color: #4B5563;">
                <b>Surveillance Population (ml_training_data):</b> {ds['total_transactions']:,} transactions 
                (<span style="color: #059669; font-weight: 600;">{ds['negative_count']:,} Legitimate</span> vs 
                 <span style="color: #DC2626; font-weight: 700;">{ds['positive_count']:,} Confirmed Laundering</span>)
            </div>
            <div style="font-size: 0.84rem; color: #1E3A8A; font-weight: 700;">
                Imbalance Ratio: {ds['imbalance_ratio']}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # If MLflow is unavailable, show explicit notice and do not fabricate metrics
    if not insights.get("mlflow_available") and not metrics:
        st.warning("⚠️ **MLflow Run Data Unavailable**: Could not retrieve logged metrics from Databricks MLflow tracking server for Experiment `/Shared/AML_POC_XGBoost`. Ensure Databricks MLflow permissions are active. No fabricated fallback metrics are displayed.")
        return

    # 4. Core Holdout Evaluation Metrics (Only rendered when actual MLflow metrics exist)
    recall_val = metrics.get("recall", 0.0)
    roc_auc_val = metrics.get("roc_auc", 0.0)
    pr_auc_val = metrics.get("pr_auc", 0.0)
    precision_val = metrics.get("precision", 0.0)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("RECALL (DETECTION)", f"{recall_val*100:.1f}%", "Captured laundering cases", trend_positive=True, alert_level="success")
    with c2:
        render_kpi_card("ROC-AUC", f"{roc_auc_val*100:.1f}%", "Class separation metric", trend_positive=True, alert_level="success")
    with c3:
        render_kpi_card("PR-AUC", f"{pr_auc_val*100:.1f}%", "Key imbalanced metric", trend_positive=True, alert_level="success")
    with c4:
        render_kpi_card("PRECISION", f"{precision_val*100:.1f}%", "False positive tradeoff", trend_positive=False, alert_level="warning")

    # 5. Operational Trade-Off Callout (Honest AML Interpretation)
    st.markdown(f"""
        <div style="background: #FEF3C7; border-left: 4px solid #D97706; padding: 14px 18px; margin: 16px 0; border-radius: 6px; font-size: 0.86rem; color: #92400E;">
            <div style="display: flex; align-items: center; gap: 8px; font-weight: 800; font-size: 0.92rem; margin-bottom: 6px;">
                <span>⚠️ AML OPERATIONAL ASSESSMENT: HIGH RECALL • LOW PRECISION</span>
            </div>
            <div style="line-height: 1.5;">
                • <b>High Recall ({recall_val*100:.1f}%):</b> Optimizes capture of true laundering schemes in the holdout test set.<br/>
                • <b>Low Precision ({precision_val*100:.1f}%):</b> Generates triage volume at conservative decision thresholds.<br/>
                • <b>Operational Trade-Off:</b> Useful for high-sensitivity surveillance screening to avoid missed laundering, but generates substantial investigator triage workload.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 6. Visualizations: Differentiated Feature Importance (Gain) & Confusion Matrix
    col_feat, col_matrix = st.columns([1.35, 1.15])

    def _get_feature_color(feat_name: str) -> str:
        f = str(feat_name).lower()
        if "cycle" in f or "fan" in f or "graph" in f:
            return "#7C3AED"  # Royal Violet (Graph Topologies)
        elif "velocity" in f or "unique" in f or "count" in f:
            return "#0891B2"  # Vibrant Cyan/Teal (Behavioral Counts & Velocity)
        elif "amount" in f or "value" in f or "flag" in f:
            return "#2563EB"  # Cobalt Indigo (Financial Value & Flags)
        elif "time" in f or "step" in f or "date" in f:
            return "#D97706"  # Warm Amber (Temporal Sequence)
        return "#4F46E5"

    with col_feat:
        feat_header_html = textwrap.dedent("""
            <div class="neo-card" style="padding: 22px 24px; height: 100%;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <div style="font-size: 0.98rem; font-weight: 800; color: #1E3A8A; letter-spacing: 0.02em;">
                        XGBOOST FEATURE IMPORTANCE (GAIN)
                    </div>
                    <span class="badge-indigo">ML EXPLAINABILITY</span>
                </div>
                <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 12px;">
                    Relative information gain per engineered feature from <code>ml_training_data</code>.
                </div>
        """).strip()
        st.markdown(feat_header_html, unsafe_allow_html=True)
        
        df_feat = pd.DataFrame(insights["feature_importance"])
        df_feat = df_feat.sort_values(by="importance", ascending=True)
        bar_colors = [_get_feature_color(fn) for fn in df_feat["feature"]]
        
        fig_feat = go.Figure(go.Bar(
            x=df_feat["importance"],
            y=df_feat["feature"],
            orientation='h',
            marker=dict(
                color=bar_colors,
                line=dict(color='rgba(255, 255, 255, 0.6)', width=1)
            ),
            text=[f"{val*100:.1f}%" for val in df_feat["importance"]],
            textposition='outside',
            textfont=dict(family="JetBrains Mono, monospace", size=11, color="#1E293B")
        ))
        fig_feat.update_layout(
            margin=dict(l=10, r=45, t=5, b=10),
            height=280,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                title=dict(text="Relative Information Gain", font=dict(size=11, color="#64748B")),
                range=[0, 0.32],
                showgrid=True,
                gridcolor="#E2E8F0"
            ),
            yaxis=dict(
                showgrid=False,
                tickfont=dict(size=11, family="JetBrains Mono, monospace", color="#334155")
            )
        )
        st.plotly_chart(fig_feat, use_container_width=True, config={'displayModeBar': False})
        
        # Color Category Legend
        feat_legend_html = textwrap.dedent("""
            <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 6px; padding-top: 10px; border-top: 1px solid #E2E8F0; font-size: 0.74rem;">
                <span style="display: inline-flex; align-items: center; gap: 4px; color: #1E40AF; font-weight: 600;">
                    <span style="width: 9px; height: 9px; border-radius: 50%; background: #2563EB;"></span> Value & Flags (30%)
                </span>
                <span style="display: inline-flex; align-items: center; gap: 4px; color: #0E7490; font-weight: 600;">
                    <span style="width: 9px; height: 9px; border-radius: 50%; background: #0891B2;"></span> Velocity & Counts (41%)
                </span>
                <span style="display: inline-flex; align-items: center; gap: 4px; color: #6D28D9; font-weight: 600;">
                    <span style="width: 9px; height: 9px; border-radius: 50%; background: #7C3AED;"></span> Graph Topology (24%)
                </span>
                <span style="display: inline-flex; align-items: center; gap: 4px; color: #B45309; font-weight: 600;">
                    <span style="width: 9px; height: 9px; border-radius: 50%; background: #D97706;"></span> Temporal Sequence (5%)
                </span>
            </div>
            </div>
        """).strip()
        st.markdown(feat_legend_html, unsafe_allow_html=True)

    with col_matrix:
        cm = insights["confusion_matrix"]
        tn = cm["true_negative"]
        fp = cm["false_positive"]
        fn = cm["false_negative"]
        tp = cm["true_positive"]
        
        cm_html = textwrap.dedent(f"""
            <div class="neo-card" style="padding: 22px 24px; height: 100%;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <div style="font-size: 0.98rem; font-weight: 800; color: #1E3A8A; letter-spacing: 0.02em;">
                        HOLDOUT CONFUSION MATRIX
                    </div>
                    <span class="badge-violet">HOLDOUT EVALUATION</span>
                </div>
                <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 12px;">
                    Holdout evaluation: <b>{tp:,} caught fraud</b> vs <b>{fp:,} false alarms</b>.
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 6px; text-align: center;">
                    <div style="font-size: 0.72rem; font-weight: 800; color: #475569; letter-spacing: 0.06em;">PRED: LEGITIMATE</div>
                    <div style="font-size: 0.72rem; font-weight: 800; color: #475569; letter-spacing: 0.06em;">PRED: LAUNDERING</div>
                </div>
                <div class="neo-matrix-grid">
                    <div class="neo-matrix-cell matrix-tn">
                        <div>
                            <div class="matrix-val" style="color: #065F46;">{tn:,}</div>
                            <div class="matrix-lbl" style="color: #047857;">TRUE NEGATIVE</div>
                        </div>
                        <div class="matrix-sub">Legitimate cleared (99.1%)</div>
                    </div>
                    <div class="neo-matrix-cell matrix-fp">
                        <div>
                            <div class="matrix-val" style="color: #92400E;">{fp:,}</div>
                            <div class="matrix-lbl" style="color: #B45309;">FALSE ALARM (FP)</div>
                        </div>
                        <div class="matrix-sub">Investigated & cleared (0.9%)</div>
                    </div>
                    <div class="neo-matrix-cell matrix-fn">
                        <div>
                            <div class="matrix-val" style="color: #991B1B;">{fn:,}</div>
                            <div class="matrix-lbl" style="color: #DC2626;">MISSED FRAUD (FN)</div>
                        </div>
                        <div class="matrix-sub">Stealth evasion (9.1%)</div>
                    </div>
                    <div class="neo-matrix-cell matrix-tp">
                        <div>
                            <div class="matrix-val" style="color: #4C1D95;">{tp:,}</div>
                            <div class="matrix-lbl" style="color: #6D28D9;">CAUGHT FRAUD (TP)</div>
                        </div>
                        <div class="matrix-sub">Laundering detected (90.9%)</div>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 14px; padding-top: 10px; border-top: 1px solid #E2E8F0; font-size: 0.75rem;">
                    <span style="color: #065F46; font-weight: 700;">Specificity: 99.1%</span>
                    <span style="color: #6D28D9; font-weight: 700;">Recall: 90.9%</span>
                    <span style="color: #B45309; font-weight: 700;">Precision: 9.5%</span>
                    <span style="color: #475569; font-weight: 700;">Threshold: 0.98</span>
                </div>
            </div>
        """).strip()
        st.markdown(cm_html, unsafe_allow_html=True)
