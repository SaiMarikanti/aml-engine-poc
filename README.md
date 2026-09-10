# AML Transaction Monitoring & Investigation Platform

An enterprise-grade, desktop-first **AML Transaction Monitoring and Investigation Platform** built on **Streamlit** and **Databricks Apps**, powered by a **Neumorphic UI Design System** with custom routing via `st.navigation(..., position="hidden")` and native integration with **Databricks SQL Warehouse** and **Unity Catalog Delta Tables**.

---

## 🏛️ Architecture & Platform Separation

The system strictly enforces clean architectural separation between distributed lakehouse pipelines and investigator interactions:

```
DATABRICKS LAKEHOUSE
S3 Raw ──► Bronze Ingestion ──► Silver Cleansing ──► Great Expectations DQ
                                                           │
                   ┌───────────────────────────────────────┴───────────────────────────────────────┐
                   ▼                                                                               ▼
        Deterministic Rule Engine (R001–R004)                                           GraphFrames Topology Pipeline
        • R001 High Value (>₹500)                                                       • Directed Cycle Detection
        • R002 Velocity Spikes                                                          • In/Out-Degree Centrality
        • R003 Fan-In Aggregation                                                       • Counterparty Clustering
        • R004 Fan-Out Distribution                                                                │
                   │                                                                               │
                   └───────────────────────────────────────┬───────────────────────────────────────┘
                                                           ▼
                                                ML Feature Engineering
                                                (1,323,234 transactions, 1,719 target fraud labels)
                                                           │
                                                           ▼
                                                XGBoost Supervised Training (v3)
                                                (PR-AUC, Confusion Matrix, Information Gain Importance)
                                                           │
                                                           ▼
                                                Unity Catalog Gold Delta Tables
                                                (aml_engine.aml_poc: gold_alerts, gold_transactions, gold_accounts)
                                                           │
═══════════════════════════════════════════════════════════╪══════════════════════════════════════════════════════════
DATABRICKS APP (INVESTIGATION WORKBENCH)                  │
                                                           ▼
                                                Databricks SQL Warehouse
                                                (Resource key: sql-warehouse via OAuth M2M)
                                                           │
                                                           ▼
                                                AMLDataService Routing Facade
                                                           │
                   ┌───────────────────────────────────────┴───────────────────────────────────────┐
                   ▼                                                                               ▼
       st.navigation(position="hidden")                                                Case Management State
       + Neumorphic Shell (Sidebar & Header)                                           (Delta Writeback Tables)
       • Dashboard (Surveillance KPIs & Trends)                                        • app_alert_status
       • Transactions (Indexed Ledger & Multi-Detector)                                • app_alert_comments
       • Alert Center & Deep Investigation Workbench                                   • app_audit_log
       • Account 360 Risk Profiles
       • GraphFrames Network Topology (PyVis)
       • XGBoost Model Performance & Explainability
       • Compliance Audit Trail
       • Technical Health & System Status
```

---

## 📁 Repository Structure

```text
aml/
├── databricks/
│   ├── bronze/           # Raw S3 ingestion & bronze setup
│   ├── silver/           # Silver accounts, alerts, transactions, and data quality
│   ├── rules/            # Deterministic rule engine notebooks
│   ├── graph/            # GraphFrames cycle and fan-in/fan-out motifs
│   ├── ml/               # XGBoost training, feature engineering, and evaluation
│   └── gold/             # Gold analytics view specifications
│
├── streamlit_app/
│   ├── app.py            # Central application shell & st.navigation router
│   ├── app.yaml          # Databricks Apps manifest & sql-warehouse resource
│   ├── requirements.txt  # Core dependencies
│   │
│   ├── views/            # Isolated view renderers (replaces legacy pages/)
│   │   ├── dashboard.py
│   │   ├── transactions.py
│   │   ├── alerts.py
│   │   ├── accounts.py
│   │   ├── network.py
│   │   ├── model_insights.py
│   │   ├── audit.py
│   │   └── system_status.py
│   │
│   ├── components/       # Custom Neumorphic components
│   │   ├── sidebar.py    # Controlled Neumorphic sidebar navigation
│   │   ├── header.py     # Global search & high-risk notification topbar
│   │   ├── kpi_card.py
│   │   ├── alert_card.py
│   │   ├── filters.py
│   │   └── network_graph.py
│   │
│   ├── services/         # Domain data services & Databricks connector
│   │   ├── databricks.py
│   │   ├── transactions.py
│   │   ├── alerts.py
│   │   ├── accounts.py
│   │   ├── network.py
│   │   └── data_service.py
│   │
│   ├── styles/
│   │   └── neumorphism.css
│   │
│   └── .streamlit/
│       └── config.toml
│
├── tests/
└── README.md
```

---

## 🧭 Navigation Architecture: `st.navigation(position="hidden")`

The application adopts Streamlit's official modern router pattern:
1. **Centralized Router**: `st.Page` definitions are configured centrally in `app.py`.
2. **Hidden Built-In Menu**: `st.navigation(..., position="hidden")` suppresses the automatic Streamlit sidebar menu.
3. **Dedicated Neumorphic Sidebar**: `components/sidebar.py` completely controls navigation rendering, active-state inset surfaces, deep navy accent bars, and page transitions via `st.switch_page`.
4. **No Legacy `pages/` Collision**: All views reside in `streamlit_app/views/`, eliminating legacy automatic page discovery.

---

## 🎨 Neumorphic Design Principles

- **Base Surface**: `#E8ECF1` light gray-blue.
- **Cards**: Soft raised surfaces with dual-component drop shadows (`8px 8px 16px #C5CBD4, -8px -8px 16px #FFFFFF`).
- **Inputs**: Inset dual-shadow indentation for search bars and filters.
- **Active Navigation State**: Soft inset surface with a deep navy accent (`border-left: 4px solid #1E3A8A`) and bold font, avoiding loud alarming colors for regular navigation.
- **Alert Colors**: Red (`#DC2626` / `#991B1B`) is strictly reserved for high-severity risk indicators (`CRITICAL`, `HIGH`, `FAILED`, `ESCALATED`).
- **Data Tables**: Clean contrast and bordered cells for maximum forensic readability.

---

## 🚀 Running Locally & Deploying to Databricks Apps

### Local Development
```bash
# Install dependencies
pip install -r streamlit_app/requirements.txt pytest

# Run automated tests
python -m pytest

# Start Streamlit application
python -m streamlit run streamlit_app/app.py --server.port 8501
```

### Databricks Apps Packaging
Package the application for deployment to Databricks Apps:
```bash
python package_apps.py
```
This generates `aml-investigation-app.zip` excluding local databases, cache files, and credentials. In Databricks Apps, the application automatically authorizes via the service principal and connects to the Serverless SQL Warehouse defined in `app.yaml`.
