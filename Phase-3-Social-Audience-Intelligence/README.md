
# Phase 3: Pakistan Social Audience & Campaign Intelligence Engine

## Project Overview

This project focuses on discovering audience behaviour patterns and marketing opportunities from social media interactions.

Using a Pakistani fashion retail context, the system analyzes social media posts and comments across Instagram, Facebook, and TikTok. Unlike traditional sentiment classification, the main objective is to identify groups of audience needs, detect unusual engagement patterns, and generate practical marketing recommendations.

## Objectives

- Analyze engagement across different content types and campaigns.
- Discover audience needs using text clustering.
- Identify unusual social media engagement patterns.
- Understand audience interests across platforms.
- Generate recommendations for marketing decisions.

## Technologies Used

- Python
- Pandas and NumPy
- Scikit-learn
- TF-IDF Vectorization
- K-Means Clustering
- Isolation Forest
- Plotly
- Streamlit
- Google Colab

## Methodology

1. Dataset preparation and exploratory data analysis.
2. Text cleaning and preprocessing.
3. TF-IDF feature extraction.
4. K-Means clustering to discover audience segments.
5. Cluster evaluation and interpretation.
6. Isolation Forest for unusual engagement detection.
7. Marketing recommendation generation.
8. Interactive dashboard development using Streamlit.

## Dashboard Features

- Content performance analysis.
- Audience behaviour clusters.
- Unusual engagement detection.
- Campaign and platform insights.
- Marketing recommendations.
- Dataset quality overview.

## Project Structure

```text
Phase-3-Social-Audience-Intelligence/
├── data/
├── notebooks/
├── results/
├── app.py
├── requirements.txt
└── README.md
```

## How to Run

Install the required libraries:

```bash
pip install -r requirements.txt
```

Start the dashboard:

```bash
streamlit run app.py
```

## Dataset Limitation

The datasets used in this academic demonstration are simulated. They do not represent actual comments, customers, or measured campaign performance from Sapphire, Khaadi, Gul Ahmed, or other brands.

The project demonstrates how clustering and anomaly detection can be applied to social media marketing analysis. Its findings should not be interpreted as verified real-world customer behaviour.

## Conclusion

The project demonstrates how unsupervised machine learning can help identify audience needs, explore campaign patterns, and support data-driven marketing decisions.
