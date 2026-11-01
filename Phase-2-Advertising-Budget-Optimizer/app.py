
import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Sapphire Pakistan | Advertising Analysis",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# SAPPHIRE COLOR PALETTE
# --------------------------------------------------

NAVY = "#0B1F3A"
DEEP_NAVY = "#071426"
ROYAL_BLUE = "#4169E1"
BLUE_HOVER = "#3154C6"
BABY_BLUE = "#DCEEFF"
PALE_BLUE = "#EEF6FF"
WHITE = "#FFFFFF"

BLUE_PALETTE = [
    "#4169E1",
    "#6495ED",
    "#87CEEB",
    "#1D4ED8",
    "#A7C7E7",
    "#0B1F3A",
]

# --------------------------------------------------
# SIDEBAR: BRANDING AND THEME
# --------------------------------------------------

with st.sidebar:

    st.markdown(
        f"""
        <div style="padding:10px 0 20px 0;">
            <div style="font-size:30px;font-weight:800;
                        letter-spacing:2px;color:{ROYAL_BLUE};">
                SAPPHIRE
            </div>
            <div style="font-size:12px;letter-spacing:2px;
                        opacity:0.75;">
                PAKISTAN · ADVERTISING ANALYSIS
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Appearance")

    display_mode = st.radio(
        "Choose theme",
        ["Light", "Dark"],
        horizontal=True,
        key="display_mode"
    )

# --------------------------------------------------
# THEME SETTINGS
# --------------------------------------------------

if display_mode == "Dark":

    bg = DEEP_NAVY
    sidebar_bg = NAVY
    card_bg = "#102747"
    text_color = "#F4F8FF"
    muted_color = "#B3C7E5"
    border_color = "#24466F"
    soft_bg = "#142F52"
    plot_grid = "#24466F"

else:

    bg = PALE_BLUE
    sidebar_bg = BABY_BLUE
    card_bg = WHITE
    text_color = "#102747"
    muted_color = "#526987"
    border_color = "#C7DDF5"
    soft_bg = "#DCEEFF"
    plot_grid = "#DCE7F5"

# --------------------------------------------------
# CSS: MATCH PHASE 1
# --------------------------------------------------

st.markdown(
    f"""
    <style>
    :root {{
        color-scheme: {"dark" if display_mode == "Dark" else "light"};
        --primary-color: {ROYAL_BLUE};
    }}

    .stApp {{
        background: {bg};
        color: {text_color};
    }}

    [data-testid="stHeader"] {{
        background: {bg};
    }}

    [data-testid="stSidebar"] {{
        background: {sidebar_bg};
        border-right: 1px solid {border_color};
    }}

    [data-testid="stSidebar"] * {{
        color: {text_color};
    }}

    h1, h2, h3, h4, h5, p, label,
    [data-testid="stMarkdownContainer"] {{
        color: {text_color};
    }}

    [data-testid="stCaptionContainer"] {{
        color: {muted_color} !important;
    }}

    [data-testid="stMetric"] {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 14px;
        padding: 18px 20px;
    }}

    [data-testid="stMetricLabel"] {{
        color: {muted_color} !important;
    }}

    [data-testid="stMetricValue"] {{
        color: {text_color} !important;
        font-weight: 750;
    }}

    .stButton > button,
    .stDownloadButton > button {{
        background: {ROYAL_BLUE} !important;
        color: #FFFFFF !important;
        border: 1px solid {ROYAL_BLUE} !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
    }}

    .stButton > button:hover,
    .stDownloadButton > button:hover {{
        background: {BLUE_HOVER} !important;
        border-color: {BLUE_HOVER} !important;
        color: #FFFFFF !important;
    }}

    input, textarea {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border-color: {border_color} !important;
    }}

    [data-baseweb="select"] > div {{
        background-color: {card_bg} !important;
        border-color: {border_color} !important;
    }}

    [data-baseweb="select"] * {{
        color: {text_color} !important;
    }}

    [data-testid="stRadio"] label,
    [data-testid="stCheckbox"] label {{
        color: {text_color} !important;
    }}

    button[data-baseweb="tab"] {{
        color: {muted_color} !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {ROYAL_BLUE} !important;
        border-bottom-color: {ROYAL_BLUE} !important;
    }}

    [data-testid="stExpander"] {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 10px;
    }}

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {{
        border: 1px solid {border_color};
        border-radius: 10px;
        overflow: hidden;
    }}

    a {{
        color: {ROYAL_BLUE} !important;
    }}

    hr {{
        border-color: {border_color};
    }}

    .dashboard-header {{
        padding: 8px 0 22px 0;
    }}

    .eyebrow {{
        color: {ROYAL_BLUE} !important;
        font-size: 12px;
        font-weight: 750;
        letter-spacing: 2px;
        text-transform: uppercase;
    }}

    .dashboard-title {{
        color: {text_color} !important;
        font-size: 34px;
        line-height: 1.2;
        font-weight: 800;
        margin: 7px 0;
    }}

    .dashboard-subtitle {{
        color: {muted_color} !important;
        font-size: 15px;
        margin-top: 8px;
    }}

    .section-heading {{
        color: {text_color} !important;
        font-size: 20px;
        font-weight: 750;
        margin: 8px 0 14px 0;
    }}

    .info-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
    }}

    .info-card p {{
        color: {muted_color} !important;
        margin-bottom: 0;
    }}

    .info-card strong {{
        color: {text_color};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "advertising_campaigns_with_metrics.csv"
)

BENCHMARK_FILE = os.path.join(
    BASE_DIR,
    "results",
    "benchmark_results.csv"
)


@st.cache_data
def load_data(path):
    return pd.read_csv(path)


if not os.path.exists(DATA_FILE):

    st.error("Advertising dataset not found.")

    st.info(
        "Place advertising_campaigns_with_metrics.csv "
        "inside the data folder."
    )

    st.stop()

try:
    df = load_data(DATA_FILE)

except Exception as exc:

    st.error(f"Could not load dataset: {exc}")
    st.stop()


required_columns = [
    "date", "campaign", "platform",
    "impressions", "clicks", "spend",
    "conversions", "revenue"
]

missing = [
    column for column in required_columns
    if column not in df.columns
]

if missing:
    st.error("Missing columns: " + ", ".join(missing))
    st.stop()

df["date"] = pd.to_datetime(df["date"], errors="coerce")

numeric_columns = [
    "impressions", "clicks", "spend",
    "conversions", "revenue"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column], errors="coerce"
    ).fillna(0)

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

