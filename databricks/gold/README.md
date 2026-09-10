# Databricks Gold Lakehouse Layer

This directory represents the Gold Analytics layer of the AML Lakehouse Platform.
The gold layer joins and aggregates Silver tables (`silver_accounts`, `silver_transactions`, `silver_alerts`), Rule Engine outputs (`rule_results`), GraphFrames topology motifs (`graph_results`), and XGBoost inferences (`ml_scores`).

## Target Tables & Views (`aml_engine.aml_poc`)
- `gold_alerts`: Primary triage view combining composite risk scores and detector flags.
- `gold_transactions`: Indexed transactions with counterparty enrichment.
- `gold_accounts`: Account 360 profiling and centrality metrics.
- `gold_network`: Precomputed GraphFrames edge lists and vertex degrees for PyVis visualization.
- `app_alert_status`: Case management workflow states (`OPEN`, `UNDER REVIEW`, `CONFIRMED`, `FALSE POSITIVE`, `CLOSED`).
- `app_alert_comments`: Chronological investigator audit commentary.
- `app_audit_log`: Compliance audit trail.
