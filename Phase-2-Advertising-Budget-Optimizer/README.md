# Phase 2 — Digital Advertising Budget Optimizer

## Project Overview

This project develops a Digital Advertising Budget Optimizer to analyze advertising campaign performance and recommend an effective distribution of a PKR 1,000,000 marketing budget across Facebook, Instagram, Google, TikTok and YouTube.

The project uses simulated advertising data to demonstrate data processing, campaign analytics, big data scalability and performance-based budget optimization.

## Dataset

The dataset contains the following attributes:

- Date
- Campaign
- Platform
- Impressions
- Clicks
- Spend
- Conversions
- Revenue
- Age
- Gender
- City
- Device

Four workload sizes are considered: 10,000, 100,000, 1 million and 10 million records. Larger workloads are generated through sampling with replacement from the original simulated dataset. They represent synthetic scaling experiments, not additional real-world observations.

## Performance Metrics

The project calculates:

- Click-Through Rate (CTR)
- Cost Per Click (CPC)
- Cost Per Acquisition (CPA)
- Conversion Rate
- Return on Ad Spend (ROAS)
- Total Revenue

## Big Data Processing

The project compares three processing approaches:

1. Pandas — chunk-based data processing.
2. MapReduce — local mapper and reducer implementation.
3. Apache Spark — distributed-processing framework evaluated in local mode.

Execution time is measured across increasing dataset sizes using the same platform-level aggregation task.

## Budget Recommendation Engine

A performance-based recommendation engine allocates a PKR 1,000,000 marketing budget across advertising platforms.

The recommendation score considers ROAS, conversion rate and CPA efficiency. Minimum and maximum allocation constraints help maintain diversification.

## Dashboard

The Streamlit dashboard provides:

- Advertising performance KPIs
- Platform comparisons
- Campaign performance analysis
- Audience and device insights
- Interactive filtering
- Budget recommendations
- Downloadable analytical results

## Technology Stack

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Apache Spark (PySpark)
- Streamlit
- Plotly
- Google Colab

## Project Limitations

The advertising dataset is simulated. The scaling experiment uses synthetic expanded workloads, while MapReduce is implemented locally and Spark runs in local mode. Therefore, the results demonstrate comparative processing behavior in the available environment rather than performance on a production distributed cluster.

## Conclusion

The project combines advertising analytics, scalable data processing and budget optimization to demonstrate how historical campaign performance can support more informed marketing allocation decisions.
