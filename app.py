import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Sapphire Pakistan | Ad Sentiment Analysis",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "sapphire_youtube_comments_labeled.csv"
SCALING_FILE = "scaling_results.csv"

SENTIMENT_ORDER = ["Positive", "Neutral", "Negative", "Unknown"]

SENTIMENT_COLORS = {
    "Positive": "#299879",
    "Neutral": "#91A1B9",
    "Negative": "#D66F7A",
    "Unknown": "#A99AC8",
}

CHART_COLORS = [
    "#527DB8", "#299879", "#D66F7A",
    "#A99AC8", "#D0A35B", "#5CAFC2"
]


# ============================================================
# DATA FUNCTIONS
# ============================================================
@st.cache_data
def load_csv(path, modified_time):
    return pd.read_csv(path)


def find_column(columns, candidates):
    lookup = {str(c).strip().lower(): c for c in columns}

    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]

    return None


def normalise_sentiment(value):
    if pd.isna(value):
        return "Unknown"

    value = str(value).strip().lower()

    labels = {
        "positive": "Positive",
        "pos": "Positive",
        "label_2": "Positive",
        "2": "Positive",

        "neutral": "Neutral",
        "neu": "Neutral",
        "label_1": "Neutral",
        "1": "Neutral",

        "negative": "Negative",
        "neg": "Negative",
        "label_0": "Negative",
        "0": "Negative",

        "unknown": "Unknown",
        "unlabelled": "Unknown",
        "unlabeled": "Unknown",
        "": "Unknown",
        "nan": "Unknown",
        "none": "Unknown",
    }

    return labels.get(value, value.title())


