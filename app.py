
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import re

# =========================================================
# SAPPHIRE PAKISTAN — AD SENTIMENT ANALYSIS
# =========================================================

st.set_page_config(
    page_title="Sapphire | Ad Sentiment Analysis",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- THEME --------------------

if "appearance" not in st.session_state:
    st.session_state.appearance = "Dark"

with st.sidebar:
    st.markdown("## SAPPHIRE")
    st.caption("AD SENTIMENT ANALYSIS")
    st.divider()

    st.radio(
        "Appearance",
        ["Dark", "Light"],
        key="appearance",
        horizontal=True
    )

    st.divider()
    st.markdown("### Filters")

dark = st.session_state.appearance == "Dark"

if dark:
    BG = "#0B1020"
    SIDEBAR = "#0D172A"
    CARD = "#121E33"
    CARD_ALT = "#182740"
    TEXT = "#F2F5FB"
    MUTED = "#A5B3C9"
    BORDER = "#273750"
    ACCENT = "#7FA8F8"
    GRID = "#26354D"
    TEMPLATE = "plotly_dark"
else:
    BG = "#F4F6FA"
    SIDEBAR = "#E9EEF6"
    CARD = "#FFFFFF"
    CARD_ALT = "#F0F4FA"
    TEXT = "#17243B"
    MUTED = "#64748B"
    BORDER = "#D9E1EC"
    ACCENT = "#2856A6"
    GRID = "#E3E8F0"
    TEMPLATE = "plotly_white"

SENTIMENT_COLORS = {
    "Positive": "#2DAA83",
    "Neutral": "#8B9BB4",
    "Negative": "#D96675",
    "Unknown": "#A69AC8"
}

CHART_COLORS = ["#315DAB", "#2DAA83", "#D96675", "#8B9BB4", "#A69AC8"]

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif;
    }}

    .stApp {{
        background: {BG};
        color: {TEXT};
    }}

    [data-testid="stSidebar"] {{
        background: {SIDEBAR};
        border-right: 1px solid {BORDER};
    }}

    [data-testid="stSidebar"] * {{
        color: {TEXT};
    }}

    [data-testid="stSidebar"] [data-baseweb="radio"] label {{
        background: transparent;
        border-radius: 8px;
    }}

    h1, h2, h3 {{
        font-family: 'Manrope', sans-serif !important;
        color: {TEXT} !important;
        letter-spacing: -0.5px;
    }}

    p, label, span, div {{
        color: inherit;
    }}

    [data-testid="stMetric"] {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 18px 20px;
    }}

    [data-testid="stMetricLabel"] {{
        color: {MUTED} !important;
        font-size: 0.85rem !important;
    }}

    [data-testid="stMetricValue"] {{
        color: {TEXT} !important;
        font-family: 'Manrope', sans-serif !important;
        font-weight: 700;
    }}

    [data-testid="stMetricDelta"] {{
        font-size: 0.8rem;
    }}

    [data-testid="stTabs"] button {{
        font-weight: 600;
    }}

    [data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 10px;
    }}

    .page-heading {{
        font-family: 'Manrope', sans-serif;
        font-size: 2.5rem;
        line-height: 1.15;
        font-weight: 800;
        color: {TEXT};
        letter-spacing: -1.2px;
        margin: 0 0 8px 0;
    }}

    .page-subtitle {{
        color: {MUTED};
        font-size: 1rem;
        margin-bottom: 25px;
    }}

    .section-heading {{
        font-family: 'Manrope', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: {TEXT};
        margin: 8px 0 4px 0;
    }}

    .section-description {{
        color: {MUTED};
        font-size: 0.88rem;
        margin-bottom: 12px;
    }}

    .info-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
    }}

    .info-label {{
        color: {MUTED};
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}

    .info-value {{
        color: {TEXT};
        font-size: 1.05rem;
        font-weight: 700;
        margin-top: 8px;
    }}

    .stButton button, .stDownloadButton button {{
        border-radius: 8px;
        border: 1px solid {BORDER};
        font-weight: 600;
    }}

    hr {{
        border-color: {BORDER};
    }}

    .stAlert {{
        border-radius: 10px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# -------------------- DATA LOADING --------------------

DATA_FILE = "sapphire_youtube_comments_labeled.csv"
SCALING_FILE = "scaling_results.csv"

st.markdown(
    """
    <div class="page-heading">Sapphire Pakistan</div>
    <div class="page-subtitle">
        Advertisement Sentiment Analysis · YouTube Comment Insights
    </div>
    """,
    unsafe_allow_html=True
)

if not os.path.exists(DATA_FILE):
    st.error(
        f"Cannot find `{DATA_FILE}`. Place the CSV file in the same folder as app.py."
    )
    st.stop()


@st.cache_data
def load_data(path, modified_time):
    return pd.read_csv(path)


df = load_data(DATA_FILE, os.path.getmtime(DATA_FILE))

# -------------------- STANDARDIZE DATA --------------------

df.columns = [str(c).strip() for c in df.columns]

required_columns = ["comment_text", "sentiment_label"]

missing_columns = [c for c in required_columns if c not in df.columns]

if missing_columns:
    st.error(
        "The CSV is missing required columns: "
        + ", ".join(missing_columns)
    )
    st.stop()

df["comment_text"] = df["comment_text"].fillna("").astype(str)

df["sentiment_label"] = (
    df["sentiment_label"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
    .str.lower()
    .replace({
        "positive": "Positive",
        "negative": "Negative",
        "neutral": "Neutral",
        "label_0": "Negative",
        "label_1": "Neutral",
        "label_2": "Positive",
        "unknown": "Unknown",
        "nan": "Unknown",
        "": "Unknown"
    })
)

df["sentiment_label"] = df["sentiment_label"].apply(
    lambda x: x if x in SENTIMENT_COLORS else x.title()
)

df.loc[
    ~df["sentiment_label"].isin(SENTIMENT_COLORS),
    "sentiment_label"
] = "Unknown"

if "video_id" not in df.columns:
    df["video_id"] = [f"Video {i+1}" for i in range(len(df))]

if "like_count" not in df.columns:
    df["like_count"] = 0

if "reply_count" not in df.columns:
    df["reply_count"] = 0

df["like_count"] = pd.to_numeric(df["like_count"], errors="coerce").fillna(0)
df["reply_count"] = pd.to_numeric(df["reply_count"], errors="coerce").fillna(0)

if "comment_date" in df.columns:
    df["comment_date"] = pd.to_datetime(df["comment_date"], errors="coerce")

if "aspect_label" not in df.columns:
    df["aspect_label"] = "Unclassified"

df["aspect_label"] = df["aspect_label"].fillna("Unclassified").astype(str)

# -------------------- HUMAN-READABLE VIDEO NAMES --------------------

video_ids = df["video_id"].dropna().astype(str).unique().tolist()

video_name_map = {
    video_id: f"Advertisement {i+1:02d}"
    for i, video_id in enumerate(video_ids)
}

df["advertisement"] = df["video_id"].astype(str).map(video_name_map)

# -------------------- FILTERS --------------------

with st.sidebar:
    selected_ads = st.multiselect(
        "Advertisements",
        options=sorted(df["advertisement"].unique()),
        default=sorted(df["advertisement"].unique())
    )

    selected_sentiments = st.multiselect(
        "Sentiment",
        options=["Positive", "Neutral", "Negative", "Unknown"],
        default=["Positive", "Neutral", "Negative", "Unknown"]
    )

    max_likes = int(max(1, df["like_count"].max()))

    likes_range = st.slider(
        "Comment likes",
        min_value=0,
        max_value=max_likes,
        value=(0, max_likes)
    )

    st.divider()
    st.caption("Use filters to update all dashboard sections.")

filtered = df[
    df["advertisement"].isin(selected_ads)
    & df["sentiment_label"].isin(selected_sentiments)
    & df["like_count"].between(likes_range[0], likes_range[1])
].copy()

if filtered.empty:
    st.warning("No comments match these filters. Adjust the filters in the sidebar.")
    st.stop()

# -------------------- HELPER FUNCTIONS --------------------

def style_fig(fig, title=None):
    fig.update_layout(
        template=TEMPLATE,
        title=dict(text=title or "", font=dict(size=16, color=TEXT)),
        font=dict(family="DM Sans, sans-serif", size=12, color=TEXT),
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        colorway=CHART_COLORS,
        margin=dict(l=18, r=18, t=55, b=25),
        legend_title_text="",
        hoverlabel=dict(bgcolor=CARD_ALT, font_color=TEXT, bordercolor=BORDER)
    )
    fig.update_xaxes(gridcolor=GRID, linecolor=BORDER, zerolinecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, linecolor=BORDER, zerolinecolor=GRID)
    return fig


def section_title(title, description=None):
    st.markdown(
        f'<div class="section-heading">{title}</div>',
        unsafe_allow_html=True
    )
    if description:
        st.markdown(
            f'<div class="section-description">{description}</div>',
            unsafe_allow_html=True
        )


def percent(part, whole):
    return (part / whole * 100) if whole else 0


# -------------------- SUMMARY METRICS --------------------

st.divider()

total_comments = len(filtered)
total_ads = filtered["advertisement"].nunique()
positive_count = int((filtered["sentiment_label"] == "Positive").sum())
negative_count = int((filtered["sentiment_label"] == "Negative").sum())
neutral_count = int((filtered["sentiment_label"] == "Neutral").sum())
known_count = positive_count + negative_count + neutral_count

positive_pct = percent(positive_count, known_count)
negative_pct = percent(negative_count, known_count)
avg_likes = filtered["like_count"].mean()
total_replies = int(filtered["reply_count"].sum())

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Comments analysed", f"{total_comments:,}")
k2.metric("Advertisements", f"{total_ads:,}")
k3.metric("Positive sentiment", f"{positive_pct:.1f}%")
k4.metric("Negative sentiment", f"{negative_pct:.1f}%")
k5.metric("Total replies", f"{total_replies:,}")

st.caption(
    "Sentiment labels are model predictions, not verified ground-truth labels. "
    "Percentages exclude comments marked Unknown."
)

# -------------------- TABS --------------------

overview_tab, sentiment_tab, ads_tab, comments_tab, quality_tab = st.tabs([
    "Overview",
    "Sentiment",
    "Advertisement Performance",
    "Comments",
    "Data Quality"
])

# =========================================================
# OVERVIEW
# =========================================================

with overview_tab:
    st.subheader("Overview")
    st.caption("A quick summary of the comments and how viewers responded.")

    left, right = st.columns([1, 1])

    with left:
        section_title(
            "Sentiment distribution",
            "Share of comments by predicted sentiment."
        )

        sentiment_counts = (
            filtered["sentiment_label"]
            .value_counts()
            .rename_axis("Sentiment")
            .reset_index(name="Comments")
        )

        fig = px.pie(
            sentiment_counts,
            names="Sentiment",
            values="Comments",
            hole=0.68,
            color="Sentiment",
            color_discrete_map=SENTIMENT_COLORS
        )
        fig.update_traces(
            textposition="outside",
            textinfo="percent",
            marker=dict(line=dict(color=CARD, width=3))
        )
        fig.update_layout(showlegend=True)
        st.plotly_chart(style_fig(fig), width="stretch")

    with right:
        section_title(
            "Comment volume by advertisement",
            "Shows which advertisements generated the most comments."
        )

        volume = (
            filtered.groupby("advertisement")
            .size()
            .reset_index(name="Comments")
            .sort_values("Comments", ascending=True)
        )

        fig = px.bar(
            volume,
            x="Comments",
            y="advertisement",
            orientation="h",
            text="Comments",
            color_discrete_sequence=[ACCENT]
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig), width="stretch")

    st.divider()
    section_title("What stands out", "Automatically calculated from the currently filtered data.")

    c1, c2, c3 = st.columns(3)

    if known_count:
        balance = positive_pct - negative_pct
        if balance > 0:
            balance_text = f"Positive sentiment leads by {balance:.1f} percentage points."
        elif balance < 0:
            balance_text = f"Negative sentiment leads by {abs(balance):.1f} percentage points."
        else:
            balance_text = "Positive and negative sentiment are balanced."
    else:
        balance_text = "There are no classified positive, neutral, or negative comments."

    c1.markdown(
        f'<div class="info-card"><div class="info-label">Sentiment balance</div>'
        f'<div class="info-value">{balance_text}</div></div>',
        unsafe_allow_html=True
    )

    top_ad = filtered["advertisement"].value_counts().idxmax()
    top_ad_count = int(filtered["advertisement"].value_counts().max())

    c2.markdown(
        f'<div class="info-card"><div class="info-label">Most discussed advertisement</div>'
        f'<div class="info-value">{top_ad}</div>'
        f'<div style="color:{MUTED};font-size:0.85rem">{top_ad_count} comments</div></div>',
        unsafe_allow_html=True
    )

    c3.markdown(
        f'<div class="info-card"><div class="info-label">Average likes per comment</div>'
        f'<div class="info-value">{avg_likes:.2f}</div></div>',
        unsafe_allow_html=True
    )

    section_title("Engagement by sentiment", "Average likes and replies for each sentiment group.")

    engagement = (
        filtered.groupby("sentiment_label", as_index=False)
        .agg(
            Comments=("comment_text", "size"),
            Average_likes=("like_count", "mean"),
            Average_replies=("reply_count", "mean")
        )
    )

    if not engagement.empty:
        fig = px.bar(
            engagement,
            x="sentiment_label",
            y="Average_likes",
            color="sentiment_label",
            color_discrete_map=SENTIMENT_COLORS,
            text_auto=".2f",
            labels={
                "sentiment_label": "Sentiment",
                "Average_likes": "Average likes"
            }
        )
        st.plotly_chart(style_fig(fig), width="stretch")

# =========================================================
# SENTIMENT
# =========================================================

with sentiment_tab:
    st.subheader("Sentiment analysis")
    st.caption("Explore sentiment proportions and how they differ between advertisements.")

    sentiment_counts = (
        filtered["sentiment_label"]
        .value_counts()
        .rename_axis("Sentiment")
        .reset_index(name="Comments")
    )

    col1, col2 = st.columns(2)

    with col1:
        section_title("Sentiment counts", "Number of comments in each category.")
        fig = px.bar(
            sentiment_counts,
            x="Sentiment",
            y="Comments",
            color="Sentiment",
            color_discrete_map=SENTIMENT_COLORS,
            text="Comments"
        )
        st.plotly_chart(style_fig(fig), width="stretch")

    with col2:
        section_title("Sentiment by advertisement", "Compare predicted comment sentiment across advertisements.")
        by_ad = (
            filtered.groupby(["advertisement", "sentiment_label"])
            .size()
            .reset_index(name="Comments")
        )
        fig = px.bar(
            by_ad,
            x="advertisement",
            y="Comments",
            color="sentiment_label",
            barmode="stack",
            color_discrete_map=SENTIMENT_COLORS,
            labels={
                "advertisement": "Advertisement",
                "sentiment_label": "Sentiment"
            }
        )
        st.plotly_chart(style_fig(fig), width="stretch")

    st.divider()
    section_title("Most liked comments by sentiment", "High-like comments can indicate stronger viewer engagement.")

    top_comments = (
        filtered.sort_values("like_count", ascending=False)
        .groupby("sentiment_label", group_keys=False)
        .head(3)
    )

    display_cols = [
        c for c in [
            "advertisement", "sentiment_label", "comment_text",
            "like_count", "reply_count"
        ] if c in top_comments.columns
    ]

    st.dataframe(
        top_comments[display_cols],
        width="stretch",
        hide_index=True
    )

# =========================================================
# ADVERTISEMENT PERFORMANCE
# =========================================================

with ads_tab:
    st.subheader("Advertisement performance")
    st.caption("Compare comment volume and engagement across videos.")

    ad_stats = (
        filtered.groupby("advertisement", as_index=False)
        .agg(
            Comments=("comment_text", "size"),
            Average_likes=("like_count", "mean"),
            Total_likes=("like_count", "sum"),
            Average_replies=("reply_count", "mean"),
            Total_replies=("reply_count", "sum")
        )
        .sort_values("Comments", ascending=False)
    )

    left, right = st.columns(2)

    with left:
        section_title("Comment volume", "Total comments associated with each advertisement.")
        fig = px.bar(
            ad_stats.sort_values("Comments"),
            x="Comments",
            y="advertisement",
            orientation="h",
            text="Comments",
            color_discrete_sequence=[ACCENT]
        )
        st.plotly_chart(style_fig(fig), width="stretch")

    with right:
        section_title("Average likes", "Average likes per comment, rather than total likes.")
        fig = px.bar(
            ad_stats.sort_values("Average_likes"),
            x="Average_likes",
            y="advertisement",
            orientation="h",
            text_auto=".2f",
            color_discrete_sequence=["#2DAA83"]
        )
        st.plotly_chart(style_fig(fig), width="stretch")

    section_title("Advertisement comparison table")
    st.dataframe(
        ad_stats.round(2),
        width="stretch",
        hide_index=True
    )

    st.download_button(
        "Download advertisement summary",
        data=ad_stats.to_csv(index=False).encode("utf-8"),
        file_name="sapphire_advertisement_summary.csv",
        mime="text/csv",
        width="stretch"
    )

    if "comment_date" in filtered.columns and filtered["comment_date"].notna().any():
        st.divider()
        section_title("Comment activity over time", "Daily comment volume based on the dates available in the dataset.")
        timeline = (
            filtered.dropna(subset=["comment_date"])
            .assign(Date=lambda x: x["comment_date"].dt.date)
            .groupby("Date")
            .size()
            .reset_index(name="Comments")
        )

        fig = px.line(
            timeline,
            x="Date",
            y="Comments",
            markers=True
        )
        st.plotly_chart(style_fig(fig), width="stretch")

# =========================================================
# COMMENTS
# =========================================================

with comments_tab:
    st.subheader("Comment explorer")
    st.caption("Search and inspect individual comments, sentiment labels, and engagement.")

    search_text = st.text_input(
        "Search comment text",
        placeholder="Enter a word or phrase..."
    )

    comment_view = filtered.copy()

    if search_text.strip():
        comment_view = comment_view[
            comment_view["comment_text"].str.contains(
                re.escape(search_text.strip()),
                case=False,
                na=False
            )
        ]

    display_cols = [
        c for c in [
            "advertisement", "comment_text", "sentiment_label",
            "aspect_label", "like_count", "reply_count", "comment_date"
        ] if c in comment_view.columns
    ]

    st.caption(f"{len(comment_view):,} comments match the current filters and search.")
    st.dataframe(
        comment_view[display_cols],
        width="stretch",
        hide_index=True
    )

    st.download_button(
        "Download filtered comments",
        data=comment_view.to_csv(index=False).encode("utf-8"),
        file_name="sapphire_filtered_comments.csv",
        mime="text/csv",
        width="stretch"
    )

# =========================================================
# DATA QUALITY
# =========================================================

with quality_tab:
    st.subheader("Data quality and limitations")
    st.caption("Review the dataset's completeness before interpreting results.")

    quality = pd.DataFrame({
        "Check": [
            "Total rows",
            "Unique advertisements",
            "Empty comment texts",
            "Duplicate comment IDs",
            "Unknown sentiment labels",
            "Missing comment dates"
        ],
        "Result": [
            len(df),
            df["video_id"].nunique(),
            int(df["comment_text"].str.strip().eq("").sum()),
            int(df["comment_id"].duplicated().sum()) if "comment_id" in df.columns else "Not available",
            int(df["sentiment_label"].eq("Unknown").sum()),
            int(df["comment_date"].isna().sum()) if "comment_date" in df.columns else "Date column unavailable"
        ]
    })

    st.dataframe(quality, width="stretch", hide_index=True)

    st.markdown("#### Interpretation notes")
    st.markdown(
        """
        - Sentiment categories are automated predictions and may misread sarcasm, slang,
          mixed-language comments, or short comments.
        - Positive sentiment does not necessarily mean the advertisement caused a purchase.
        - Likes and replies measure visible engagement, not overall customer satisfaction.
        - Advertisement names are neutral display labels. They replace raw video IDs in the dashboard;
          the original IDs remain in the source CSV.
        - Results represent the comments in this dataset and should not be treated as a complete
          representation of all Sapphire customers.
        """
    )

    st.download_button(
        "Download quality report",
        data=quality.to_csv(index=False).encode("utf-8"),
        file_name="sapphire_data_quality_report.csv",
        mime="text/csv",
        width="stretch"
    )

# -------------------- SCALING EXPERIMENT --------------------

with st.expander("Dataset scaling experiment"):
    st.caption(
        "Optional results from the separate scaling experiment. Synthetic data must be clearly "
        "identified as synthetic and must not be presented as real YouTube comments."
    )

    if os.path.exists(SCALING_FILE):
        scaling = pd.read_csv(SCALING_FILE)
        st.dataframe(scaling, width="stretch", hide_index=True)

        numeric_cols = scaling.select_dtypes(include="number").columns.tolist()
        possible_size_cols = [
            c for c in scaling.columns
            if any(word in c.lower() for word in ["row", "size", "record", "comment", "dataset"])
        ]

        if numeric_cols and possible_size_cols:
            x_col = possible_size_cols[0]
            y_candidates = [
                c for c in numeric_cols
                if c != x_col and any(
                    word in c.lower()
                    for word in ["time", "second", "memory", "runtime"]
                )
            ]

            if y_candidates:
                y_col = y_candidates[0]
                fig = px.line(
                    scaling,
                    x=x_col,
                    y=y_col,
                    markers=True,
                    title=f"{y_col} by {x_col}"
                )
                st.plotly_chart(style_fig(fig), width="stretch")
    else:
        st.info(
            "No scaling_results.csv file found. Add it to the app folder to display scaling results."
        )

st.divider()
st.caption("Sapphire Pakistan · Advertisement Sentiment Analysis")
