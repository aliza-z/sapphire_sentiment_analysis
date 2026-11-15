
import os
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Sapphire | Social Audience Intelligence",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


posts = load_csv(
    os.path.join(RESULTS_DIR, "post_anomalies.csv")
)

comments = load_csv(
    os.path.join(RESULTS_DIR, "clustered_comments.csv")
)

content = load_csv(
    os.path.join(RESULTS_DIR, "content_performance.csv")
)

clusters = load_csv(
    os.path.join(RESULTS_DIR, "cluster_summary.csv")
)

recommendations = load_csv(
    os.path.join(RESULTS_DIR, "marketing_recommendations.csv")
)


# --------------------------------------------------
# CHECK REQUIRED FILES
# --------------------------------------------------

required_files = {
    "Post analysis": posts,
    "Clustered comments": comments,
    "Content performance": content,
    "Cluster summary": clusters
}

missing = [
    name for name, df in required_files.items()
    if df.empty
]

if missing:
    st.error(
        "Some result files are missing or empty: "
        + ", ".join(missing)
    )
    st.info(
        "Run the Phase 3 Colab notebook and place all "
        "generated CSV files inside the results folder."
    )
    st.stop()


# --------------------------------------------------
# THEME SELECTION
# --------------------------------------------------

st.sidebar.markdown(
    """
    <div style="padding: 8px 0 18px 0;">
        <h1 style="letter-spacing: 3px; margin-bottom: 0;">
            SAPPHIRE
        </h1>
        <p style="font-size: 11px; letter-spacing: 1.5px;">
            PAKISTAN · AUDIENCE INTELLIGENCE
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

display_mode = st.sidebar.radio(
    "Appearance",
    ["Light", "Dark"],
    horizontal=True
)

if display_mode == "Dark":
    BG = "#071426"
    SIDEBAR = "#0B1F3A"
    CARD = "#102944"
    TEXT = "#F4F8FF"
    MUTED = "#A7BEDA"
    GRID = "#29415D"
    INPUT = "#102944"
else:
    BG = "#EEF6FF"
    SIDEBAR = "#DCEEFF"
    CARD = "#FFFFFF"
    TEXT = "#0B1F3A"
    MUTED = "#64748B"
    GRID = "#DCE6F1"
    INPUT = "#FFFFFF"

ROYAL_BLUE = "#4169E1"
BLUE_HOVER = "#3154C6"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BG};
        color: {TEXT};
    }}

    section[data-testid="stSidebar"] {{
        background-color: {SIDEBAR};
    }}

    section[data-testid="stSidebar"] * {{
        color: {TEXT};
    }}

    h1, h2, h3, h4, p, label {{
        color: {TEXT};
    }}

    [data-testid="stMetric"] {{
        background-color: {CARD};
        border: 1px solid {GRID};
        padding: 18px;
        border-radius: 14px;
    }}

    [data-testid="stMetricLabel"] {{
        color: {MUTED};
    }}

    [data-testid="stMetricValue"] {{
        color: {TEXT};
    }}

    div.stButton > button,
    div.stDownloadButton > button {{
        background-color: {ROYAL_BLUE};
        color: white;
        border: none;
        border-radius: 9px;
    }}

    div.stButton > button:hover,
    div.stDownloadButton > button:hover {{
        background-color: {BLUE_HOVER};
        color: white;
    }}

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {{
        background-color: {INPUT};
        border-radius: 8px;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid {GRID};
        border-radius: 10px;
    }}

    .section-label {{
        color: {ROYAL_BLUE};
        font-size: 12px;
        letter-spacing: 2px;
        font-weight: 700;
        text-transform: uppercase;
    }}

    .dashboard-caption {{
        color: {MUTED};
        font-size: 14px;
    }}

    hr {{
        border-color: {GRID};
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.divider()
st.sidebar.markdown("### Dashboard Filters")

platform_options = ["All"]

if "platform" in posts.columns:
    platform_options += sorted(
        posts["platform"].dropna().unique().tolist()
    )

selected_platform = st.sidebar.selectbox(
    "Platform",
    platform_options
)

campaign_options = ["All"]

if "campaign" in posts.columns:
    campaign_options += sorted(
        posts["campaign"].dropna().unique().tolist()
    )

selected_campaign = st.sidebar.selectbox(
    "Campaign",
    campaign_options
)

content_options = ["All"]

if "content_type" in posts.columns:
    content_options += sorted(
        posts["content_type"].dropna().unique().tolist()
    )

selected_content = st.sidebar.selectbox(
    "Content Type",
    content_options
)


# --------------------------------------------------
# FILTER POSTS
# --------------------------------------------------

filtered_posts = posts.copy()

if selected_platform != "All":
    filtered_posts = filtered_posts[
        filtered_posts["platform"] == selected_platform
    ]

if selected_campaign != "All":
    filtered_posts = filtered_posts[
        filtered_posts["campaign"] == selected_campaign
    ]

if selected_content != "All":
    filtered_posts = filtered_posts[
        filtered_posts["content_type"] == selected_content
    ]


# --------------------------------------------------
# FILTER COMMENTS USING MATCHING POST IDS
# --------------------------------------------------

filtered_comments = comments.copy()

if "post_id" in filtered_comments.columns:
    valid_post_ids = filtered_posts["post_id"].dropna().unique()

    filtered_comments = filtered_comments[
        filtered_comments["post_id"].isin(valid_post_ids)
    ]


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<p class="section-label">SAPPHIRE PAKISTAN</p>',
    unsafe_allow_html=True
)

st.title("Social Audience & Campaign Intelligence")

st.markdown(
    """
    <p class="dashboard-caption">
    Discover audience needs, understand content performance,
    identify unusual patterns and support smarter marketing decisions.
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()


# --------------------------------------------------
# KPI METRICS
# --------------------------------------------------

total_posts = len(filtered_posts)
total_comments = len(filtered_comments)

total_engagement = (
    filtered_posts["total_engagement"].sum()
    if "total_engagement" in filtered_posts.columns
    else 0
)

unusual_posts = (
    (filtered_posts["anomaly_flag"] == "Unusual").sum()
    if "anomaly_flag" in filtered_posts.columns
    else 0
)

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Posts", f"{total_posts:,}")
k2.metric("Total Comments", f"{total_comments:,}")
k3.metric("Total Engagement", f"{total_engagement:,.0f}")
k4.metric("Unusual Posts", f"{unusual_posts:,}")


# --------------------------------------------------
# DASHBOARD TABS
# --------------------------------------------------

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview",
    "Content Performance",
    "Audience Clusters",
    "Anomaly Detection",
    "Recommendations",
    "Data Quality"
])


