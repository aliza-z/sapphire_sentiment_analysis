
import os
import re
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Sapphire Pakistan | Ad Sentiment Analysis",
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
# SIDEBAR: THEME AND FILTERS
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
                PAKISTAN · SENTIMENT ANALYSIS
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
    accent = ROYAL_BLUE
    soft_bg = "#142F52"
    plot_grid = "#24466F"
else:
    bg = PALE_BLUE
    sidebar_bg = BABY_BLUE
    card_bg = WHITE
    text_color = "#102747"
    muted_color = "#526987"
    border_color = "#C7DDF5"
    accent = ROYAL_BLUE
    soft_bg = "#DCEEFF"
    plot_grid = "#DCE7F5"

# --------------------------------------------------
# CSS: REMOVE ORANGE FROM STREAMLIT ELEMENTS
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

    [data-testid="stCaptionContainer"],
    .muted {{
        color: {muted_color} !important;
    }}

    /* Metric cards */
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

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button {{
        background: {ROYAL_BLUE} !important;
        color: #FFFFFF !important;
        border: 1px solid {ROYAL_BLUE} !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease;
    }}

    .stButton > button:hover,
    .stDownloadButton > button:hover {{
        background: {BLUE_HOVER} !important;
        border-color: {BLUE_HOVER} !important;
        color: #FFFFFF !important;
    }}

    .stButton > button:focus,
    .stDownloadButton > button:focus {{
        box-shadow: 0 0 0 2px {bg}, 0 0 0 4px {ROYAL_BLUE} !important;
    }}

    /* Inputs and dropdowns */
    input, textarea {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border-color: {border_color} !important;
        caret-color: {ROYAL_BLUE} !important;
    }}

    input:focus, textarea:focus {{
        border-color: {ROYAL_BLUE} !important;
        box-shadow: 0 0 0 1px {ROYAL_BLUE} !important;
    }}

    [data-baseweb="select"] > div {{
        background-color: {card_bg} !important;
        border-color: {border_color} !important;
    }}

    [data-baseweb="select"] * {{
        color: {text_color} !important;
    }}

    /* Radio buttons */
    [data-testid="stRadio"] label {{
        color: {text_color} !important;
    }}

    [data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {{
        color: {text_color} !important;
    }}

    /* Checkbox */
    [data-testid="stCheckbox"] label {{
        color: {text_color} !important;
    }}

    /* Sliders: royal-blue track and thumb */
    [data-testid="stSlider"] [role="slider"] {{
        background: {ROYAL_BLUE} !important;
        border-color: {ROYAL_BLUE} !important;
    }}

    [data-testid="stSlider"] [data-baseweb="slider"] > div > div {{
        background: {ROYAL_BLUE} !important;
    }}

    /* Tabs */
    button[data-baseweb="tab"] {{
        color: {muted_color} !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {ROYAL_BLUE} !important;
        border-bottom-color: {ROYAL_BLUE} !important;
    }}

    /* Expanders */
    [data-testid="stExpander"] {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 10px;
    }}

    /* Data tables */
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {{
        border: 1px solid {border_color};
        border-radius: 10px;
        overflow: hidden;
    }}

    /* Links and progress */
    a {{
        color: {ROYAL_BLUE} !important;
    }}

    [data-testid="stProgressBar"] > div > div {{
        background-color: {ROYAL_BLUE} !important;
    }}

    /* Focus outlines */
    *:focus-visible {{
        outline-color: {ROYAL_BLUE} !important;
    }}

    hr {{
        border-color: {border_color};
    }}

    /* Sapphire dashboard components */
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
DATA_FILE = "sapphire_youtube_comments_labeled.csv"
SCALING_FILE = "scaling_results.csv"


@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)


if not os.path.exists(DATA_FILE):
    st.error(f"Dataset not found: `{DATA_FILE}`")
    st.info(
        "Place sapphire_youtube_comments_labeled.csv "
        "in the same folder as app.py."
    )
    st.stop()

try:
    df = load_data(DATA_FILE)
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

required_columns = ["comment_text", "sentiment_label"]
missing_columns = [c for c in required_columns if c not in df.columns]

