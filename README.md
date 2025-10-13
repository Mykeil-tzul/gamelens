VisaNet Authorization Performance Pipeline

This project simulates a real-world authorization monitoring pipeline, inspired by how payment networks like VisaNet track transaction approval and decline rates daily to ensure reliability and detect anomalies.

Built with Python, Apache Airflow, and Tableau, it demonstrates end-to-end orchestration of data workflows — from data ingestion and transformation to KPI visualization and insight delivery.

Overview

Simulate daily merchant transaction data (approved and declined)

Automate KPI calculations using Python ETL scripts

Schedule workflows using Apache Airflow

Save daily outputs as CSV for analysis

Build and visualize KPIs in Tableau

Project Structure

auth-approval-pipeline/
│
├── airflow_dags/
│   └── auth_pipeline_dag.py
│
├── data/
│   ├── daily_transactions.csv
│   └── daily_approval_summary.csv
│
├── dashboard/
│   └── Tableau_Screenshot.twb
│
├── images/
│   └── volume_trend_comparison.png
│
├── notebooks/
├── sql/
├── requirements.txt
└── README.md

How It Works
1. Simulated Dataset

daily_transactions.csv represents four days of merchant transactions with fields such as status, amount, and timestamp.

2. Python DAG (auth_pipeline_dag.py)

Reads the transaction dataset

Calculates approved and declined counts

Derives daily approval rate (%)

Saves the results to daily_approval_summary.csv

3. Apache Airflow

Orchestrates and schedules the ETL pipeline daily

Automates data refresh and reproducibility

4. Tableau Dashboard

Visualizes approval vs decline trends

Highlights performance KPIs and potential anomalies

Volume Trend Comparison
<img src="airflow_dags/images/volume_trend_comparison.png" alt="Volume Trend Comparison" width="600"/>
Key Performance Indicators (KPIs)
Metric	Description
Approval Rate (%)	Ratio of approved to total transactions
Decline Rate (%)	Ratio of declined to total transactions
Transaction Volume	Total daily transaction count
Decline Spike Alert	Highlights abnormal decline patterns
Business Value

Provides daily transparency into transaction health

Detects issuer or merchant decline surges in real time

Supports fraud and operations teams with actionable insights

Establishes a foundation for scalable VisaNet-style monitoring pipelines

What I Learned

Designing and automating ETL workflows with Apache Airflow

Writing modular Python and Pandas scripts for metric computation

Translating engineering output into business KPIs

Creating clear, data-driven dashboards in Tableau

Managing workflow code with Git and GitHub

Challenges Faced

Generating realistic merchant transaction data

Dynamically calculating metrics from raw CSV input

Rendering Tableau screenshots properly on GitHub

Balancing dashboard clarity with analytical depth

Next Steps

Add email alerts for Airflow DAG failures and threshold breaches

Migrate data storage to Snowflake for cloud scalability

Deploy a Streamlit interface for real-time monitoring

Integrate anomaly detection (Isolation Forest or Z-score analysis)

Tech Stack

Python 3.10

Apache Airflow

Pandas

Tableau

Git / GitHub

Author

Mykeil Tzul
LinkedIn
 | GitHub

Summary

This project bridges the gap between data engineering and business intelligence, demonstrating the ability to:

Automate and schedule production-style data workflows

Derive meaningful KPIs from raw transactional data

Present insights through clear, executive-ready visuals

It represents a complete end-to-end data pipeline, mirroring how real Visa authorization data would be processed and analyzed at scale.