# --------------------------------------------------
# TAB 1: OVERVIEW
# --------------------------------------------------

with tab1:

    st.subheader("Audience Intelligence Overview")

    left, right = st.columns(2)

    with left:

        if (
            "content_type" in filtered_posts.columns
            and "total_engagement" in filtered_posts.columns
        ):

            engagement = filtered_posts.groupby(
                "content_type"
            )["total_engagement"].mean().reset_index()

            fig = px.bar(
                engagement,
                x="content_type",
                y="total_engagement",
                title="Average Engagement by Content Type",
                color="content_type"
            )

            fig.update_layout(
                plot_bgcolor=CARD,
                paper_bgcolor=CARD,
                font_color=TEXT,
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

    with right:

        if "cluster_label" in filtered_comments.columns:

            cluster_data = filtered_comments[
                "cluster_label"
            ].value_counts().reset_index()

            cluster_data.columns = [
                "Audience Need",
                "Comments"
            ]

            fig = px.pie(
                cluster_data,
                names="Audience Need",
                values="Comments",
                hole=0.48,
                title="Distribution of Audience Needs"
            )

            fig.update_layout(
                paper_bgcolor=CARD,
                font_color=TEXT
            )

            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent Post Analysis")

    st.dataframe(
        filtered_posts.head(20),
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# TAB 2: CONTENT PERFORMANCE
# --------------------------------------------------

with tab2:

    st.subheader("Content Performance Analysis")

    if not filtered_posts.empty:

        if "content_type" in filtered_posts.columns:

            metrics = [
                col for col in [
                    "likes",
                    "comments_count",
                    "shares",
                    "views",
                    "total_engagement"
                ]
                if col in filtered_posts.columns
            ]

            selected_metric = st.selectbox(
                "Select engagement metric",
                metrics
            )

            performance = filtered_posts.groupby(
                "content_type"
            )[selected_metric].mean().reset_index()

            fig = px.bar(
                performance,
                x="content_type",
                y=selected_metric,
                color="content_type",
                title=f"Average {selected_metric} by Content Type"
            )

            fig.update_layout(
                plot_bgcolor=CARD,
                paper_bgcolor=CARD,
                font_color=TEXT,
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            filtered_posts,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No posts match the selected filters.")


# --------------------------------------------------
# TAB 3: AUDIENCE CLUSTERS
# --------------------------------------------------

with tab3:

    st.subheader("Audience Behaviour Clusters")

    if "cluster_label" in filtered_comments.columns:

        cluster_data = filtered_comments[
            "cluster_label"
        ].value_counts().reset_index()

        cluster_data.columns = [
            "Audience Need",
            "Number of Comments"
        ]

        fig = px.bar(
            cluster_data,
            x="Audience Need",
            y="Number of Comments",
            color="Audience Need",
            title="Audience Needs Discovered Through Clustering"
        )

        fig.update_layout(
            plot_bgcolor=CARD,
            paper_bgcolor=CARD,
            font_color=TEXT,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Explore individual clusters")

        selected_cluster = st.selectbox(
            "Select audience group",
            sorted(
                filtered_comments["cluster_label"]
                .dropna()
                .unique()
            )
        )

        sample = filtered_comments[
            filtered_comments["cluster_label"] == selected_cluster
        ]

        if "comment_text" in sample.columns:
            st.dataframe(
                sample[[
                    col for col in [
                        "comment_text",
                        "cluster_label",
                        "platform",
                        "campaign"
                    ]
                    if col in sample.columns
                ]].head(50),
                use_container_width=True,
                hide_index=True
            )

        st.metric(
            "Comments in Selected Group",
            f"{len(sample):,}"
        )

    else:
        st.info("Cluster labels are not available.")


# --------------------------------------------------
# TAB 4: ANOMALY DETECTION
# --------------------------------------------------

with tab4:

    st.subheader("Unusual Engagement Patterns")

    if "anomaly_flag" in filtered_posts.columns:

        unusual = filtered_posts[
            filtered_posts["anomaly_flag"] == "Unusual"
        ]

        st.metric(
            "Unusual Posts Detected",
            len(unusual)
        )

        if (
            "likes" in filtered_posts.columns
            and "comments_count" in filtered_posts.columns
        ):

            fig = px.scatter(
                filtered_posts,
                x="likes",
                y="comments_count",
                color="anomaly_flag",
                hover_data=[
                    col for col in [
                        "post_id",
                        "platform",
                        "content_type",
                        "campaign"
                    ]
                    if col in filtered_posts.columns
                ],
                title="Post Engagement Anomaly Analysis"
            )

            fig.update_layout(
                plot_bgcolor=CARD,
                paper_bgcolor=CARD,
                font_color=TEXT
            )

            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Posts requiring further investigation")

        st.dataframe(
            unusual,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "An unusual post is not automatically a successful or unsuccessful "
            "post. Its engagement pattern should be investigated."
        )

    else:
        st.info("Anomaly detection results are unavailable.")


# --------------------------------------------------
# TAB 5: RECOMMENDATIONS
# --------------------------------------------------

with tab5:

    st.subheader("Marketing Recommendations")

    if not recommendations.empty:

        display_columns = [
            col for col in [
                "cluster_label",
                "total_comments",
                "recommendation"
            ]
            if col in recommendations.columns
        ]

        if display_columns:

            for _, row in recommendations.iterrows():

                label = row.get(
                    "cluster_label",
                    "Audience Segment"
                )

                advice = row.get(
                    "recommendation",
                    "Investigate this audience group further."
                )

                count = row.get("total_comments", None)

                with st.expander(str(label)):

                    st.write(advice)

                    if pd.notna(count):
                        st.caption(
                            f"Comments in this group: {int(count):,}"
                        )

            st.download_button(
                "Download Recommendations",
                recommendations.to_csv(index=False),
                file_name="marketing_recommendations.csv",
                mime="text/csv"
            )

        else:
            st.dataframe(
                recommendations,
                use_container_width=True
            )

    else:
        st.info(
            "Recommendation file not found. "
            "Check your results folder."
        )


# --------------------------------------------------
# TAB 6: DATA QUALITY
# --------------------------------------------------

with tab6:

    st.subheader("Dataset Information")

    st.write(
        "This project uses simulated demonstration data. "
        "The records do not represent actual customer comments "
        "or measured campaign performance from the named brands."
    )

    q1, q2, q3 = st.columns(3)

    q1.metric("Post Records", len(posts))
    q2.metric("Comment Records", len(comments))
    q3.metric("Cluster Groups", (
        comments["cluster_label"].nunique()
        if "cluster_label" in comments.columns
        else 0
    ))

    st.markdown("### Missing values")

    quality = pd.DataFrame({
        "Dataset": [
            "Posts",
            "Comments",
            "Content Performance",
            "Cluster Summary"
        ],
        "Rows": [
            len(posts),
            len(comments),
            len(content),
            len(clusters)
        ],
        "Missing Values": [
            int(posts.isnull().sum().sum()),
            int(comments.isnull().sum().sum()),
            int(content.isnull().sum().sum()),
            int(clusters.isnull().sum().sum())
        ]
    })

    st.dataframe(
        quality,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### Download analysis files")

    for filename, df in [
        ("clustered_comments.csv", filtered_comments),
        ("post_anomalies.csv", filtered_posts),
        ("content_performance.csv", content),
        ("cluster_summary.csv", clusters)
    ]:

        st.download_button(
            f"Download {filename}",
            df.to_csv(index=False),
            file_name=filename,
            mime="text/csv",
            key=filename
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    """
    <div style="text-align:center; padding:12px;">
        <p style="letter-spacing:2px; font-weight:700;">
            SAPPHIRE PAKISTAN
        </p>
        <p style="font-size:12px;">
            Social Audience & Campaign Intelligence Engine
            · Academic Demonstration
        </p>
        <p style="font-size:11px;">
            Results are based on simulated demonstration data.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
