# 🔐 VisaNet Authorization Performance Pipeline

This project simulates a real-world authorization monitoring pipeline, inspired by how VisaNet tracks transaction approval and decline rates daily to ensure reliability and detect anomalies such as fraud or issuer outages.

Built with Python, Apache Airflow, and Tableau, it demonstrates end-to-end orchestration of data workflows — from ingestion and transformation to KPI visualization and business insights.

## Overview

Simulates daily merchant transaction data (approved and declined)

Automates KPI calculations using Python ETL scripts

Schedules workflows using Apache Airflow

Stores outputs as CSV files for analysis

Visualizes key metrics in Tableau

## Project Structure
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

## How It Works
## 1. Simulated Dataset

daily_transactions.csv represents four days of merchant transactions with fields such as status, amount, and timestamp.

## 2. Python DAG (auth_pipeline_dag.py)

Reads transaction data

Calculates approved and declined counts

Derives daily approval rate (%)

Saves the aggregated results to daily_approval_summary.csv

## 3. Apache Airflow

Orchestrates and schedules the ETL pipeline daily

Automates data refresh and ensures reproducibility

## 4. Tableau Dashboard

Visualizes approval vs. decline trends

Highlights performance KPIs and potential anomalies


## 📊 Volume Trend Comparison
<img src="airflow_dags/images/volume_trend_comparison.png" alt="Volume Trend Comparison" width="600"/>


## Key Performance Indicators (KPIs)

Metric	Description
Approval Rate (%)	Ratio of approved to total transactions
Decline Rate (%)	Ratio of declined to total transactions
Transaction Volume	Total number of daily transactions
Decline Spike Alert	Highlights abnormal decline patterns



## Business Value

Provides daily transparency into transaction health

Detects issuer or merchant decline surges in near real time

Supports fraud and operations teams with actionable insights

Establishes a foundation for scalable VisaNet-style monitoring pipelines

## What I Learned

Designing and automating ETL workflows with Apache Airflow

Writing modular Python and Pandas scripts for KPI computation

Translating engineering output into business metrics

Creating clear, data-driven dashboards with Tableau

Managing workflow code with Git and GitHub

## Challenges Faced

Generating realistic merchant transaction data

Handling dynamic metric calculations from raw input

Rendering Tableau screenshots cleanly on GitHub

Balancing dashboard clarity with analytical depth

## Next Steps

Add email alerts for Airflow DAG failures or threshold breaches

Store data in Snowflake for cloud analytics scalability

Deploy a Streamlit interface for real-time monitoring

Integrate anomaly detection (Isolation Forest or Z-score analysis)

## Tech Stack

Python 3.10

Apache Airflow

Pandas

Tableau

Git / GitHub


## 🏁 Summary

This project bridges data engineering and business intelligence, demonstrating the ability to:

Automate and schedule production-style data workflows

Derive meaningful KPIs from raw transactional data

Present insights through clear, executive-ready visuals

It represents a complete end-to-end data pipeline, mirroring how real Visa authorization data would be processed and analyzed at scale.