with st.sidebar:

    st.divider()

    st.markdown("### Dashboard Filters")

    platforms = ["All platforms"] + sorted(
        df["platform"].dropna().unique().tolist()
    )

    selected_platform = st.selectbox(
        "Advertising platform",
        platforms
    )

    campaigns = ["All campaigns"] + sorted(
        df["campaign"].dropna().unique().tolist()
    )

    selected_campaign = st.selectbox(
        "Campaign",
        campaigns
    )

    cities = ["All cities"]

    if "city" in df.columns:
        cities += sorted(
            df["city"].dropna().unique().tolist()
        )

    selected_city = st.selectbox(
        "Target city",
        cities
    )

    devices = ["All devices"]

    if "device" in df.columns:
        devices += sorted(
            df["device"].dropna().unique().tolist()
        )

    selected_device = st.selectbox(
        "Device",
        devices
    )

    st.divider()

    st.caption(f"{len(df):,} advertising records loaded")
    st.caption("Sapphire Pakistan · Advertising analysis")

# Apply filters

filtered_df = df.copy()

if selected_platform != "All platforms":
    filtered_df = filtered_df[
        filtered_df["platform"] == selected_platform
    ]

if selected_campaign != "All campaigns":
    filtered_df = filtered_df[
        filtered_df["campaign"] == selected_campaign
    ]

if selected_city != "All cities" and "city" in df.columns:
    filtered_df = filtered_df[
        filtered_df["city"] == selected_city
    ]

if selected_device != "All devices" and "device" in df.columns:
    filtered_df = filtered_df[
        filtered_df["device"] == selected_device
    ]

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def section_title(title, subtitle=None):

    st.markdown(
        f'<div class="section-heading">{title}</div>',
        unsafe_allow_html=True
    )

    if subtitle:
        st.caption(subtitle)