if missing_columns:
    st.error(
        "The dataset is missing required columns: "
        + ", ".join(missing_columns)
    )
    st.write("Available columns:", list(df.columns))
    st.stop()

# Add optional columns if not present
for col, default in [
    ("video_id", "Unknown advertisement"),
    ("like_count", 0),
    ("reply_count", 0),
    ("aspect_label", "Unspecified"),
]:
    if col not in df.columns:
        df[col] = default

df["comment_text"] = df["comment_text"].fillna("").astype(str)
df["sentiment_label"] = (
    df["sentiment_label"].fillna("Unknown").astype(str).str.strip()
)
df["video_id"] = df["video_id"].fillna("Unknown advertisement").astype(str)
df["like_count"] = pd.to_numeric(df["like_count"], errors="coerce").fillna(0)
df["reply_count"] = pd.to_numeric(df["reply_count"], errors="coerce").fillna(0)
df["aspect_label"] = df["aspect_label"].fillna("Unspecified").astype(str)

# Friendly advertisement labels for the interface
video_ids = list(df["video_id"].drop_duplicates())
video_names = {
    video_id: f"Advertisement {i + 1:02d}"
    for i, video_id in enumerate(video_ids)
}
df["advertisement"] = df["video_id"].map(video_names)

# Normalize sentiment display labels
df["sentiment_display"] = df["sentiment_label"].str.title()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
with st.sidebar:
    st.divider()
    st.markdown("### Dashboard Filters")

    ad_options = ["All advertisements"] + list(df["advertisement"].unique())
    selected_ad = st.selectbox("Advertisement", ad_options)

    sentiment_options = ["All sentiments"] + sorted(
        df["sentiment_display"].dropna().unique().tolist()
    )
    selected_sentiment = st.selectbox("Sentiment", sentiment_options)

    max_likes = int(max(0, df["like_count"].max()))
    min_likes = st.slider(
        "Minimum likes",
        min_value=0,
        max_value=max(1, max_likes),
        value=0
    )

    st.divider()
    st.caption(f"{len(df):,} comments loaded")
    st.caption("Sapphire Pakistan · YouTube analysis")

# Apply filters
filtered_df = df.copy()

if selected_ad != "All advertisements":
    filtered_df = filtered_df[filtered_df["advertisement"] == selected_ad]

if selected_sentiment != "All sentiments":
    filtered_df = filtered_df[
        filtered_df["sentiment_display"] == selected_sentiment
    ]

filtered_df = filtered_df[filtered_df["like_count"] >= min_likes]

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------
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
        ),
    )
    return fig


def section_title(title, subtitle=None):
    st.markdown(
        f'<div class="section-heading">{title}</div>',
        unsafe_allow_html=True
    )
    if subtitle:
        st.caption(subtitle)


def metric_card(label, value, help_text=None):
    st.metric(label=label, value=value, help=help_text)


def get_sentiment_counts(data):
    return (
        data["sentiment_display"]
        .value_counts()
        .rename_axis("Sentiment")
        .reset_index(name="Comments")
    )


