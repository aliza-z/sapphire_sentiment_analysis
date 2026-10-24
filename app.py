
import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="Sapphire Analytics",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #f6f8f4;
}
h1, h2, h3 {
    color: #254d3a;
}
[data-testid="stMetric"] {
    background: white;
    padding: 16px;
    border-radius: 12px;
    border: 1px solid #e1e8df;
}
</style>
""", unsafe_allow_html=True)

st.title("Sapphire Pakistan")
st.subheader("YouTube Comment Analytics Dashboard")
st.caption(
    "Sentiment, audience engagement, and scaling experiment analysis"
)

DATA_FILE = "sapphire_youtube_comments_labeled.csv"
SCALING_FILE = "scaling_results.csv"

if not os.path.exists(DATA_FILE):
    st.error(f"Missing file: {DATA_FILE}")
    st.info("Upload the labeled CSV to the GitHub repository.")
    st.stop()

df = pd.read_csv(DATA_FILE)

# Standardize column names
df.columns = df.columns.str.strip().str.lower()

# Check required columns
if "comment_text" not in df.columns:
    st.error("The dataset must contain a comment_text column.")
    st.stop()

if "video_id" not in df.columns:
    df["video_id"] = "Unknown"

if "sentiment_label" not in df.columns:
    df["sentiment_label"] = "Unknown"

for col in ["like_count", "reply_count"]:
    if col not in df.columns:
        df[col] = 0
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

if "comment_date" in df.columns:
    df["comment_date"] = pd.to_datetime(
        df["comment_date"], errors="coerce", utc=True
    )

# Sidebar filters
st.sidebar.header("Dashboard Filters")

videos = sorted(df["video_id"].dropna().astype(str).unique())
selected_videos = st.sidebar.multiselect(
    "Select videos",
    videos,
    default=videos
)

sentiments = sorted(
    df["sentiment_label"].fillna("Unknown").astype(str).unique()
)
selected_sentiments = st.sidebar.multiselect(
    "Select sentiments",
    sentiments,
    default=sentiments
)

filtered = df[
    df["video_id"].astype(str).isin(selected_videos)
    & df["sentiment_label"].fillna("Unknown").astype(str).isin(
        selected_sentiments
    )
].copy()

# KPI cards
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Comments", f"{len(filtered):,}")
c2.metric("Videos Analyzed", filtered["video_id"].nunique())
c3.metric("Average Likes", f"{filtered['like_count'].mean():.2f}")
c4.metric("Average Replies", f"{filtered['reply_count'].mean():.2f}")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "Engagement",
    "Sentiment",
    "Comment Explorer",
    "Scaling Experiment"
])

with tab1:
    st.header("Audience Engagement")

    if filtered.empty:
        st.warning("No comments match the selected filters.")
    else:
        video_counts = (
            filtered.groupby("video_id")
            .size()
            .reset_index(name="comments")
        )

        fig = px.bar(
            video_counts,
            x="video_id",
            y="comments",
            title="Comments per Video",
            labels={"video_id": "Video ID", "comments": "Number of Comments"}
        )
        st.plotly_chart(fig, use_container_width=True)

        left, right = st.columns(2)

        with left:
            fig = px.histogram(
                filtered,
                x="like_count",
                nbins=15,
                title="Distribution of Comment Likes",
                labels={"like_count": "Likes"}
            )
            st.plotly_chart(fig, use_container_width=True)

        with right:
            fig = px.scatter(
                filtered,
                x="like_count",
                y="reply_count",
                title="Likes vs Replies",
                labels={
                    "like_count": "Likes",
                    "reply_count": "Replies"
                },
                hover_data=["video_id"]
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Video Summary")
        summary = (
            filtered.groupby("video_id")
            .agg(
                comments=("comment_text", "count"),
                total_likes=("like_count", "sum"),
                average_likes=("like_count", "mean"),
                total_replies=("reply_count", "sum")
            )
            .reset_index()
        )
        st.dataframe(summary, use_container_width=True)

with tab2:
    st.header("Predicted Sentiment Analysis")

    if filtered.empty:
        st.warning("No comments match the selected filters.")
    else:
        sentiment_counts = (
            filtered["sentiment_label"]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
            .rename_axis("Sentiment")
            .reset_index(name="Comments")
        )

        left, right = st.columns(2)

        with left:
            fig = px.pie(
                sentiment_counts,
                names="Sentiment",
                values="Comments",
                title="Sentiment Distribution",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)

        with right:
            fig = px.bar(
                sentiment_counts,
                x="Sentiment",
                y="Comments",
                title="Comments by Sentiment"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.info(
            "Sentiment labels are automated model predictions, not "
            "human-verified ground truth. Sarcasm, slang, and Urdu or "
            "Roman Urdu may affect prediction quality."
        )

        if (
            "aspect_label" in filtered.columns
            and filtered["aspect_label"].notna().any()
        ):
            st.subheader("Aspect Analysis")
            aspect_counts = (
                filtered["aspect_label"]
                .dropna()
                .astype(str)
                .value_counts()
                .reset_index()
            )
            aspect_counts.columns = ["Aspect", "Comments"]
            fig = px.bar(
                aspect_counts,
                x="Aspect",
                y="Comments",
                title="Comments by Aspect"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption(
                "Aspect analysis is unavailable because aspect labels "
                "have not been populated."
            )

with tab3:
    st.header("Explore Individual Comments")

    search_text = st.text_input("Search comment text")

    view = filtered.copy()

    if search_text:
        view = view[
            view["comment_text"].astype(str).str.contains(
                search_text, case=False, na=False
            )
        ]

    display_cols = [
        col for col in [
            "video_id", "comment_text", "sentiment_label",
            "like_count", "reply_count", "comment_date"
        ] if col in view.columns
    ]

    st.write(f"Showing {len(view)} comments")
    st.dataframe(view[display_cols], use_container_width=True)

    st.download_button(
        "Download filtered comments",
        data=view.to_csv(index=False).encode("utf-8"),
        file_name="filtered_sapphire_comments.csv",
        mime="text/csv"
    )

    st.download_button(
        "Download full labeled dataset",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="sapphire_youtube_comments_labeled.csv",
        mime="text/csv"
    )

with tab4:
    st.header("Scaling Experiment")

    if os.path.exists(SCALING_FILE):
        scaling = pd.read_csv(SCALING_FILE)
        st.write("Scaling experiment results")
        st.dataframe(scaling, use_container_width=True)

        # Find a likely workload-size column
        possible_size_cols = [
            "rows", "row_count", "dataset_size", "num_rows",
            "records", "n_rows", "size"
        ]
        size_col = next(
            (c for c in possible_size_cols if c in scaling.columns),
            None
        )

        possible_metric_cols = [
            "runtime_seconds", "execution_time", "time_seconds",
            "runtime", "time", "memory_mb", "memory_usage_mb",
            "file_size_mb", "write_time_seconds"
        ]

        metric_cols = [
            c for c in possible_metric_cols
            if c in scaling.columns
            and pd.api.types.is_numeric_dtype(scaling[c])
        ]

        if size_col and metric_cols:
            metric = st.selectbox(
                "Select scaling metric",
                metric_cols
            )

            fig = px.line(
                scaling,
                x=size_col,
                y=metric,
                markers=True,
                title=f"{metric} versus workload size"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(
                "A chart could not be generated automatically. "
                "Check the column names in scaling_results.csv."
            )

        st.download_button(
            "Download scaling results",
            data=scaling.to_csv(index=False).encode("utf-8"),
            file_name="scaling_results.csv",
            mime="text/csv"
        )
    else:
        st.warning(
            "scaling_results.csv is missing. Upload it to the repository "
            "to display scaling charts."
        )

st.divider()
st.caption(
    "Academic project | Sapphire Pakistan YouTube Comment Analytics"
)