def style_fig(fig, height=360):

    fig.update_layout(
        height=height,
        paper_bgcolor=card_bg,
        plot_bgcolor=card_bg,
        font=dict(
            family="Arial, sans-serif",
            color=text_color,
            size=12
        ),
        colorway=BLUE_PALETTE,
        margin=dict(l=20, r=20, t=45, b=20),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=text_color)
        ),
        title_font=dict(color=text_color, size=16),
        xaxis=dict(
            gridcolor=plot_grid,
            zerolinecolor=plot_grid,
            tickfont=dict(color=muted_color),
            title_font=dict(color=muted_color)
        ),
        yaxis=dict(
            gridcolor=plot_grid,
            zerolinecolor=plot_grid,
            tickfont=dict(color=muted_color),
            title_font=dict(color=muted_color)
        )
    )

    return fig


def metric_card(label, value, help_text=None):
    st.metric(label=label, value=value, help=help_text)


def aggregate_platform(data):

    summary = data.groupby("platform").agg({
        "impressions": "sum",
        "clicks": "sum",
        "spend": "sum",
        "conversions": "sum",
        "revenue": "sum"
    }).reset_index()

    summary["CTR"] = np.where(
        summary["impressions"] > 0,
        summary["clicks"] / summary["impressions"] * 100,
        0
    )

    summary["CPC"] = np.where(
        summary["clicks"] > 0,
        summary["spend"] / summary["clicks"],
        0
    )

    summary["CPA"] = np.where(
        summary["conversions"] > 0,
        summary["spend"] / summary["conversions"],
        0
    )

    summary["Conversion_Rate"] = np.where(
        summary["clicks"] > 0,
        summary["conversions"] / summary["clicks"] * 100,
        0
    )

    summary["ROAS"] = np.where(
        summary["spend"] > 0,
        summary["revenue"] / summary["spend"],
        0
    )

    return summary


def recommend_budget(data, budget):

    summary = aggregate_platform(data)

    if len(summary) == 0:
        return summary

    summary["ROAS_Score"] = (
        summary["ROAS"] / summary["ROAS"].max()
        if summary["ROAS"].max() > 0 else 0
    )

    summary["Conversion_Score"] = (
        summary["Conversion_Rate"] /
        summary["Conversion_Rate"].max()
        if summary["Conversion_Rate"].max() > 0 else 0
    )

    positive_cpa = summary.loc[
        summary["CPA"] > 0, "CPA"
    ]

    minimum_cpa = (
        positive_cpa.min()
        if not positive_cpa.empty else 0
    )

    summary["CPA_Score"] = np.where(
        summary["CPA"] > 0,
        minimum_cpa / summary["CPA"],
        0
    )

    summary["Performance_Score"] = (
        0.50 * summary["ROAS_Score"] +
        0.25 * summary["Conversion_Score"] +
        0.25 * summary["CPA_Score"]
    )

    # Equal weights if all scores are zero
    scores = summary["Performance_Score"].to_numpy(float)

    if scores.sum() == 0:
        scores = np.ones(len(summary))

    weights = scores / scores.sum()

    # Diversification constraints
    lower = np.full(len(weights), 0.10)
    upper = np.full(len(weights), 0.35)

    for _ in range(1000):

        weights = np.clip(weights, lower, upper)

        difference = 1 - weights.sum()

        if abs(difference) < 1e-10:
            break

        if difference > 0:
            eligible = weights < upper - 1e-10
        else:
            eligible = weights > lower + 1e-10

        if not eligible.any():
            break

        weights[eligible] += (
            difference *
            weights[eligible] /
            weights[eligible].sum()
        )

    summary["Allocation_Percentage"] = weights * 100

    summary["Recommended_Budget"] = (
        weights * budget
    ).round(0)

    difference = budget - summary["Recommended_Budget"].sum()

    if difference != 0:
        summary.loc[
            summary["Recommended_Budget"].idxmax(),
            "Recommended_Budget"
        ] += difference

    return summary