def prepare_data(raw):
    df = raw.copy()
    df.columns = [str(c).strip() for c in df.columns]

    aliases = {
        "video_id": [
            "video_id", "video id", "video",
            "ad_id", "ad id"
        ],
        "comment_id": [
            "comment_id", "comment id", "id"
        ],
        "comment_text": [
            "comment_text", "comment text",
            "text", "comment"
        ],
        "comment_date": [
            "comment_date", "comment date",
            "published_at", "date"
        ],
        "like_count": [
            "like_count", "like count", "likes"
        ],
        "reply_count": [
            "reply_count", "reply count", "replies"
        ],
        "sentiment_label": [
            "sentiment_label", "sentiment label",
            "sentiment", "predicted_sentiment"
        ],
        "aspect_label": [
            "aspect_label", "aspect label",
            "aspect", "topic"
        ],
    }

    rename = {}

    for standard, candidates in aliases.items():
        found = find_column(df.columns, candidates)

        if found is not None and found != standard:
            rename[found] = standard

    df = df.rename(columns=rename)

    if "comment_text" not in df.columns:
        st.error(
            "The CSV needs a comment text column. "
            "Expected comment_text, text or comment."
        )
        st.stop()

    defaults = {
        "video_id": "Unknown video",
        "comment_id": "",
        "comment_date": None,
        "like_count": 0,
        "reply_count": 0,
        "sentiment_label": "Unknown",
        "aspect_label": "Unlabelled",
    }

    for column, default in defaults.items():
        if column not in df.columns:
            df[column] = default

    df["comment_text"] = (
        df["comment_text"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df = df[df["comment_text"] != ""].copy()

    df["video_id"] = (
        df["video_id"]
        .fillna("Unknown video")
        .astype(str)
    )

    df["comment_id"] = (
        df["comment_id"]
        .fillna("")
        .astype(str)
    )

    df["sentiment_label"] = (
        df["sentiment_label"].apply(normalise_sentiment)
    )

    df["aspect_label"] = (
        df["aspect_label"]
        .fillna("Unlabelled")
        .astype(str)
        .str.strip()
        .replace({
            "": "Unlabelled",
            "nan": "Unlabelled",
            "None": "Unlabelled",
        })
    )

    for column in ["like_count", "reply_count"]:
        df[column] = (
            pd.to_numeric(df[column], errors="coerce")
            .fillna(0)
            .clip(lower=0)
        )

    df["comment_date"] = pd.to_datetime(
        df["comment_date"],
        errors="coerce",
        utc=True
    ).dt.tz_convert(None)

    # Friendly labels replace raw video IDs in charts and filters.
    # The original video IDs remain in the underlying dataset.
    video_ids = sorted(df["video_id"].unique())

    video_labels = {
        video_id: f"Ad {i:02d}"
        for i, video_id in enumerate(video_ids, start=1)
    }

    df["ad_label"] = df["video_id"].map(video_labels)

    return df


# ============================================================
# LOAD DATA
# ============================================================
if not Path(DATA_FILE).exists():
    st.error(
        f"Cannot find {DATA_FILE}. Put the CSV in the same "
        "GitHub repository folder as app.py."
    )
    st.stop()

raw_df = load_csv(DATA_FILE, os.path.getmtime(DATA_FILE))
df = prepare_data(raw_df)


# ============================================================
# THEME
# ============================================================
if "appearance" not in st.session_state:
    st.session_state.appearance = "Dark"

if st.session_state.appearance == "Dark":
    page_bg = "#0B1220"
    sidebar_bg = "#0E1728"
    card_bg = "#121E31"
    card_alt = "#192943"
    main_text = "#F0F4FA"
    muted_text = "#A0AEC2"
    line = "#293950"
    accent = "#82A9E8"
    grid = "#293950"
    chip_bg = "#263C5B"
    chip_text = "#F0F4FA"
    chart_template = "plotly_dark"

else:
    page_bg = "#F3F5F9"
    sidebar_bg = "#E9EEF5"
    card_bg = "#FFFFFF"
    card_alt = "#E9EFF7"
    main_text = "#17253D"
    muted_text = "#65748B"
    line = "#D8E1EC"
    accent = "#315F9E"
    grid = "#E1E7EF"
    chip_bg = "#DCE7F5"
    chip_text = "#1D3557"
    chart_template = "plotly_white"


# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown(
    f"""
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap'
    );

    :root {{
        --page-bg: {page_bg};
        --sidebar-bg: {sidebar_bg};
        --card-bg: {card_bg};
        --card-alt: {card_alt};
        --main-text: {main_text};
        --muted-text: {muted_text};
        --line: {line};
        --accent: {accent};
        --chip-bg: {chip_bg};
        --chip-text: {chip_text};
    }}

    html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif;
    }}

    .stApp {{
        background: var(--page-bg);
        color: var(--main-text);
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    [data-testid="stSidebar"] {{
        background: var(--sidebar-bg);
        border-right: 1px solid var(--line);
    }}

    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1.25rem;
    }}

    h1, h2, h3, h4 {{
        font-family: 'Manrope', sans-serif !important;
        color: var(--main-text) !important;
        letter-spacing: -0.035em;
    }}

    h1 {{
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }}

    h2 {{
        font-size: 1.45rem !important;
        font-weight: 700 !important;
    }}

    h3 {{
        font-size: 1.08rem !important;
        font-weight: 700 !important;
    }}

    p, label {{
        color: var(--main-text);
    }}

    [data-testid="stCaptionContainer"] p {{
        color: var(--muted-text) !important;
    }}

    /* Brand */

    .brand-lockup {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 5px 0 14px 0;
    }}

    .brand-mark {{
        width: 42px;
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid var(--line);
        border-radius: 8px;
        color: var(--main-text);
        font-family: 'Manrope', sans-serif;
        font-size: 25px;
        font-weight: 800;
    }}

    .brand-name {{
        color: var(--main-text);
        font-family: 'Manrope', sans-serif;
        font-size: 15px;
        font-weight: 800;
        letter-spacing: 2px;
    }}

    .brand-sub {{
        color: var(--muted-text);
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 2.5px;
        margin-top: 2px;
    }}

    .sidebar-rule {{
        border-top: 1px solid var(--line);
        margin: 12px 0 20px;
    }}

    /* Page heading */

    .hero {{
        background: var(--card-bg);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 28px 30px;
        margin: 5px 0 22px;
    }}

    .hero-kicker {{
        color: var(--accent);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 12px;
    }}

    .hero-title {{
        color: var(--main-text);
        font-family: 'Manrope', sans-serif;
        font-size: clamp(28px, 3vw, 38px);
        line-height: 1.2;
        letter-spacing: -1.4px;
        font-weight: 800;
    }}

    .hero-subtitle {{
        color: var(--muted-text);
        font-size: 14px;
        line-height: 1.7;
        margin-top: 10px;
        max-width: 760px;
    }}

    .section-note {{
        color: var(--muted-text);
        font-size: 13px;
        margin-top: -6px;
        margin-bottom: 14px;
    }}

    /* Insight panels */

    .insight-card {{
        background: var(--card-bg);
        border: 1px solid var(--line);
        border-left: 3px solid var(--accent);
        border-radius: 9px;
        padding: 14px 16px;
        margin-bottom: 10px;
        line-height: 1.6;
    }}

    .insight-title {{
        color: var(--main-text);
        font-weight: 700;
        margin-bottom: 3px;
    }}

    .insight-body {{
        color: var(--muted-text);
        font-size: 13px;
        overflow-wrap: anywhere;
    }}

    /* Metric cards */

    [data-testid="stMetric"] {{
        background: var(--card-bg);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 17px 18px;
    }}

    [data-testid="stMetricLabel"] {{
        color: var(--muted-text) !important;
        font-size: 12px;
        font-weight: 600;
    }}

    [data-testid="stMetricValue"] {{
        color: var(--main-text) !important;
        font-family: 'Manrope', sans-serif;
        font-weight: 800;
    }}

    /* Remove default red/orange selection accents */

    input, textarea, select {{
        accent-color: var(--accent) !important;
    }}

    [data-baseweb="radio"] div[aria-checked="true"] {{
        border-color: var(--accent) !important;
    }}

    [data-baseweb="radio"] div[aria-checked="true"]::after {{
        background-color: var(--accent) !important;
    }}

    [data-baseweb="checkbox"] div[aria-checked="true"] {{
        background-color: var(--accent) !important;
        border-color: var(--accent) !important;
    }}

    /* Multiselect chips */

    [data-baseweb="tag"] {{
        background: var(--chip-bg) !important;
        border: 1px solid var(--line) !important;
        border-radius: 6px !important;
    }}

    [data-baseweb="tag"] span {{
        color: var(--chip-text) !important;
    }}

    [data-baseweb="tag"] svg {{
        fill: var(--chip-text) !important;
    }}

    [data-baseweb="select"] > div {{
        border-color: var(--line) !important;
        border-radius: 8px !important;
    }}

    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div {{
        border-color: var(--line) !important;
        border-radius: 8px !important;
        background: var(--card-bg) !important;
    }}

    /* Buttons */

    .stButton > button,
    .stDownloadButton > button {{
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--card-bg);
        color: var(--main-text);
        font-weight: 600;
    }}

    .stButton > button:hover,
    .stDownloadButton > button:hover {{
        border-color: var(--accent);
        color: var(--accent);
        background: var(--card-bg);
    }}

    /* Tabs */

    [data-testid="stTabs"] [role="tablist"] {{
        gap: 16px;
        border-bottom: 1px solid var(--line);
    }}

    [data-testid="stTabs"] button[role="tab"] {{
        color: var(--muted-text);
        font-weight: 600;
    }}

    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
        color: var(--accent);
        border-bottom-color: var(--accent);
    }}

    /* Charts and tables */

    [data-testid="stPlotlyChart"] {{
        background: var(--card-bg);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 6px;
    }}

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {{
        border: 1px solid var(--line);
        border-radius: 9px;
        overflow: hidden;
    }}

    hr {{
        border-color: var(--line);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR BRAND AND FILTERS
# ============================================================
with st.sidebar:

    st.markdown(
        """
        <div class="brand-lockup">
            <div class="brand-mark">S</div>
            <div>
                <div class="brand-name">SAPPHIRE</div>
                <div class="brand-sub">PAKISTAN</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='sidebar-rule'></div>",
        unsafe_allow_html=True,
    )

    st.caption("DISPLAY MODE")

    st.radio(
        "Appearance",
        ["Dark", "Light"],
        key="appearance",
        horizontal=True,
        label_visibility="collapsed",
    )

    st.markdown(
        "<div class='sidebar-rule'></div>",
        unsafe_allow_html=True,
    )

    st.markdown("### Filters")
    st.caption("Choose which comments to include.")

    available_ads = sorted(df["ad_label"].unique().tolist())

    selected_ads = st.multiselect(
        "Advertisement",
        options=available_ads,
        default=available_ads,
        help=(
            "Ad labels are used instead of long YouTube IDs. "
            "The original IDs remain available in the Comments tab."
        ),
    )

    available_sentiments = [
        s for s in SENTIMENT_ORDER
        if s in df["sentiment_label"].unique()
    ]

    selected_sentiments = st.multiselect(
        "Predicted sentiment",
        options=available_sentiments,
        default=available_sentiments,
    )

    max_likes = int(df["like_count"].max()) if len(df) else 0

    if max_likes > 0:
        like_range = st.slider(
            "Likes per comment",
            min_value=0,
            max_value=max_likes,
            value=(0, max_likes),
        )
    else:
        like_range = (0, 0)

    st.markdown(
        "<div class='sidebar-rule'></div>",
        unsafe_allow_html=True,
    )

    st.caption("DATASET")
    st.write(f"{len(df):,} comments")
    st.write(f"{df['ad_label'].nunique():,} advertisements")
    st.caption(
        "Sentiment labels should be treated as model predictions "
        "unless manually verified."
    )


filtered = df[
    df["ad_label"].isin(selected_ads)
    & df["sentiment_label"].isin(selected_sentiments)
    & df["like_count"].between(like_range[0], like_range[1])
].copy()


# ============================================================
# CHART STYLE FUNCTION
# ============================================================
def style_fig(fig, title="", height=360):
    fig.update_layout(
        template=chart_template,
        title=dict(
            text=title,
            font=dict(size=16, color=main_text),
        ),
        font=dict(
            family="DM Sans, sans-serif",
            size=12,
            color=main_text,
        ),
        paper_bgcolor=card_bg,
        plot_bgcolor=card_bg,
        colorway=CHART_COLORS,
        margin=dict(l=18, r=18, t=60, b=38),
        height=height,
        legend_title_text="",
        hoverlabel=dict(
            bgcolor=card_alt,
            font_color=main_text,
            bordercolor=line,
        ),
    )

    fig.update_xaxes(
        gridcolor=grid,
        linecolor=line,
        zerolinecolor=grid,
        automargin=True,
    )

    fig.update_yaxes(
        gridcolor=grid,
        linecolor=line,
        zerolinecolor=grid,
        automargin=True,
    )

    return fig


# ============================================================
# MAIN HEADER
# ============================================================
st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">SAPPHIRE PAKISTAN</div>
        <div class="hero-title">Ad Sentiment Analysis</div>
        <div class="hero-subtitle">
            Analysis of YouTube comments, sentiment patterns,
            and engagement across Sapphire advertisements.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


if filtered.empty:
    st.warning(
        "No comments match the selected filters. "
        "Change the filters in the sidebar."
    )
    st.stop()


# ============================================================
# CALCULATE SUMMARY METRICS
# ============================================================
positive_n = int(
    (filtered["sentiment_label"] == "Positive").sum()
)
neutral_n = int(
    (filtered["sentiment_label"] == "Neutral").sum()
)
negative_n = int(
    (filtered["sentiment_label"] == "Negative").sum()
)
unknown_n = int(
    (filtered["sentiment_label"] == "Unknown").sum()
)

known_n = positive_n + neutral_n + negative_n

positive_pct = positive_n / known_n * 100 if known_n else 0
neutral_pct = neutral_n / known_n * 100 if known_n else 0
negative_pct = negative_n / known_n * 100 if known_n else 0

avg_likes = filtered["like_count"].mean()

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Comments", f"{len(filtered):,}")
k2.metric("Advertisements", f"{filtered['ad_label'].nunique():,}")
k3.metric("Positive sentiment", f"{positive_pct:.1f}%")
k4.metric("Negative sentiment", f"{negative_pct:.1f}%")
k5.metric("Average likes", f"{avg_likes:.2f}")


# ============================================================
# NAVIGATION
# ============================================================
overview_tab, sentiment_tab, performance_tab, comments_tab, quality_tab = (
    st.tabs([
        "Overview",
        "Sentiment",
        "Ad Performance",
        "Comments",
        "Data Quality",
    ])
)


# ============================================================
# OVERVIEW
# ============================================================
with overview_tab:

    st.subheader("Key findings")

    st.markdown(
        "<div class='section-note'>"
        "A summary of the comments included in the current selection."
        "</div>",
        unsafe_allow_html=True,
    )

    if known_n:
        balance = positive_pct - negative_pct

        if balance >= 0:
            balance_text = (
                f"Positive predictions exceed negative predictions "
                f"by {balance:.1f} percentage points."
            )
        else:
            balance_text = (
                f"Negative predictions exceed positive predictions "
                f"by {abs(balance):.1f} percentage points."
            )
    else:
        balance_text = (
            "No known sentiment predictions are available "
            "for this selection."
        )

    video_counts = (
        filtered.groupby("ad_label")
        .size()
        .sort_values(ascending=False)
    )

    top_ad = video_counts.index[0] if len(video_counts) else "N/A"
    top_ad_count = int(video_counts.iloc[0]) if len(video_counts) else 0

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">Sentiment balance</div>
            <div class="insight-body">{balance_text}
            These are model predictions, not verified measures
            of customer satisfaction.</div>
        </div>
        <div class="insight-card">
            <div class="insight-title">Most-commented advertisement</div>
            <div class="insight-body">{top_ad} has {top_ad_count:,}
            comments in the current selection.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    most_liked = filtered.loc[
        filtered["like_count"].idxmax()
    ]

    preview = str(most_liked["comment_text"])

    if len(preview) > 220:
        preview = preview[:217] + "..."

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">Most-liked comment</div>
            <div class="insight-body">
                {int(most_liked['like_count'])} likes ·
                {most_liked['ad_label']}<br>
                {preview}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    with left:
        sentiment_counts = (
            filtered["sentiment_label"]
            .value_counts()
            .reindex(SENTIMENT_ORDER, fill_value=0)
            .rename_axis("Sentiment")
            .reset_index(name="Comments")
        )

        sentiment_counts = sentiment_counts[
            sentiment_counts["Comments"] > 0
        ]

        fig = px.pie(
            sentiment_counts,
            names="Sentiment",
            values="Comments",
            hole=0.62,
            color="Sentiment",
            color_discrete_map=SENTIMENT_COLORS,
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
        )

        st.plotly_chart(
            style_fig(fig, "Sentiment distribution"),
            use_container_width=True,
        )

    with right:
        grouped = (
            filtered.groupby(["ad_label", "sentiment_label"])
            .size()
            .reset_index(name="Comments")
        )

        fig = px.bar(
            grouped,
            x="ad_label",
            y="Comments",
            color="sentiment_label",
            barmode="stack",
            category_orders={
                "sentiment_label": SENTIMENT_ORDER
            },
            color_discrete_map=SENTIMENT_COLORS,
            labels={
                "ad_label": "Advertisement",
                "sentiment_label": "Sentiment",
            },
        )

        fig.update_layout(
            xaxis_title="Advertisement",
            yaxis_title="Comments",
        )

        st.plotly_chart(
            style_fig(fig, "Comments by advertisement"),
            use_container_width=True,
        )

    st.caption(
        f"{known_n:,} comments have known sentiment labels; "
        f"{unknown_n:,} are unknown or unlabelled. "
        "Sentiment percentages exclude unknown labels."
    )


# ============================================================
# SENTIMENT ANALYSIS
# ============================================================
with sentiment_tab:

    st.subheader("Sentiment analysis")

    st.markdown(
        "<div class='section-note'>"
        "Compare predicted sentiment categories across advertisements."
        "</div>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Positive", f"{positive_n:,}", f"{positive_pct:.1f}%")
    c2.metric("Neutral", f"{neutral_n:,}", f"{neutral_pct:.1f}%")
    c3.metric("Negative", f"{negative_n:,}", f"{negative_pct:.1f}%")

    by_ad = (
        filtered.groupby(["ad_label", "sentiment_label"])
        .size()
        .reset_index(name="Comments")
    )

    fig = px.bar(
        by_ad,
        x="ad_label",
        y="Comments",
        color="sentiment_label",
        barmode="group",
        category_orders={
            "sentiment_label": SENTIMENT_ORDER
        },
        color_discrete_map=SENTIMENT_COLORS,
        labels={
            "ad_label": "Advertisement",
            "sentiment_label": "Sentiment",
        },
    )

    fig.update_layout(
        xaxis_title="Advertisement",
        yaxis_title="Comments",
    )

    st.plotly_chart(
        style_fig(fig, "Sentiment by advertisement", 420),
        use_container_width=True,
    )

    if "confidence" in filtered.columns:
        confidence = pd.to_numeric(
            filtered["confidence"],
            errors="coerce",
        )

        confidence_df = filtered.assign(
            _confidence=confidence
        ).dropna(subset=["_confidence"])

        if not confidence_df.empty:
            fig = px.histogram(
                confidence_df,
                x="_confidence",
                color="sentiment_label",
                nbins=20,
                color_discrete_map=SENTIMENT_COLORS,
                labels={
                    "_confidence": "Model confidence",
                    "sentiment_label": "Sentiment",
                },
            )

            st.plotly_chart(
                style_fig(fig, "Model confidence distribution"),
                use_container_width=True,
            )
    else:
        st.info(
            "A confidence-score column was not found. "
            "This chart can be shown if confidence scores are "
            "added to the dataset."
        )

    st.markdown("#### Comment examples")

    available_examples = [
        s for s in SENTIMENT_ORDER
        if s in filtered["sentiment_label"].unique()
    ]

    chosen_sentiment = st.selectbox(
        "Select sentiment",
        available_examples,
    )

    examples = filtered[
        filtered["sentiment_label"] == chosen_sentiment
    ].sort_values(
        ["like_count", "reply_count"],
        ascending=False,
    ).head(5)

    if examples.empty:
        st.info("No comments found for this sentiment.")
    else:
        for _, row in examples.iterrows():
            st.markdown(
                f"**{row['ad_label']} · "
                f"{int(row['like_count'])} likes · "
                f"{int(row['reply_count'])} replies**"
            )
            st.write(row["comment_text"])
            st.divider()


# ============================================================
# AD PERFORMANCE
# ============================================================
with performance_tab:

    st.subheader("Advertisement performance")

    st.markdown(
        "<div class='section-note'>"
        "Compare comment volume and engagement across advertisements."
        "</div>",
        unsafe_allow_html=True,
    )

    ad_summary = (
        filtered.groupby("ad_label", as_index=False)
        .agg(
            Comments=("comment_text", "size"),
            Total_likes=("like_count", "sum"),
            Average_likes=("like_count", "mean"),
            Total_replies=("reply_count", "sum"),
            Average_replies=("reply_count", "mean"),
        )
    )

    sentiment_table = filtered[
        filtered["sentiment_label"].isin(
            ["Positive", "Neutral", "Negative"]
        )
    ]

    sentiment_pivot = (
        sentiment_table.groupby(["ad_label", "sentiment_label"])
        .size()
        .unstack(fill_value=0)
    )

    for sentiment in ["Positive", "Neutral", "Negative"]:
        if sentiment not in sentiment_pivot.columns:
            sentiment_pivot[sentiment] = 0

    denominator = sentiment_pivot[
        ["Positive", "Neutral", "Negative"]
    ].sum(axis=1).replace(0, float("nan"))

    sentiment_pivot["Positive %"] = (
        sentiment_pivot["Positive"] / denominator * 100
    )

    sentiment_pivot["Negative %"] = (
        sentiment_pivot["Negative"] / denominator * 100
    )

    ad_summary = ad_summary.merge(
        sentiment_pivot[
            ["Positive %", "Negative %"]
        ].reset_index(),
        on="ad_label",
        how="left",
    )

    left, right = st.columns(2)

    with left:
        volume = ad_summary.sort_values(
            "Comments",
            ascending=False,
        )

        fig = px.bar(
            volume,
            x="ad_label",
            y="Comments",
            labels={
                "ad_label": "Advertisement",
                "Comments": "Comments",
            },
        )

        fig.update_traces(marker_color=accent)

        st.plotly_chart(
            style_fig(fig, "Comment volume"),
            use_container_width=True,
        )

    with right:
        fig = px.scatter(
            ad_summary,
            x="Comments",
            y="Total_likes",
            size="Total_replies",
            hover_name="ad_label",
            labels={
                "Comments": "Number of comments",
                "Total_likes": "Total likes",
                "Total_replies": "Total replies",
            },
        )

        fig.update_traces(
            marker_color=accent,
            marker_line_color=line,
            marker_line_width=1,
        )

        st.plotly_chart(
            style_fig(fig, "Comment volume and engagement"),
            use_container_width=True,
        )

    st.markdown("#### Advertisement summary")

    st.dataframe(
        ad_summary.sort_values(
            "Comments",
            ascending=False,
        ).round(2),
        use_container_width=True,
        hide_index=True,
    )

    left, right = st.columns(2)

    with left:
        fig = px.histogram(
            filtered,
            x="like_count",
            nbins=20,
            labels={"like_count": "Likes per comment"},
        )

        fig.update_traces(marker_color=accent)

        st.plotly_chart(
            style_fig(fig, "Likes per comment"),
            use_container_width=True,
        )

    with right:
        fig = px.histogram(
            filtered,
            x="reply_count",
            nbins=15,
            labels={"reply_count": "Replies per comment"},
        )

        fig.update_traces(marker_color=accent)

        st.plotly_chart(
            style_fig(fig, "Replies per comment"),
            use_container_width=True,
        )

    if filtered["comment_date"].notna().any():

        timeline = (
            filtered.dropna(subset=["comment_date"])
            .assign(
                Date=lambda x: x["comment_date"].dt.date
            )
            .groupby("Date")
            .size()
            .reset_index(name="Comments")
        )

        fig = px.line(
            timeline,
            x="Date",
            y="Comments",
            markers=True,
        )

        fig.update_traces(
            line_color=accent,
            marker_color=accent,
        )

        st.plotly_chart(
            style_fig(fig, "Comment activity over time"),
            use_container_width=True,
        )


# ============================================================
# COMMENT EXPLORER
# ============================================================
with comments_tab:

    st.subheader("Comment explorer")

    st.markdown(
        "<div class='section-note'>"
        "Search, inspect and export individual comments."
        "</div>",
        unsafe_allow_html=True,
    )

    search_text = st.text_input(
        "Search comments",
        placeholder="Enter a word or phrase...",
    )

    comments_view = filtered.copy()

    if search_text.strip():
        comments_view = comments_view[
            comments_view["comment_text"].str.contains(
                search_text.strip(),
                case=False,
                na=False,
                regex=False,
            )
        ]

    sort_choice = st.selectbox(
        "Sort by",
        [
            "Most likes",
            "Most replies",
            "Newest first",
            "Oldest first",
        ],
    )

    if sort_choice == "Most likes":
        comments_view = comments_view.sort_values(
            "like_count",
            ascending=False,
        )

    elif sort_choice == "Most replies":
        comments_view = comments_view.sort_values(
            "reply_count",
            ascending=False,
        )

    elif sort_choice == "Newest first":
        comments_view = comments_view.sort_values(
            "comment_date",
            ascending=False,
            na_position="last",
        )

    else:
        comments_view = comments_view.sort_values(
            "comment_date",
            ascending=True,
            na_position="last",
        )

    display_columns = [
        "ad_label",
        "comment_text",
        "sentiment_label",
        "aspect_label",
        "like_count",
        "reply_count",
        "comment_date",
        "video_id",
        "comment_id",
    ]

    display_columns = [
        col for col in display_columns
        if col in comments_view.columns
    ]

    table = comments_view[display_columns].rename(
        columns={
            "ad_label": "Advertisement",
            "comment_text": "Comment",
            "sentiment_label": "Predicted sentiment",
            "aspect_label": "Aspect",
            "like_count": "Likes",
            "reply_count": "Replies",
            "comment_date": "Comment date",
            "video_id": "Original video ID",
            "comment_id": "Comment ID",
        }
    )

    st.caption(
        f"{len(table):,} comments match the current filters and search."
    )

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        height=480,
    )

    st.download_button(
        "Download filtered comments (CSV)",
        data=comments_view.to_csv(index=False).encode("utf-8-sig"),
        file_name="sapphire_filtered_comments.csv",
        mime="text/csv",
    )

    with st.expander("About advertisement labels"):
        st.write(
            "Labels such as Ad 01 and Ad 02 make charts easier to read. "
            "They are assigned from the sorted video IDs and are not "
            "official Sapphire campaign names. Original video IDs are "
            "retained in this table for traceability."
        )