# --------------------------------------------------
# DASHBOARD HEADER
# --------------------------------------------------
st.markdown(
    """
    <div class="dashboard-header">
        <div class="eyebrow">SAPPHIRE PAKISTAN</div>
        <div class="dashboard-title">Ad Sentiment Analysis</div>
        <div class="dashboard-subtitle">
            Understanding audience reactions to Sapphire's YouTube
            advertisements through comment sentiment.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# --------------------------------------------------
# OVERVIEW METRICS
# --------------------------------------------------
total_comments = len(filtered_df)
positive_count = int(
    (filtered_df["sentiment_display"].str.lower() == "positive").sum()
)
negative_count = int(
    (filtered_df["sentiment_display"].str.lower() == "negative").sum()
)
neutral_count = int(
    (filtered_df["sentiment_display"].str.lower() == "neutral").sum()
)

positive_pct = (
    positive_count / total_comments * 100 if total_comments else 0
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    metric_card("Total comments", f"{total_comments:,}")

with c2:
    metric_card("Positive comments", f"{positive_count:,}")

with c3:
    metric_card("Negative comments", f"{negative_count:,}")

with c4:
    metric_card("Positive share", f"{positive_pct:.1f}%")

st.write("")

# --------------------------------------------------
# NAVIGATION TABS
# --------------------------------------------------
overview_tab, sentiment_tab, ads_tab, comments_tab, quality_tab = st.tabs(
    [
        "Overview",
        "Sentiment",
        "Advertisement Performance",
        "Comments",
        "Data Quality",
    ]
)

# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------
with overview_tab:
    section_title(
        "Sentiment overview",
        "A snapshot of the sentiment distribution for the selected data."
    )

    if filtered_df.empty:
        st.warning("No comments match the selected filters.")
    else:
        left, right = st.columns([1, 1.3])

        sentiment_counts = get_sentiment_counts(filtered_df)

        with left:
            fig = px.pie(
                sentiment_counts,
                names="Sentiment",
                values="Comments",
                hole=0.62,
                color_discrete_sequence=BLUE_PALETTE,
            )
            fig.update_traces(
                textposition="inside",
                textinfo="percent+label",
                marker=dict(
                    line=dict(color=card_bg, width=2)
                )
            )
            fig.update_layout(
                annotations=[
                    dict(
                        text=f"{total_comments:,}<br>Comments",
                        x=0.5,
                        y=0.5,
                        font=dict(size=17, color=text_color),
                        showarrow=False
                    )
                ]
            )
            st.plotly_chart(
                style_fig(fig),
                width="stretch",
                config={"displayModeBar": False}
            )

        with right:
            fig = px.bar(
                sentiment_counts,
                x="Sentiment",
                y="Comments",
                color="Sentiment",
                color_discrete_sequence=BLUE_PALETTE,
                text="Comments",
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

    st.write("")
    section_title("Quick findings")

    if not filtered_df.empty:
        counts = filtered_df["sentiment_display"].value_counts()
        dominant = counts.index[0] if not counts.empty else "Unknown"
        most_liked = filtered_df.loc[filtered_df["like_count"].idxmax()]

        insight1, insight2 = st.columns(2)

        with insight1:
            st.markdown(
                f"""
                <div class="info-card">
                    <strong>Most common sentiment</strong>
                    <p style="font-size:22px;margin-top:8px;">
                        {dominant}
                    </p>
                    <p>
                        This is the most frequently assigned sentiment
                        in the currently filtered comments.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with insight2:
            st.markdown(
                f"""
                <div class="info-card">
                    <strong>Most-liked comment</strong>
                    <p style="margin-top:8px;">
                        {most_liked["comment_text"][:250]}
                    </p>
                    <p>
                        {int(most_liked["like_count"]):,} likes ·
                        {most_liked["advertisement"]}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.download_button(
            "Download filtered comments",
            data=filtered_df.to_csv(index=False).encode("utf-8"),
            file_name="sapphire_filtered_comments.csv",
            mime="text/csv",
            width="stretch"
        )

# --------------------------------------------------
# SENTIMENT TAB
# --------------------------------------------------
with sentiment_tab:
    section_title(
        "Sentiment breakdown",
        "Compare sentiment labels and inspect their distribution."
    )

    if filtered_df.empty:
        st.warning("No comments match the selected filters.")
    else:
        sentiment_counts = get_sentiment_counts(filtered_df)

        fig = px.bar(
            sentiment_counts,
            x="Sentiment",
            y="Comments",
            color="Sentiment",
            text="Comments",
            color_discrete_sequence=BLUE_PALETTE,
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

        st.dataframe(
            sentiment_counts,
            width="stretch",
            hide_index=True
        )

        aspect_counts = (
            filtered_df["aspect_label"]
            .value_counts()
            .head(12)
            .rename_axis("Aspect")
            .reset_index(name="Comments")
        )

        if not aspect_counts.empty:
            section_title("Frequently discussed aspects")

            fig = px.bar(
                aspect_counts.sort_values("Comments"),
                x="Comments",
                y="Aspect",
                orientation="h",
                color_discrete_sequence=[ROYAL_BLUE],
                text="Comments",
            )
            fig.update_traces(
                textposition="outside",
                marker_line_width=0
            )

            st.plotly_chart(
                style_fig(fig, 420),
                width="stretch",
                config={"displayModeBar": False}
            )

# --------------------------------------------------
# ADVERTISEMENT PERFORMANCE TAB
# --------------------------------------------------
with ads_tab:
    section_title(
        "Advertisement performance",
        "Compare comment volume, sentiment, and engagement by advertisement."
    )

    if filtered_df.empty:
        st.warning("No comments match the selected filters.")
    else:
        ad_summary = (
            filtered_df.groupby("advertisement", as_index=False)
            .agg(
                Total_Comments=("comment_text", "count"),
                Total_Likes=("like_count", "sum"),
                Average_Likes=("like_count", "mean"),
                Average_Replies=("reply_count", "mean"),
            )
        )

        sentiment_pivot = pd.crosstab(
            filtered_df["advertisement"],
            filtered_df["sentiment_display"]
        ).reset_index()

        ad_summary = ad_summary.merge(
            sentiment_pivot,
            on="advertisement",
            how="left"
        ).fillna(0)

        if "Positive" in ad_summary.columns:
            ad_summary["Positive_Percentage"] = (
                ad_summary["Positive"]
                / ad_summary["Total_Comments"].replace(0, 1)
                * 100
            )
        else:
            ad_summary["Positive_Percentage"] = 0

        fig = px.bar(
            ad_summary.sort_values("Total_Comments", ascending=False),
            x="advertisement",
            y="Total_Comments",
            color_discrete_sequence=[ROYAL_BLUE],
            text="Total_Comments",
        )
        fig.update_traces(
            textposition="outside",
            marker_line_width=0
        )

        st.plotly_chart(
            style_fig(fig, 400),
            width="stretch",
            config={"displayModeBar": False}
        )

        section_title("Advertisement comparison")

        display_summary = ad_summary.rename(
            columns={
                "advertisement": "Advertisement",
                "Total_Comments": "Total comments",
                "Total_Likes": "Total likes",
                "Average_Likes": "Average likes",
                "Average_Replies": "Average replies",
                "Positive_Percentage": "Positive comments (%)",
            }
        )

        st.dataframe(
            display_summary.round(2),
            width="stretch",
            hide_index=True
        )

        st.download_button(
            "Download advertisement summary",
            data=display_summary.to_csv(index=False).encode("utf-8"),
            file_name="sapphire_advertisement_summary.csv",
            mime="text/csv",
            width="stretch"
        )

# --------------------------------------------------
# COMMENTS TAB
# --------------------------------------------------
with comments_tab:
    section_title(
        "Explore comments",
        "Search comment text and inspect the corresponding sentiment labels."
    )

    search_text = st.text_input(
        "Search comments",
        placeholder="Enter a keyword or phrase..."
    )

    comment_view = filtered_df.copy()

    if search_text.strip():
        comment_view = comment_view[
            comment_view["comment_text"].str.contains(
                re.escape(search_text.strip()),
                case=False,
                na=False,
                regex=True
            )
        ]

    display_columns = [
        "advertisement",
        "comment_text",
        "sentiment_display",
        "aspect_label",
        "like_count",
        "reply_count",
    ]

    display_comments = comment_view[display_columns].rename(
        columns={
            "advertisement": "Advertisement",
            "comment_text": "Comment",
            "sentiment_display": "Sentiment",
            "aspect_label": "Aspect",
            "like_count": "Likes",
            "reply_count": "Replies",
        }
    )

    st.caption(f"{len(display_comments):,} matching comments")

    st.dataframe(
        display_comments,
        width="stretch",
        hide_index=True,
        height=480,
        column_config={
            "Comment": st.column_config.TextColumn(
                "Comment",
                width="large"
            ),
            "Advertisement": st.column_config.TextColumn(
                "Advertisement",
                width="medium"
            ),
        }
    )

    st.download_button(
        "Download comments",
        data=display_comments.to_csv(index=False).encode("utf-8"),
        file_name="sapphire_comments.csv",
        mime="text/csv",
        width="stretch"
    )

    st.write("")
    section_title("Most-liked comments")

    top_comments = (
        comment_view.sort_values("like_count", ascending=False)
        .head(10)[
            [
                "advertisement",
                "comment_text",
                "sentiment_display",
                "like_count",
            ]
        ]
        .rename(
            columns={
                "advertisement": "Advertisement",
                "comment_text": "Comment",
                "sentiment_display": "Sentiment",
                "like_count": "Likes",
            }
        )
    )

    st.dataframe(
        top_comments,
        width="stretch",
        hide_index=True
    )

# --------------------------------------------------
# DATA QUALITY TAB
# --------------------------------------------------
with quality_tab:
    section_title(
        "Dataset health",
        "Review missing values, duplicate comments, and sentiment coverage."
    )

    total_rows = len(df)
    missing_text = int(df["comment_text"].str.strip().eq("").sum())
    missing_sentiment = int(
        df["sentiment_label"].str.strip().eq("").sum()
    )
    duplicate_comments = int(
        df["comment_text"].duplicated().sum()
    )

    q1, q2, q3, q4 = st.columns(4)

    with q1:
        metric_card("Dataset rows", f"{total_rows:,}")

    with q2:
        metric_card("Blank comments", f"{missing_text:,}")

    with q3:
        metric_card("Blank sentiment", f"{missing_sentiment:,}")

    with q4:
        metric_card("Duplicate comments", f"{duplicate_comments:,}")

    st.write("")
    section_title("Missing values by column")

    missing_df = (
        df.isna()
        .sum()
        .rename_axis("Column")
        .reset_index(name="Missing values")
    )
    missing_df["Missing percentage"] = (
        missing_df["Missing values"] / max(len(df), 1) * 100
    )

    fig = px.bar(
        missing_df.sort_values("Missing values", ascending=False),
        x="Column",
        y="Missing values",
        color_discrete_sequence=[ROYAL_BLUE],
        text="Missing values",
    )
    fig.update_traces(
        textposition="outside",
        marker_line_width=0
    )

    st.plotly_chart(
        style_fig(fig, 360),
        width="stretch",
        config={"displayModeBar": False}
    )

    st.dataframe(
        missing_df.round(2),
        width="stretch",
        hide_index=True
    )

    with st.expander("View original dataset columns"):
        st.write(list(df.columns))
        st.dataframe(df.head(50), width="stretch")

    if os.path.exists(SCALING_FILE):
        with st.expander("View model scaling results"):
            try:
                scaling_df = load_data(SCALING_FILE)
                st.dataframe(
                    scaling_df,
                    width="stretch",
                    hide_index=True
                )

                numeric_cols = scaling_df.select_dtypes(
                    include="number"
                ).columns.tolist()

                if len(numeric_cols) >= 1 and len(scaling_df) > 0:
                    plot_col = st.selectbox(
                        "Metric to compare",
                        numeric_cols
                    )

                    label_candidates = [
                        c for c in scaling_df.columns
                        if c not in numeric_cols
                    ]

                    if label_candidates:
                        label_col = label_candidates[0]
                        fig = px.bar(
                            scaling_df,
                            x=label_col,
                            y=plot_col,
                            color_discrete_sequence=[ROYAL_BLUE],
                            text=plot_col,
                        )
                        fig.update_traces(
                            textposition="outside",
                            marker_line_width=0
                        )

                        st.plotly_chart(
                            style_fig(fig, 360),
                            width="stretch",
                            config={"displayModeBar": False}
                        )
            except Exception as exc:
                st.warning(f"Could not load scaling results: {exc}")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()

st.markdown(
    f"""
    <div style="text-align:center;padding:12px 0 20px 0;">
        <div style="font-weight:800;letter-spacing:2px;
                    color:{ROYAL_BLUE};">
            SAPPHIRE PAKISTAN
        </div>
        <div style="color:{muted_color};font-size:12px;margin-top:6px;">
            YouTube Comment Sentiment Analysis Dashboard
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