# --------------------------------------------------
# DASHBOARD HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="dashboard-header">
        <div class="eyebrow">SAPPHIRE PAKISTAN</div>
        <div class="dashboard-title">
            Digital Advertising Analysis
        </div>
        <div class="dashboard-subtitle">
            Understanding campaign performance and improving
            marketing budget allocation across digital platforms.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# --------------------------------------------------
# OVERVIEW METRICS
# --------------------------------------------------

total_impressions = filtered_df["impressions"].sum()
total_clicks = filtered_df["clicks"].sum()
total_spend = filtered_df["spend"].sum()
total_conversions = filtered_df["conversions"].sum()
total_revenue = filtered_df["revenue"].sum()

ctr = (
    total_clicks / total_impressions * 100
    if total_impressions else 0
)

cpc = (
    total_spend / total_clicks
    if total_clicks else 0
)

cpa = (
    total_spend / total_conversions
    if total_conversions else 0
)

roas = (
    total_revenue / total_spend
    if total_spend else 0
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    metric_card("Total impressions", f"{total_impressions:,.0f}")

with c2:
    metric_card("Total clicks", f"{total_clicks:,.0f}")

with c3:
    metric_card("Total revenue", f"Rs. {total_revenue:,.0f}")

with c4:
    metric_card("Total advertising spend", f"Rs. {total_spend:,.0f}")

c1, c2, c3, c4 = st.columns(4)

with c1:
    metric_card("CTR", f"{ctr:.2f}%")

with c2:
    metric_card("CPC", f"Rs. {cpc:.2f}")

with c3:
    metric_card("CPA", f"Rs. {cpa:.2f}")

with c4:
    metric_card("ROAS", f"{roas:.2f}x")

st.write("")

# --------------------------------------------------
# NAVIGATION TABS
# --------------------------------------------------

(
    overview_tab,
    platform_tab,
    campaign_tab,
    audience_tab,
    scaling_tab,
    budget_tab
) = st.tabs([
    "Overview",
    "Platform Analysis",
    "Campaign Analysis",
    "Audience Insights",
    "Big Data Experiment",
    "Budget Optimizer"
])

# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

with overview_tab:

    section_title(
        "Advertising overview",
        "A snapshot of performance across the selected campaigns and platforms."
    )

    platform_data = aggregate_platform(filtered_df)

    left, right = st.columns(2)

    with left:

        fig = px.pie(
            platform_data,
            names="platform",
            values="revenue",
            hole=0.62,
            color_discrete_sequence=BLUE_PALETTE,
            title="Revenue contribution by platform"
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color=card_bg, width=2))
        )

        st.plotly_chart(
            style_fig(fig),
            width="stretch",
            config={"displayModeBar": False}
        )

    with right:

        fig = px.bar(
            platform_data,
            x="platform",
            y="revenue",
            color="platform",
            text="revenue",
            color_discrete_sequence=BLUE_PALETTE,
            title="Revenue by platform"
        )

        fig.update_traces(
            textposition="outside",
            marker_line_width=0
        )

        fig.update_layout(showlegend=False)

        st.plotly_chart(
            style_fig(fig),
            width="stretch",
            config={"displayModeBar": False}
        )

    section_title("Quick findings")

    best_roas = platform_data.loc[
        platform_data["ROAS"].idxmax()
    ]

    highest_revenue = platform_data.loc[
        platform_data["revenue"].idxmax()
    ]

    insight1, insight2 = st.columns(2)

    with insight1:

        st.markdown(
            f"""
            <div class="info-card">
                <strong>Highest ROAS</strong>
                <p style="font-size:22px;margin-top:8px;">
                    {best_roas['platform']}
                </p>
                <p>
                    {best_roas['ROAS']:.2f}x return on advertising spend
                    in the selected data.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with insight2:

        st.markdown(
            f"""
            <div class="info-card">
                <strong>Highest revenue</strong>
                <p style="font-size:22px;margin-top:8px;">
                    {highest_revenue['platform']}
                </p>
                <p>
                    Rs. {highest_revenue['revenue']:,.0f}
                    in attributed revenue.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.download_button(
        "Download filtered advertising data",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="sapphire_advertising_data.csv",
        mime="text/csv",
        width="stretch"
    )


# --------------------------------------------------
# PLATFORM ANALYSIS
# --------------------------------------------------

with platform_tab:

    section_title(
        "Platform performance",
        "Compare advertising efficiency and returns across platforms."
    )

    platform_data = aggregate_platform(filtered_df)

    metric_options = {
        "Revenue": "revenue",
        "ROAS": "ROAS",
        "CTR": "CTR",
        "CPC": "CPC",
        "CPA": "CPA",
        "Conversions": "conversions"
    }

    selected_metric = st.selectbox(
        "Select performance metric",
        list(metric_options.keys())
    )

    fig = px.bar(
        platform_data,
        x="platform",
        y=metric_options[selected_metric],
        color="platform",
        text=metric_options[selected_metric],
        color_discrete_sequence=BLUE_PALETTE,
        title=f"{selected_metric} by platform"
    )

    fig.update_traces(
        textposition="outside",
        marker_line_width=0
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(
        style_fig(fig, 400),
        width="stretch",
        config={"displayModeBar": False}
    )

    section_title("Platform comparison")

    st.dataframe(
        platform_data.round(2),
        width="stretch",
        hide_index=True
    )

    st.download_button(
        "Download platform summary",
        data=platform_data.to_csv(index=False).encode("utf-8"),
        file_name="platform_performance.csv",
        mime="text/csv",
        width="stretch"
    )


# --------------------------------------------------
# CAMPAIGN ANALYSIS
# --------------------------------------------------

with campaign_tab:

    section_title(
        "Campaign performance",
        "Identify campaigns contributing most to advertising results."
    )

    campaign_data = filtered_df.groupby("campaign").agg({
        "spend": "sum",
        "revenue": "sum",
        "clicks": "sum",
        "conversions": "sum",
        "impressions": "sum"
    }).reset_index()

    campaign_data["ROAS"] = np.where(
        campaign_data["spend"] > 0,
        campaign_data["revenue"] / campaign_data["spend"],
        0
    )

    left, right = st.columns(2)

    with left:

        fig = px.bar(
            campaign_data.sort_values("revenue", ascending=False),
            x="campaign",
            y="revenue",
            color_discrete_sequence=[ROYAL_BLUE],
            title="Revenue by campaign"
        )

        fig.update_traces(marker_line_width=0)

        st.plotly_chart(
            style_fig(fig, 420),
            width="stretch",
            config={"displayModeBar": False}
        )

    with right:

        fig = px.bar(
            campaign_data.sort_values("ROAS", ascending=False),
            x="campaign",
            y="ROAS",
            color_discrete_sequence=[ROYAL_BLUE],
            title="ROAS by campaign"
        )

        fig.update_traces(marker_line_width=0)

        st.plotly_chart(
            style_fig(fig, 420),
            width="stretch",
            config={"displayModeBar": False}
        )

    st.dataframe(
        campaign_data.round(2),
        width="stretch",
        hide_index=True
    )

    st.download_button(
        "Download campaign summary",
        data=campaign_data.to_csv(index=False).encode("utf-8"),
        file_name="campaign_performance.csv",
        mime="text/csv",
        width="stretch"
    )


# --------------------------------------------------
# AUDIENCE INSIGHTS
# --------------------------------------------------

with audience_tab:

    section_title(
        "Audience and device insights",
        "Explore conversions across demographic and device groups."
    )

    if "gender" in filtered_df.columns:

        left, right = st.columns(2)

        with left:

            gender_data = filtered_df.groupby(
                "gender"
            )["conversions"].sum().reset_index()

            fig = px.pie(
                gender_data,
                names="gender",
                values="conversions",
                hole=0.55,
                color_discrete_sequence=BLUE_PALETTE,
                title="Conversions by gender"
            )

            st.plotly_chart(
                style_fig(fig),
                width="stretch",
                config={"displayModeBar": False}
            )

        with right:

            if "device" in filtered_df.columns:

                device_data = filtered_df.groupby(
                    "device"
                )["conversions"].sum().reset_index()

                fig = px.bar(
                    device_data,
                    x="device",
                    y="conversions",
                    color_discrete_sequence=[ROYAL_BLUE],
                    title="Conversions by device"
                )

                fig.update_traces(marker_line_width=0)

                st.plotly_chart(
                    style_fig(fig),
                    width="stretch",
                    config={"displayModeBar": False}
                )

    if "city" in filtered_df.columns:

        city_data = filtered_df.groupby(
            "city"
        )["revenue"].sum().reset_index()

        fig = px.bar(
            city_data.sort_values("revenue", ascending=False),
            x="city",
            y="revenue",
            color_discrete_sequence=[ROYAL_BLUE],
            title="Revenue by city"
        )

        fig.update_traces(marker_line_width=0)

        st.plotly_chart(
            style_fig(fig, 400),
            width="stretch",
            config={"displayModeBar": False}
        )


# --------------------------------------------------
# BIG DATA EXPERIMENT
# --------------------------------------------------

with scaling_tab:

    section_title(
        "Big Data processing experiment",
        "Compare processing time across increasing dataset sizes."
    )

    if os.path.exists(BENCHMARK_FILE):

        benchmark = pd.read_csv(BENCHMARK_FILE)

        st.dataframe(
            benchmark,
            width="stretch",
            hide_index=True
        )

        time_columns = [
            "Pandas Time (s)",
            "MapReduce Time (s)",
            "Spark Time (s)"
        ]

        if all(c in benchmark.columns for c in time_columns):

            fig = px.line(
                benchmark,
                x="Dataset Size",
                y=time_columns,
                markers=True,
                title="Processing time comparison",
                color_discrete_sequence=BLUE_PALETTE
            )

            st.plotly_chart(
                style_fig(fig, 420),
                width="stretch",
                config={"displayModeBar": False}
            )

        st.download_button(
            "Download benchmark results",
            data=benchmark.to_csv(index=False).encode("utf-8"),
            file_name="benchmark_results.csv",
            mime="text/csv",
            width="stretch"
        )

    else:

        st.info(
            "Benchmark results have not been uploaded yet. "
            "Add benchmark_results.csv to the results folder."
        )


# --------------------------------------------------
# BUDGET OPTIMIZER
# --------------------------------------------------

with budget_tab:

    section_title(
        "Marketing budget recommendation engine",
        "Generate a performance-based allocation across advertising platforms."
    )

    budget = st.number_input(
        "Enter your marketing budget (PKR)",
        min_value=10000,
        value=1000000,
        step=50000
    )

    st.caption(
        "Recommendations consider ROAS, conversion rate and CPA efficiency. "
        "Each platform has a 10% minimum and 35% maximum allocation."
    )

    if st.button("Generate budget recommendations"):

        recommendation = recommend_budget(
            filtered_df,
            budget
        )

        st.session_state["budget_recommendation"] = recommendation
        st.session_state["budget_amount"] = budget

    if "budget_recommendation" in st.session_state:

        recommendation = st.session_state[
            "budget_recommendation"
        ]

        st.dataframe(
            recommendation[
                [
                    "platform",
                    "ROAS",
                    "CPA",
                    "Conversion_Rate",
                    "Allocation_Percentage",
                    "Recommended_Budget"
                ]
            ].round(2),
            width="stretch",
            hide_index=True
        )

        fig = px.pie(
            recommendation,
            names="platform",
            values="Recommended_Budget",
            hole=0.58,
            color_discrete_sequence=BLUE_PALETTE,
            title="Recommended budget distribution"
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color=card_bg, width=2))
        )

        st.plotly_chart(
            style_fig(fig, 400),
            width="stretch",
            config={"displayModeBar": False}
        )

        st.metric(
            "Total recommended budget",
            f"Rs. {recommendation['Recommended_Budget'].sum():,.0f}"
        )

        st.download_button(
            "Download budget recommendations",
            data=recommendation.to_csv(index=False).encode("utf-8"),
            file_name="budget_recommendations.csv",
            mime="text/csv",
            width="stretch"
        )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Sapphire Pakistan · Digital Advertising Analysis | "
    "Academic project using simulated advertising data."
)