# ============================================================
# DATA QUALITY
# ============================================================
with quality_tab:

    st.subheader("Data quality and limitations")

    st.markdown(
        "<div class='section-note'>"
        "Dataset coverage, missing information and interpretation limits."
        "</div>",
        unsafe_allow_html=True,
    )

    duplicate_ids = None

    if df["comment_id"].ne("").any():
        duplicate_ids = int(
            df.loc[
                df["comment_id"].ne(""),
                "comment_id"
            ].duplicated().sum()
        )

    quality_checks = [
        {
            "Check": "Rows in source CSV",
            "Result": f"{len(raw_df):,}",
        },
        {
            "Check": "Usable comments",
            "Result": f"{len(df):,}",
        },
        {
            "Check": "Unique advertisements",
            "Result": f"{df['video_id'].nunique():,}",
        },
        {
            "Check": "Blank comment text after cleaning",
            "Result": f"{int(df['comment_text'].eq('').sum()):,}",
        },
        {
            "Check": "Unknown sentiment labels",
            "Result": f"{int((df['sentiment_label'] == 'Unknown').sum()):,}",
        },
        {
            "Check": "Missing comment dates",
            "Result": f"{int(df['comment_date'].isna().sum()):,}",
        },
        {
            "Check": "Duplicate comment IDs",
            "Result": (
                "Not assessed"
                if duplicate_ids is None
                else f"{duplicate_ids:,}"
            ),
        },
    ]

    st.dataframe(
        pd.DataFrame(quality_checks),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Interpretation notes")

    st.markdown(
        """
        - **Predicted sentiment is not ground truth.** Unless comments
          have been manually verified, treat sentiment categories as
          model predictions.

        - **Language affects accuracy.** Models can misinterpret Urdu,
          Roman Urdu, slang, sarcasm, cultural references and emojis.

        - **Engagement is not sentiment.** Likes and replies indicate
          interaction but do not necessarily indicate agreement.

        - **Dataset coverage is limited.** Findings describe the
          comments collected for this analysis, not every Sapphire
          customer or YouTube viewer.

        - **Advertisement labels are display names.** Ad 01, Ad 02
          and similar labels are not official campaign titles.
        """
    )

    if Path(SCALING_FILE).exists():

        with st.expander("Scaling experiment results"):

            scaling_df = pd.read_csv(SCALING_FILE)

            st.dataframe(
                scaling_df,
                use_container_width=True,
                hide_index=True,
            )

            numeric_columns = scaling_df.select_dtypes(
                include="number"
            ).columns.tolist()

            if numeric_columns and len(scaling_df.columns) >= 2:

                x_candidates = [
                    col for col in scaling_df.columns
                    if col not in numeric_columns
                ]

                if not x_candidates:
                    x_candidates = scaling_df.columns.tolist()

                x_column = st.selectbox(
                    "X-axis",
                    x_candidates,
                    key="scaling_x",
                )

                y_column = st.selectbox(
                    "Measure",
                    numeric_columns,
                    key="scaling_y",
                )

                fig = px.line(
                    scaling_df,
                    x=x_column,
                    y=y_column,
                    markers=True,
                )

                fig.update_traces(
                    line_color=accent,
                    marker_color=accent,
                )

                st.plotly_chart(
                    style_fig(
                        fig,
                        f"{y_column} by {x_column}",
                    ),
                    use_container_width=True,
                )

    else:
        st.caption(
            "Optional: add scaling_results.csv to the repository "
            "to display scaling experiment results."
        )


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")

st.caption(
    "Sapphire Pakistan | Ad Sentiment Analysis · "
    "Interpret model-predicted sentiment with care."
)
