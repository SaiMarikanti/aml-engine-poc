"""Model Insights View - Supervised ML & XGBoost Explainability."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
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
                    <span class="status-chip status-closed">TRACKED IN MLFLOW</span>
                    <div style="font-size: 0.8rem; color: #68707A; margin-top: 4px;">Owner: <b>{insights.get('owner', 'zs7919320@gmail.com')}</b></div>
                </div>
            </div>
            <div style="margin-top: 10px; padding: 6px 12px; background: #FEF3C7; border-left: 3px solid #D97706; border-radius: 4px; font-size: 0.8rem; color: #92400E;">
                <b>MLflow Run Status:</b> Baseline evaluation metrics recorded in MLflow run <code>{insights.get('run_name', 'aml_xgboost_final')}</code>. (Note: Registry write to Unity Catalog requires UC Model Registry permissions).
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Hyperparameters Pill Bar
    if hp:
        st.markdown(f"""
            <div class="neo-card-sm" style="background: #F8FAFC; padding: 12px 18px; margin-bottom: 16px; border: 1px solid #E2E8F0; border-radius: 8px;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #1E3A8A; margin-bottom: 6px;">TUNED HYPERPARAMETERS (MLFLOW LOGGED):</div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px; font-size: 0.82rem; color: #374151;">
                    <span class="code-pill">n_estimators: {hp.get('n_estimators', 300)}</span>
                    <span class="code-pill">max_depth: {hp.get('max_depth', 6)}</span>
                    <span class="code-pill">learning_rate: {hp.get('learning_rate', 0.05)}</span>
                    <span class="code-pill">subsample: {hp.get('subsample', 0.8)}</span>
                    <span class="code-pill">colsample_bytree: {hp.get('colsample_bytree', 0.8)}</span>
                    <span class="code-pill">scale_pos_weight: {hp.get('scale_pos_weight', 20.35)}</span>
                    <span class="code-pill">neg_to_pos_ratio: {hp.get('negative_to_positive_ratio', '20:1')}</span>
                    <span class="code-pill" style="background: #FEF3C7; color: #92400E; font-weight: 700;">classification_threshold: {hp.get('classification_threshold', 0.98)}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # 3. Class Population Summary Card
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

    # 4. Core Holdout Evaluation Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("RECALL (DETECTION)", f"{metrics['recall']*100:.1f}%", "Caught 249 of 274 fraud cases", trend_positive=True, alert_level="success")
    with c2:
        render_kpi_card("ROC-AUC", f"{metrics['roc_auc']*100:.1f}%", "Strong class separation", trend_positive=True, alert_level="success")
    with c3:
        render_kpi_card("PR-AUC", f"{metrics['pr_auc']*100:.1f}%", "Key imbalanced metric", trend_positive=True, alert_level="success")
    with c4:
        render_kpi_card("PRECISION", f"{metrics['precision']*100:.1f}%", "2,372 false positives (0.98 threshold)", trend_positive=False, alert_level="warning")

    # 5. Operational Trade-Off Callout
    st.markdown("""
        <div style="background: #EFF6FF; border-left: 4px solid #2563EB; padding: 12px 16px; margin: 16px 0; border-radius: 4px; font-size: 0.86rem; color: #1E40AF;">
            <b>Operational Context:</b> High recall (<b>90.9%</b>) ensures investigators capture the vast majority of money laundering schemes. 
            The low precision (<b>9.5%</b>) reflects the extreme real-world class imbalance (20:1) and the conservative <b>0.98 threshold</b> configured to minimize false negatives (missed fraud).
        </div>
    """, unsafe_allow_html=True)

    # 6. Visualizations: Feature Importance (Gain) & Confusion Matrix
    col_feat, col_matrix = st.columns([1.4, 1])

    with col_feat:
        st.markdown('<div class="neo-card" style="padding: 20px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.95rem; font-weight: 700; color: #1E3A8A; margin-bottom: 6px;">XGBOOST FEATURE IMPORTANCE (GAIN)</div>', unsafe_allow_html=True)
        st.caption("Relative information gain per engineered feature from ml_training_data.")
        
        df_feat = pd.DataFrame(insights["feature_importance"])
        df_feat = df_feat.sort_values(by="importance", ascending=True)
        
        fig_feat = go.Figure(go.Bar(
            x=df_feat["importance"],
            y=df_feat["feature"],
            orientation='h',
            marker_color='#1E3A8A',
            text=[f"{val*100:.1f}%" for val in df_feat["importance"]],
            textposition='outside'
        ))
        fig_feat.update_layout(
            margin=dict(l=10, r=40, t=10, b=20),
            height=310,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title="Relative Information Gain", range=[0, 0.35], showgrid=True, gridcolor="#DFE4EA"),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_feat, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_matrix:
        st.markdown('<div class="neo-card" style="padding: 20px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.95rem; font-weight: 700; color: #1E3A8A; margin-bottom: 6px;">HOLDOUT CONFUSION MATRIX</div>', unsafe_allow_html=True)
        st.caption("Holdout evaluation: 249 caught fraud vs 2,372 false alarms.")

        cm = insights["confusion_matrix"]
        cm_data = [
            [cm["true_negative"], cm["false_positive"]],
            [cm["false_negative"], cm["true_positive"]]
        ]
        
        fig_cm = go.Figure(data=go.Heatmap(
            z=cm_data,
            x=['Predicted Legitimate', 'Predicted Laundering'],
            y=['Actual Legitimate', 'Actual Laundering'],
            colorscale=[[0, '#F1F4F8'], [1, '#1E3A8A']],
            showscale=False,
            text=[[f"{cm['true_negative']:,}", f"{cm['false_positive']:,}"],
                  [f"{cm['false_negative']:,}", f"{cm['true_positive']:,}"]],
            texttemplate="%{text}",
            textfont={"size": 14, "color": "white"}
        ))
        fig_cm.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            height=310,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_cm, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
