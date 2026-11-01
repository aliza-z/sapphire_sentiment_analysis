import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from budget_optimizer import recommend_budget

st.set_page_config(
    page_title="Sapphire Advertising Budget Optimizer",
    page_icon="📊",
    layout="wide"
)

st.title("Sapphire Digital Advertising Analysis")
st.caption("Campaign Performance & Marketing Budget Optimization")

# Load data
DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "data",
    "advertising_campaigns_with_metrics.csv"
)

df = pd.read_csv(DATA_PATH)
df['date'] = pd.to_datetime(df['date'])

# Sidebar
st.sidebar.header("Analysis Filters")

platforms = st.sidebar.multiselect(
    "Select Platforms",
    options=sorted(df['platform'].unique()),
    default=sorted(df['platform'].unique())
)

campaigns = st.sidebar.multiselect(
    "Select Campaigns",
    options=sorted(df['campaign'].unique()),
    default=sorted(df['campaign'].unique())
)

filtered = df[
    df['platform'].isin(platforms) &
    df['campaign'].isin(campaigns)
].copy()

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# Aggregate KPIs
impressions = filtered['impressions'].sum()
clicks = filtered['clicks'].sum()
spend = filtered['spend'].sum()
conversions = filtered['conversions'].sum()
revenue = filtered['revenue'].sum()

ctr = clicks / impressions * 100 if impressions else 0
cpc = spend / clicks if clicks else 0
cpa = spend / conversions if conversions else 0
roas = revenue / spend if spend else 0

# KPI cards
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Impressions", f"{impressions:,.0f}")
c2.metric("Total Clicks", f"{clicks:,.0f}")
c3.metric("Total Revenue", f"Rs. {revenue:,.0f}")
c4.metric("Total Spend", f"Rs. {spend:,.0f}")

c1, c2, c3, c4 = st.columns(4)

c1.metric("CTR", f"{ctr:.2f}%")
c2.metric("CPC", f"Rs. {cpc:.2f}")
c3.metric("CPA", f"Rs. {cpa:.2f}")
c4.metric("ROAS", f"{roas:.2f}x")

st.divider()

# Platform performance
st.subheader("Platform Performance")

platform_data = filtered.groupby('platform').agg({
    'impressions': 'sum',
    'clicks': 'sum',
    'spend': 'sum',
    'conversions': 'sum',
    'revenue': 'sum'
}).reset_index()

platform_data['ROAS'] = (
    platform_data['revenue'] / platform_data['spend']
)

platform_data['CTR'] = (
    platform_data['clicks'] /
    platform_data['impressions'] * 100
)

platform_data['CPC'] = (
    platform_data['spend'] / platform_data['clicks']
)

platform_data['CPA'] = (
    platform_data['spend'] / platform_data['conversions']
)

left, right = st.columns(2)

with left:
    fig = px.bar(
        platform_data,
        x='platform',
        y='revenue',
        title='Revenue by Platform',
        color='platform'
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.bar(
        platform_data,
        x='platform',
        y='ROAS',
        title='ROAS by Platform',
        color='platform'
    )
    st.plotly_chart(fig, use_container_width=True)

st.dataframe(platform_data, use_container_width=True)

st.divider()

# Campaign performance
st.subheader("Campaign Performance")

campaign_data = filtered.groupby('campaign').agg({
    'spend': 'sum',
    'revenue': 'sum',
    'clicks': 'sum',
    'conversions': 'sum'
}).reset_index()

fig = px.bar(
    campaign_data.sort_values('revenue', ascending=False),
    x='campaign',
    y='revenue',
    title='Revenue by Campaign',
    color='campaign'
)

st.plotly_chart(fig, use_container_width=True)

st.dataframe(campaign_data, use_container_width=True)

st.divider()

# Audience insights
st.subheader("Audience and Device Analysis")

left, right = st.columns(2)

with left:
    gender_data = filtered.groupby('gender')['conversions'].sum().reset_index()

    fig = px.pie(
        gender_data,
        names='gender',
        values='conversions',
        title='Conversions by Gender'
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    device_data = filtered.groupby('device')['conversions'].sum().reset_index()

    fig = px.bar(
        device_data,
        x='device',
        y='conversions',
        title='Conversions by Device'
    )

    st.plotly_chart(fig, use_container_width=True)

# Budget optimizer
st.divider()

st.subheader("Marketing Budget Recommendation Engine")

budget = st.number_input(
    "Enter your marketing budget (PKR)",
    min_value=10000,
    value=1000000,
    step=50000
)

if st.button("Generate Budget Recommendations"):

    recommendation_data = recommend_budget(filtered, budget)

    st.dataframe(
        recommendation_data[
            [
                'platform',
                'ROAS',
                'CPA',
                'Conversion_Rate',
                'Allocation_Percentage',
                'Recommended_Budget'
            ]
        ],
        use_container_width=True
    )

    fig = px.pie(
        recommendation_data,
        names='platform',
        values='Recommended_Budget',
        title='Recommended Budget Distribution'
    )

    st.plotly_chart(fig, use_container_width=True)

    csv = recommendation_data.to_csv(index=False).encode('utf-8')

    st.download_button(
        "Download Budget Recommendations",
        data=csv,
        file_name="budget_recommendations.csv",
        mime="text/csv"
    )

# Download filtered data
st.divider()

st.subheader("Export Analysis")

csv = filtered.to_csv(index=False).encode('utf-8')

st.download_button(
    "Download Filtered Advertising Data",
    data=csv,
    file_name="filtered_advertising_data.csv",
    mime="text/csv"
)

st.caption(
    "Note: This dashboard uses simulated advertising data for academic analysis. "
    "Recommendations are based on historical simulated performance, "
    "not actual advertising platform results."
)
