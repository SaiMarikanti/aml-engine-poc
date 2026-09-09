# AML Transaction Monitoring & Investigation Platform

An enterprise-grade, desktop-first **AML Transaction Monitoring and Investigation Platform** built using **Streamlit**, **Python**, **Plotly**, and **PyVis**, powered by a **Neumorphic UI Design System** and designed for direct integration with **Databricks SQL Warehouse** and **Unity Catalog Delta Tables**.

---

## 🏛️ Architecture & Platform Separation

The system strictly enforces a clean architectural separation between distributed analytics and investigator interactions:

```
AML PLATFORM DATA PROCESSING (Databricks Lakehouse)
S3 Raw ──► Bronze Ingestion ──► Silver Cleansing ──► Great Expectations DQ
                                                              │
                     ┌────────────────────────────────────────┴────────────────────────────────────────┐
                     ▼                                                                                 ▼
          Traditional Rule Engine (R001–R004)                                           GraphFrames & Temporal Cycles
          • R001 High Value (>₹500)                                                     • Directed Cycle Detection
          • R002 Velocity Spikes                                                        • In/Out-Degree Centrality
          • R003 Fan-In Aggregation                                                     • Counterparty Clustering
          • R004 Fan-Out Distribution                                                                  │
                     │                                                                                 │
                     └────────────────────────────────────────┬────────────────────────────────────────┘
                                                              ▼
                                                   ML Feature Engineering
                                                   (1,323,234 transactions, 1,719 target fraud labels)
                                                              │
                                                              ▼
                                                   XGBoost Batch Training & MLflow
                                                   (PR-AUC, Confusion Matrix, Gain Importance)
                                                              │
                                                              ▼
                                                   Unity Catalog Batch Scoring
                                                   • rule_score (40%) + ml_probability (60%) = final_risk_score
                                                              │
                                                              ▼
                                                   Gold Delta Tables (Read-Only to UI)
                                                   • gold_aml_risk / gold_account_risk / gold_alerts
                                                              │
══════════════════════════════════════════════════════════════╪══════════════════════════════════════════════════════════
APPLICATION & INVESTIGATION LAYER (Streamlit UI)              │
                                                              ▼
                                                   Databricks SQL Warehouse
                                                              │
                 ┌────────────────────────────────────────────┴────────────────────────────────────────────┐
                 ▼                                                                                         ▼
      Databricks SQL Connector                                                              Local Development Adapter
      (Production Unity Catalog Mode)                                                       (Deterministic Local Lakehouse)
                 │                                                                                         │
                 └────────────────────────────────────────────┬────────────────────────────────────────────┘
                                                              ▼
                                                   AMLDataService Routing Facade
                                                              │
                     ┌────────────────────────────────────────┴────────────────────────────────────────┐
                     ▼                                                                                 ▼
          Investigator Presentation                                                         Case Management State
          • Monitoring Center KPIs                                                          (Separate App Writeback Tables)
          • Multi-Detector Transaction Explorer                                             • app_alert_status
          • Deep Alert Triage Workbench                                                     • app_alert_comments
          • Account 360 Risk Profiles                                                       • app_audit_log
          • PyVis Graph Network Canvas
          • XGBoost Model Performance & Gain Charts
          • Batch Pipeline Status Dashboard
```

---

## 🔍 Dataset Verification & Imbalance Characteristics

The verified surveillance dataset contains:
- **Total Transactions**: 1,323,234 rows across simulated event time 0–199.
- **Fraud Positives**: Exactly 1,719 transactions (`IS_FRAUD = True`).
- **Class Imbalance**: ~0.1299% positive rate (1 fraud case per 769 legitimate transactions).
- **Alert Population**: Exactly 1,719 alert records corresponding 1-to-1 with fraud transactions across 391 unique `ALERT_ID` incident clusters:
  - `cycle` = 936 transactions
  - `fan_in` = 783 transactions
- **Accounts**: 10,000 profiled accounts.

---

## 🎨 Neumorphic Design System

The visual language models a precision financial intelligence control panel:
- **Base Surface**: `#E8ECF1`
- **Raised Cards**: Dual light and dark drop shadows (`8px 8px 16px #c8ced6, -8px -8px 16px #ffffff`)
- **Inset Inputs**: Inner shadow indentation for search and filter bars
- **High-Contrast Semantic Risk Chips**:
  - **LOW**: `#059669` (Soft Green)
  - **MEDIUM**: `#D97706` (Amber)
  - **HIGH**: `#DC2626` (Crimson Red)
  - **CRITICAL**: `#991B1B` (Dark Wine Red)

---

## 🚀 Application Navigation & Modules

| Section | Page | Description |
| :--- | :--- | :--- |
| **HOME** | **Dashboard** | Monitoring Center, KPIs, surveillance time trends, risk severity breakdown, and recent alerts. |
| **INVESTIGATION** | **Transactions** | Parameterized search across 1.32M transactions; multi-detector (Rule Engine, Graph, ML) evidence breakdown with composite formula. |
| **INVESTIGATION** | **Alerts** | Work queue, alert triage, status transitions (`UNDER REVIEW`, `CONFIRMED`, `FALSE POSITIVE`, `CLOSED`), assignee management, notes write-back. |
| **INVESTIGATION** | **Accounts** | Account 360 profile, centrality risk metrics, incoming/outgoing volume, detected systemic risk factors. |
| **INVESTIGATION** | **Network** | Interactive PyVis physics graph rendering precomputed GraphFrames topologies, circular cycles, and money mule hubs. |
| **INTELLIGENCE** | **Model Insights** | XGBoost model registry metadata, holdout confusion matrix, PR-AUC, and Gain Feature Importance chart. |
| **ADMINISTRATION** | **Audit Log** | Immutable case management trail capturing investigator actions, timestamp, previous/new states with CSV export. |
| **ADMINISTRATION** | **System Status** | Operational health dashboard across Batch Lakehouse stages (Bronze -> Silver -> DQ -> Rules -> Graph -> ML -> Gold). |

---

## 💻 Quickstart

### 1. Install Dependencies
```bash
pip install -r aml_app/requirements.txt
```

### 2. Run Automated Tests
```bash
pytest
```

### 3. Launch Platform
```bash
python -m streamlit run aml_app/app.py --server.port 8501
```
Or double click `run_app.bat`.

---

## ⚙️ Configuration (Databricks Cloud Mode)

To connect directly to your Databricks SQL Warehouse:
```bash
export DATABRICKS_HOST="dbc-xxxx.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi..."
export DATABRICKS_HTTP_PATH="/sql/1.0/warehouses/xxxx"
export DATABRICKS_CATALOG="main"
export DATABRICKS_SCHEMA="aml_gold"
export FORCE_LOCAL_LAKEHOUSE="false"
```
When credentials are not configured, the application automatically runs in **Local Development Adapter Mode** using the pre-indexed local lakehouse with zero random numbers.
