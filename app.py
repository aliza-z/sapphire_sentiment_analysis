import os
import re
import html
import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Sapphire | Audience Intelligence",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_FILE = "sapphire_youtube_comments_labeled.csv"
SCALING_FILE = "scaling_results.csv"

# --------------------------------------------------
# THEME
# --------------------------------------------------
if "appearance" not in st.session_state:
    st.session_state.appearance = "Dark"

with st.sidebar:
    st.markdown("## 💠 Sapphire Analytics")
    st.caption("Audience Intelligence Platform")
    st.divider()

    st.radio(
        "Appearance",
        ["Dark", "Light"],
        key="appearance",
        horizontal=True
    )

dark = st.session_state.appearance == "Dark"

if dark:
    bg = "#10151D"
    panel = "#19222E"
    text = "#EDF2F7"
    muted = "#A5B2C3"
    border = "#303D4D"
    accent = "#68D5B2"
    chart_template = "plotly_dark"
else:
    bg = "#F4F7F5"
    panel = "#FFFFFF"
    text = "#1D3029"
    muted = "#65756D"
    border = "#DDE6E0"
    accent = "#167D60"
    chart_template = "plotly_white"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg};
        color: {text};
    }}
    [data-testid="stSidebar"] {{
        background-color: {panel};
        border-right: 1px solid {border};
    }}
    [data-testid="stMetric"] {{
        background-color: {panel};
        border: 1px solid {border};
        padding: 18px 20px;
        border-radius: 14px;
    }}
    [data-testid="stMetricLabel"] {{
        color: {muted};
    }}
    [data-testid="stMetricValue"] {{
        color: {text};
    }}
    div[data-testid="stTabs"] button {{
        font-weight: 600;
    }}
    .hero {{
        padding: 25px 28px;
        background: {panel};
        border: 1px solid {border};
        border-radius: 18px;
        margin-bottom: 20px;
    }}
    .hero h1 {{
        color: {text};
        margin-bottom: 5px;
        font-size: 2.15rem;
    }}
    .hero p {{
        color: {muted};
        margin-bottom: 0;
    }}
    .insight {{
        padding: 15px 18px;
        background: {panel};
        border: 1px solid {border};
        border-left: 4px solid {accent};
        border-radius: 10px;
        margin: 8px 0;
        color: {text};
    }}
    .small-note {{
        color: {muted};
        font-size: 0.88rem;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_csv(path, modified_time):
    return pd.read_csv(path)

if not os.path.exists(DATA_FILE):
    st.error(f"Dataset not found: {DATA_FILE}")
    st.write(
        "Upload the labeled comments CSV to the root of your "
        "GitHub repository, alongside app.py."
    )
    st.stop()

df = load_csv(DATA_FILE, os.path.getmtime(DATA_FILE))
df.columns = df.columns.str.strip().str.lower()

required = ["comment_text"]
missing = [c for c in required if c not in df.columns]

if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

# Ensure optional columns exist
defaults = {
    "video_id": "Unknown",
    "sentiment_label": "Unknown",
    "like_count": 0,
    "reply_count": 0
}
for col, default in defaults.items():
    if col not in df.columns:
        df[col] = default

for col in ["like_count", "reply_count"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["comment_text"] = df["comment_text"].fillna("").astype(str)
df["video_id"] = df["video_id"].fillna("Unknown").astype(str)

# Standardize common sentiment label formats
def normalize_sentiment(value):
    label = str(value).strip().lower().replace(" ", "_")
    mapping = {
        "positive": "Positive",
        "pos": "Positive",
        "label_2": "Positive",
        "negative": "Negative",
        "neg": "Negative",
        "label_0": "Negative",
        "neutral": "Neutral",
        "neu": "Neutral",
        "label_1": "Neutral"
    }
    return mapping.get(label, "Unknown" if label in ["", "nan", "none"] else str(value).title())

df["sentiment_label"] = df["sentiment_label"].apply(normalize_sentiment)

sentiment_colors = {
    "Positive": "#26B887",
    "Neutral": "#8A9BAD",
    "Negative": "#E56B70",
    "Unknown": "#B3A1C9"
}

# Parse dates if available
if "comment_date" in df.columns:
    df["comment_date"] = pd.to_datetime(
        df["comment_date"], errors="coerce", utc=True
    )

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
with st.sidebar:
    st.divider()
    st.markdown("### Filter your analysis")

    all_videos = sorted(df["video_id"].unique().tolist())
    chosen_videos = st.multiselect(
        "Videos",
        options=all_videos,
        default=all_videos
    )

    all_sentiments = [
        s for s in ["Positive", "Neutral", "Negative", "Unknown"]
        if s in df["sentiment_label"].unique()
    ]
    chosen_sentiments = st.multiselect(
        "Sentiment",
        options=all_sentiments,
        default=all_sentiments
    )

    min_likes = int(df["like_count"].min())
    max_likes = int(df["like_count"].max())

    if min_likes < max_likes:
        likes_range = st.slider(
            "Comment likes",
            min_value=min_likes,
            max_value=max_likes,
            value=(min_likes, max_likes)
        )
    else:
        likes_range = (min_likes, max_likes)

filtered = df[
    df["video_id"].isin(chosen_videos)
    & df["sentiment_label"].isin(chosen_sentiments)
    & df["like_count"].between(likes_range[0], likes_range[1])
].copy()

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>💠 Sapphire Pakistan</h1>
        <p>YouTube audience intelligence · Sentiment · Engagement · Insights</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    f"Showing {len(filtered):,} of {len(df):,} comments "
    f"across {filtered['video_id'].nunique():,} selected videos."
)

# --------------------------------------------------
# METRICS
# --------------------------------------------------
total = len(filtered)
positive = int((filtered["sentiment_label"] == "Positive").sum())
negative = int((filtered["sentiment_label"] == "Negative").sum())
neutral = int((filtered["sentiment_label"] == "Neutral").sum())

known = positive + negative + neutral
positive_pct = positive / known * 100 if known else 0
negative_pct = negative / known * 100 if known else 0
sentiment_balance = (
    (positive - negative) / known * 100 if known else 0
)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Comments", f"{total:,}")
m2.metric("Videos", f"{filtered['video_id'].nunique():,}")
m3.metric("Positive", f"{positive_pct:.1f}%", f"{positive:,} comments")
m4.metric("Negative", f"{negative_pct:.1f}%", f"{negative:,} comments")
m5.metric("Avg. likes", f"{filtered['like_count'].mean():.2f}")

st.divider()

if total == 0:
    st.warning("No records match these filters. Adjust the sidebar filters.")
    st.stop()

# --------------------------------------------------
# INSIGHT GENERATOR
# --------------------------------------------------
st.subheader("Quick insights")

if known:
    if positive_pct > negative_pct:
        sentiment_summary = (
            f"Positive predictions exceed negative predictions by "
            f"{positive_pct - negative_pct:.1f} percentage points."
        )
    elif negative_pct > positive_pct:
        sentiment_summary = (
            f"Negative predictions exceed positive predictions by "
            f"{negative_pct - positive_pct:.1f} percentage points."
        )
    else:
        sentiment_summary = "Positive and negative predictions are balanced."

    st.markdown(
        f'<div class="insight">✦ <b>Sentiment balance:</b> '
        f'{html.escape(sentiment_summary)} '
        f'Balance score: {sentiment_balance:+.1f} '
        f'(positive share minus negative share, as a percentage of known labels).</div>',
        unsafe_allow_html=True
    )

top_video = (
    filtered.groupby("video_id").size().sort_values(ascending=False)
)
if len(top_video):
    st.markdown(
        f'<div class="insight">✦ <b>Conversation volume:</b> '
        f'Video <b>{html.escape(str(top_video.index[0]))}</b> has the '
        f'most comments in the current selection ({int(top_video.iloc[0])}).</div>',
        unsafe_allow_html=True
    )

if known:
    engagement = filtered.groupby("sentiment_label")["like_count"].mean()
    engagement = engagement.reindex(["Positive", "Neutral", "Negative"]).dropna()
    engagement = engagement[engagement.index.isin(filtered["sentiment_label"].unique())]
    if len(engagement):
        best_engagement = engagement.idxmax()
        st.markdown(
            f'<div class="insight">✦ <b>Engagement signal:</b> '
            f'{html.escape(str(best_engagement))}-labeled comments have the '
            f'highest average likes ({engagement.max():.2f}) in this selection. '
            f'This is an association, not evidence that sentiment causes likes.</div>',
            unsafe_allow_html=True
        )

# --------------------------------------------------
# TABS
# --------------------------------------------------
overview, sentiment_tab, videos_tab, explorer, quality = st.tabs([
    "Overview",
    "Sentiment Intelligence",
    "Video Performance",
    "Comment Explorer",
    "Data Quality"
])

def style_fig(fig, title=None):
    fig.update_layout(
        template=chart_template,
        title=title,
        font=dict(color=text),
        paper_bgcolor=panel,
        plot_bgcolor=panel,
        margin=dict(l=20, r=20, t=60, b=30),
        legend_title_text=""
    )
    return fig

# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------
with overview:
    st.subheader("Engagement overview")

    left, right = st.columns(2)

    with left:
        counts = (
            filtered["sentiment_label"]
            .value_counts()
            .reindex(["Positive", "Neutral", "Negative", "Unknown"])
            .dropna()
            .reset_index()
        )
        counts.columns = ["Sentiment", "Comments"]

        fig = px.pie(
            counts,
            names="Sentiment",
            values="Comments",
            hole=0.62,
            color="Sentiment",
            color_discrete_map=sentiment_colors
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(style_fig(fig, "Sentiment composition"), use_container_width=True)

    with right:
        sentiment_summary = (
            filtered["sentiment_label"].value_counts()
            .reindex(["Positive", "Neutral", "Negative", "Unknown"])
            .dropna()
            .rename_axis("Sentiment")
            .reset_index(name="Comments")
        )
        fig = px.bar(
            sentiment_summary,
            x="Sentiment",
            y="Comments",
            color="Sentiment",
            color_discrete_map=sentiment_colors
        )
        st.plotly_chart(style_fig(fig, "Predicted sentiment counts"), use_container_width=True)

    st.subheader("Engagement distribution")
    left, right = st.columns(2)

    with left:
        fig = px.histogram(
            filtered,
            x="like_count",
            nbins=min(20, max(5, filtered["like_count"].nunique())),
            labels={"like_count": "Likes"},
        )
        st.plotly_chart(style_fig(fig, "Distribution of likes"), use_container_width=True)

    with right:
        fig = px.scatter(
            filtered,
            x="like_count",
            y="reply_count",
            color="sentiment_label",
            color_discrete_map=sentiment_colors,
            hover_data=["video_id"],
            labels={
                "like_count": "Likes",
                "reply_count": "Replies",
                "sentiment_label": "Predicted sentiment"
            }
        )
        st.plotly_chart(style_fig(fig, "Likes compared with replies"), use_container_width=True)

# --------------------------------------------------
# SENTIMENT INTELLIGENCE
# --------------------------------------------------
with sentiment_tab:
    st.subheader("Understand the conversation")

    st.markdown(
        '<div class="small-note">Sentiment is model-predicted, not '
        'human-verified. Interpret proportions as estimates for this sample.</div>',
        unsafe_allow_html=True
    )

    if known:
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Positive comments", f"{positive:,}")
        s2.metric("Neutral comments", f"{neutral:,}")
        s3.metric("Negative comments", f"{negative:,}")
        s4.metric("Unclassified", f"{total - known:,}")

        st.subheader("Sentiment by video")

        by_video = (
            filtered.groupby(["video_id", "sentiment_label"])
            .size()
            .reset_index(name="Comments")
        )

        fig = px.bar(
            by_video,
            x="video_id",
            y="Comments",
            color="sentiment_label",
            barmode="stack",
            category_orders={
                "sentiment_label": ["Positive", "Neutral", "Negative", "Unknown"]
            },
            color_discrete_map=sentiment_colors,
            labels={
                "video_id": "Video ID",
                "sentiment_label": "Sentiment"
            }
        )
        st.plotly_chart(style_fig(fig), use_container_width=True)

        st.subheader("Average engagement by sentiment")

        engagement_by_sentiment = (
            filtered.groupby("sentiment_label")
            .agg(
                comments=("comment_text", "size"),
                avg_likes=("like_count", "mean"),
                avg_replies=("reply_count", "mean"),
                total_likes=("like_count", "sum")
            )
            .reindex(["Positive", "Neutral", "Negative", "Unknown"])
            .dropna(how="all")
            .reset_index()
        )

        st.dataframe(
            engagement_by_sentiment,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Comments with the most likes by sentiment")
        for sentiment in ["Positive", "Negative", "Neutral"]:
            subset = filtered[
                filtered["sentiment_label"] == sentiment
            ].sort_values("like_count", ascending=False)

            if not subset.empty:
                with st.expander(f"{sentiment} — top liked comments"):
                    for _, row in subset.head(5).iterrows():
                        st.markdown(
                            f"**{int(row['like_count'])} likes** · "
                            f"Video `{row['video_id']}`"
                        )
                        st.write(row["comment_text"])
                        st.divider()
    else:
        st.info("No recognized sentiment labels are available in this selection.")

    # Optional confidence analysis
    confidence_col = next(
        (c for c in ["sentiment_confidence", "confidence", "sentiment_score"]
         if c in filtered.columns),
        None
    )

    if confidence_col:
        st.subheader("Prediction confidence")
        confidence = pd.to_numeric(
            filtered[confidence_col], errors="coerce"
        ).dropna()

        if not confidence.empty:
            st.metric("Mean confidence / score", f"{confidence.mean():.3f}")
            fig = px.histogram(confidence, nbins=15)
            st.plotly_chart(
                style_fig(fig, f"Distribution of {confidence_col}"),
                use_container_width=True
            )
    else:
        st.caption(
            "Confidence analysis is not shown because the dataset has no "
            "recognized prediction-confidence column."
        )

    # Basic keyword signals
    st.subheader("Common words in each sentiment")
    st.caption(
        "Simple word-frequency signals only; this is not topic modelling."
    )

    stopwords = {
        "the", "and", "for", "you", "are", "this", "that", "with", "was",
        "but", "not", "have", "has", "had", "they", "them", "your", "our",
        "from", "very", "just", "its", "it's", "what", "when", "where",
        "who", "how", "all", "can", "will", "would", "about", "been",
        "there", "their", "out", "she", "her", "his", "him", "too", "only",
        "into", "more", "than", "then", "also", "because", "love", "like",
        "sapphire", "video", "please", "https", "http", "www", "com"
    }

    def frequent_words(series):
        words = []
        for sentence in series.astype(str):
            tokens = re.findall(r"[a-zA-Z]{3,}", sentence.lower())
            words.extend(
                word for word in tokens
                if word not in stopwords
            )
        if not words:
            return pd.DataFrame(columns=["Word", "Frequency"])
        return (
            pd.Series(words).value_counts().head(10)
            .rename_axis("Word")
            .reset_index(name="Frequency")
        )

    word_cols = st.columns(3)
    for col, sentiment in zip(
        word_cols, ["Positive", "Neutral", "Negative"]
    ):
        with col:
            st.markdown(f"**{sentiment}**")
            subset = filtered[
                filtered["sentiment_label"] == sentiment
            ]
            words = frequent_words(subset["comment_text"])
            if words.empty:
                st.caption("Not enough English words to display.")
            else:
                fig = px.bar(
                    words.sort_values("Frequency"),
                    x="Frequency",
                    y="Word",
                    orientation="h"
                )
                st.plotly_chart(
                    style_fig(fig),
                    use_container_width=True
                )

# --------------------------------------------------
# VIDEO PERFORMANCE
# --------------------------------------------------
with videos_tab:
    st.subheader("Compare videos")

    video_stats = (
        filtered.groupby("video_id")
        .agg(
            comments=("comment_text", "size"),
            total_likes=("like_count", "sum"),
            average_likes=("like_count", "mean"),
            total_replies=("reply_count", "sum"),
            average_replies=("reply_count", "mean")
        )
        .reset_index()
        .sort_values("comments", ascending=False)
    )

    if not video_stats.empty:
        left, right = st.columns(2)

        with left:
            fig = px.bar(
                video_stats,
                x="video_id",
                y="comments",
                hover_data=["total_likes", "total_replies"]
            )
            st.plotly_chart(
                style_fig(fig, "Comments per video"),
                use_container_width=True
            )

        with right:
            fig = px.scatter(
                video_stats,
                x="comments",
                y="total_likes",
                size="total_replies",
                hover_name="video_id",
                labels={
                    "comments": "Comments",
                    "total_likes": "Total likes",
                    "total_replies": "Total replies"
                }
            )
            st.plotly_chart(
                style_fig(fig, "Volume versus engagement"),
                use_container_width=True
            )

        st.dataframe(
            video_stats,
            use_container_width=True,
            hide_index=True
        )

    if "comment_date" in filtered.columns:
        dated = filtered.dropna(subset=["comment_date"])
        if not dated.empty:
            daily = (
                dated.groupby(dated["comment_date"].dt.date)
                .size()
                .reset_index(name="comments")
            )
            daily.columns = ["Date", "Comments"]
            fig = px.line(
                daily, x="Date", y="Comments", markers=True
            )
            st.plotly_chart(
                style_fig(fig, "Comment activity over time"),
                use_container_width=True
            )
        else:
            st.info("No valid comment dates are available.")

# --------------------------------------------------
# COMMENT EXPLORER
# --------------------------------------------------
with explorer:
    st.subheader("Search and inspect comments")

    query = st.text_input(
        "Search comment text",
        placeholder="Enter a word or phrase..."
    )

    view = filtered.copy()

    if query:
        view = view[
            view["comment_text"].str.contains(
                query, case=False, na=False, regex=False
            )
        ]

    st.caption(f"{len(view):,} matching comments")

    display_cols = [
        c for c in [
            "video_id", "comment_text", "sentiment_label",
            "like_count", "reply_count", "comment_date"
        ] if c in view.columns
    ]

    st.dataframe(
        view[display_cols],
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download filtered comments",
        data=view.to_csv(index=False).encode("utf-8"),
        file_name="filtered_sapphire_comments.csv",
        mime="text/csv"
    )

    st.download_button(
        "Download complete labeled dataset",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="sapphire_youtube_comments_labeled.csv",
        mime="text/csv"
    )

# --------------------------------------------------
# DATA QUALITY
# --------------------------------------------------
with quality:
    st.subheader("Dataset quality and limitations")

    q1, q2, q3 = st.columns(3)
    q1.metric("Dataset rows", f"{len(df):,}")
    q2.metric("Blank comments", f"{df['comment_text'].str.strip().eq('').sum():,}")
    q3.metric("Duplicate comment IDs",
              f"{df['comment_id'].duplicated().sum():,}"
              if "comment_id" in df.columns else "Not available")

    quality_table = pd.DataFrame({
        "Column": df.columns,
        "Missing values": [int(df[c].isna().sum()) for c in df.columns],
        "Missing (%)": [
            round(df[c].isna().mean() * 100, 2)
            for c in df.columns
        ],
        "Unique values": [int(df[c].nunique(dropna=True)) for c in df.columns]
    })

    st.dataframe(
        quality_table,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### Interpretation cautions")
    st.markdown("""
    - Automated sentiment predictions are not verified ground truth.
    - Sarcasm, short comments, emojis, and Roman Urdu or Urdu can affect model accuracy.
    - A small sample may not represent all Sapphire customers or viewers.
    - Likes and replies measure visible engagement, not customer satisfaction by themselves.
    - Common-word charts show frequency, not the meaning or cause of a sentiment.
    """)

    st.download_button(
        "Download data quality report",
        data=quality_table.to_csv(index=False).encode("utf-8"),
        file_name="sapphire_data_quality.csv",
        mime="text/csv"
    )

# --------------------------------------------------
# SCALING EXPERIMENT
# --------------------------------------------------
st.divider()
with st.expander("📈 Scaling experiment results"):
    if os.path.exists(SCALING_FILE):
        scaling = pd.read_csv(SCALING_FILE)
        st.dataframe(scaling, use_container_width=True, hide_index=True)

        size_candidates = [
            "rows", "row_count", "dataset_size", "num_rows",
            "records", "n_rows", "size"
        ]
        size_col = next(
            (c for c in size_candidates if c in scaling.columns),
            None
        )

        metric_candidates = [
            "runtime_seconds", "execution_time", "time_seconds",
            "runtime", "time", "memory_mb", "memory_usage_mb",
            "file_size_mb", "write_time_seconds"
        ]
        metric_cols = [
            c for c in metric_candidates
            if c in scaling.columns
            and pd.api.types.is_numeric_dtype(scaling[c])
        ]

        if size_col and metric_cols:
            metric = st.selectbox(
                "Scaling metric",
                metric_cols,
                key="scaling_metric"
            )
            fig = px.line(
                scaling,
                x=size_col,
                y=metric,
                markers=True
            )
            st.plotly_chart(
                style_fig(fig, f"{metric} as dataset size increases"),
                use_container_width=True
            )
        else:
            st.info(
                "The results are shown in the table. Adjust the chart's "
                "column mapping if your experiment uses different names."
            )

        st.download_button(
            "Download scaling results",
            data=scaling.to_csv(index=False).encode("utf-8"),
            file_name="scaling_results.csv",
            mime="text/csv"
        )
    else:
        st.info(
            "Add scaling_results.csv to your GitHub repository to display "
            "the experiment here."
        )

st.divider()
st.caption(
    "Sapphire Pakistan · Academic analytics project · "
    "Sentiment labels are model-generated estimates."
)
