"""Model Insights View - Supervised ML & XGBoost Explainability."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
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

    # Model Overview Card
    st.markdown(f"""
        <div class="neo-card" style="padding: 20px 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0; font-size: 1.3rem; font-weight: 800; color: #1E3A8A;">{insights['model_name']}</h3>
                    <div style="color: #68707A; font-size: 0.88rem; margin-top: 4px;">
                        Model Version: <b style="color: #20242A;">{insights['model_version']}</b> 
                        • Engine: <b>{insights['model_type']}</b> 
                        • Target: <code>transactions.IS_FRAUD</code>
                    </div>
                </div>
                <div style="text-align: right;">
                    <span class="status-chip status-closed">REGISTERED IN UNITY CATALOG</span>
                    <div style="font-size: 0.8rem; color: #68707A; margin-top: 4px;">Surveillance Baseline: <b>v3</b></div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Class Population Summary Card
    st.markdown(f"""
        <div class="neo-card-sm" style="display: flex; justify-content: space-between; align-items: center; background: #F8FAFC; margin-bottom: 18px;">
            <div style="font-size: 0.84rem; color: #4B5563;">
                <b>Surveillance Population:</b> {ds['total_transactions']:,} transactions 
                (<span style="color: #059669; font-weight: 600;">{ds['negative_count']:,} Legitimate</span> vs 
                 <span style="color: #DC2626; font-weight: 700;">{ds['positive_count']:,} Confirmed Laundering</span>)
            </div>
            <div style="font-size: 0.84rem; color: #1E3A8A; font-weight: 700;">
                Imbalance Ratio: {ds['imbalance_ratio']}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Core Metrics: Precision, Recall, F1, PR-AUC
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("PRECISION", f"{metrics['precision']*100:.1f}%", "Controlled false positive rate", trend_positive=True)
    with c2:
        render_kpi_card("RECALL (DETECTION)", f"{metrics['recall']*100:.1f}%", "89.5% fraud captured", trend_positive=True, alert_level="success")
    with c3:
        f1_score = 2 * (metrics['precision'] * metrics['recall']) / (metrics['precision'] + metrics['recall']) if (metrics['precision'] + metrics['recall']) > 0 else 0.0
        render_kpi_card("F1-SCORE", f"{f1_score:.3f}", "Harmonic balance on holdout", trend_positive=True)
    with c4:
        render_kpi_card("PR-AUC", f"{metrics['pr_auc']:.3f}", "Primary metric for class imbalance", trend_positive=True, alert_level="success")

    # Visualizations: Feature Importance (Gain) & Confusion Matrix
    col_feat, col_matrix = st.columns([1.4, 1])

    with col_feat:
        st.markdown('<div class="neo-card" style="padding: 20px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.95rem; font-weight: 700; color: #1E3A8A; margin-bottom: 6px;">XGBOOST FEATURE IMPORTANCE (GAIN)</div>', unsafe_allow_html=True)
        st.caption("Relative information gain per engineered feature.")
        
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
        st.caption("Classification outcomes on out-of-time test dataset.")

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
