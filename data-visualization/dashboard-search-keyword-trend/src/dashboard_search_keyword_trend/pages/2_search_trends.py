"""
Search Keyword Trend Intelligence Dashboard
-------------------------------------------
Surfaces keywords with high search velocity but low conversion —
the "opportunity gap" where demand is real but marketing hasn't captured it yet.
"""

from pathlib import Path
from random import randint

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard_search_keyword_trend.fixtures import SearchKeywordTrendMockGenerator
from dashboard_search_keyword_trend.style import DashboardColors as dh
from dashboard_search_keyword_trend.style import set_header

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Keyword Velocity Intelligence",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(
    f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: {dh.SLATE};
    color: {dh.WHITE};
  }}

  /* Remove Streamlit chrome padding */
  .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }}
  header[data-testid="stHeader"] {{ background: {dh.SLATE}; }}

  /* KPI cards */
  .kpi-grid {{ display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }}
  .kpi {{
    background: {dh.SLATE_2};
    border: 1px solid {dh.SLATE_3};
    border-radius: 4px;
    padding: 1rem 1.25rem;
    flex: 1;
    min-width: 140px;
  }}
  .kpi-label {{ font-size: 0.72rem; color: {dh.MUTED}; margin-bottom: 0.3rem; }}
  .kpi-value {{ font-size: 1.75rem; font-weight: 600; line-height: 1; }}
  .kpi-sub {{ font-size: 0.72rem; color: {dh.MUTED}; margin-top: 0.25rem; }}
  .kpi-amber .kpi-value {{ color: {dh.AMBER}; }}
  .kpi-teal  .kpi-value {{ color: {dh.TEAL}; }}
  .kpi-white .kpi-value {{ color: {dh.WHITE}; }}

  /* Form */
  .stForm {{
    background: {dh.SLATE_2};
    border: 1px solid {dh.SLATE_3};
    border-radius: 4px;
    padding: 1.25rem 1.5rem;
  }}
  .stForm label {{ font-size: 0.8rem; color: {dh.MUTED}; font-weight: 500; }}

  /* Section heading */
  .section-head {{
    font-size: 0.75rem;
    font-weight: 600;
    color: {dh.MUTED};
    letter-spacing: 0.06em;
    text-transform: uppercase;
    border-bottom: 1px solid {dh.SLATE_3};
    padding-bottom: 0.4rem;
    margin: 1.5rem 0 0.9rem;
  }}

  /* Quadrant label */
  .qlabel {{
    font-size: 0.7rem;
    font-family: 'IBM Plex Mono', monospace;
    color: {dh.MUTED};
  }}

  /* Alert pill */
  .alert-pill {{
    display: inline-block;
    background: rgba(245,158,11,0.12);
    border: 1px solid rgba(245,158,11,0.25);
    border-radius: 20px;
    padding: 0.15rem 0.65rem;
    font-size: 0.72rem;
    color: {dh.AMBER};
    font-weight: 500;
  }}

  /* Plotly charts: transparent bg */
  .js-plotly-plot .plotly .bg {{ fill: transparent !important; }}
</style>
""",
    unsafe_allow_html=True,
)

# ── Hero ──────────────────────────────────────────────────────────────────────
set_header(
    title="Keyword Velocity Intelligence",
    description=(
        "Surfaces keywords where search demand is accelerating faster than the baseline — "
        "but conversion hasn't followed. These are your live activation windows: "
        "the gap between what shoppers are hunting for and what your campaigns are capturing."
    ),
    background_image_path=Path(__file__).resolve().parent
    / "assets"
    / "search_keyword_trend_header.png",
)

# ── Parameter form ────────────────────────────────────────────────────────────
with st.form("search_trends_form"):
    st.markdown(
        "**Analytical thresholds**",
        help="Filters applied server-side against mart.search_keyword_trend",
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        trend_velocity_score = st.slider(
            "Min trend velocity score",
            min_value=0.0,
            max_value=5.0,
            value=2.0,
            step=0.1,
            help="Z-score-like deviation of current search count vs. baseline. Higher = more anomalous spike.",
        )
        lookback_hours = st.select_slider(
            "Lookback window (hours)",
            options=[6, 12, 24, 48, 72],
            value=24,
            help="How far back to scan for keyword windows.",
        )

    with col2:
        conversion_proxy_rate = st.slider(
            "Max conversion proxy rate",
            min_value=0.001,
            max_value=0.10,
            value=0.02,
            step=0.001,
            format="%.3f",
            help="Ratio of attributed orders to searches. Low value = demand not yet converted.",
        )
        keyword_filter = st.multiselect(
            "Filter keywords (optional)",
            options=[
                "sneakers",
                "blazer",
                "coat",
                "dress",
                "shorts",
                "skirt",
                "socks",
                "sweater",
                "boots",
                "hoodie",
            ],
            default=[],
            help="Leave empty to show all qualifying keywords.",
        )

    with col3:
        region_filter = st.multiselect(
            "Filter regions (optional)",
            options=[
                "Mazowieckie",
                "Wielkopolskie",
                "Małopolskie",
                "Pomorskie",
                "Dolnośląskie",
            ],
            default=[],
        )
        channel_filter = st.multiselect(
            "Filter channels (optional)",
            options=["paid", "organic", "social", "direct"],
            default=[],
        )

    submitted = st.form_submit_button(
        "🔍 Refresh signal data", width="stretch"
    )

# ── Data fetch ────────────────────────────────────────────────────────────────
if submitted or "search_trends_df" not in st.session_state:
    with st.spinner("Scanning keyword velocity windows..."):
        generator = SearchKeywordTrendMockGenerator(seed=randint(1, 50))
        st.session_state.search_trends_df = generator.generate_mock_search_trends(
            trend_velocity_score=trend_velocity_score,
            conversion_proxy_rate=conversion_proxy_rate,
            lookback_hours=lookback_hours,
        )
        # Store active params so we can display them
        st.session_state.active_params = dict(
            velocity=trend_velocity_score,
            conversion=conversion_proxy_rate,
            hours=lookback_hours,
        )

df: pd.DataFrame = st.session_state.search_trends_df.copy()

# ── Client-side filters (keyword / region / channel) ─────────────────────────
if keyword_filter:
    df = df[df["search_keyword"].isin(keyword_filter)]
if region_filter:
    df = df[df["primary_region"].isin(region_filter)]
if channel_filter:
    df = df[df["dominant_channel"].isin(channel_filter)]

# ── Empty state ───────────────────────────────────────────────────────────────
if df.empty:
    st.info(
        "No keyword windows meet the current thresholds. "
        "Try lowering the minimum velocity score or raising the max conversion rate, then refresh."
    )
    st.stop()

# ── KPI strip ─────────────────────────────────────────────────────────────────
total_keywords = df["search_keyword"].nunique()
total_windows = len(df)
avg_velocity = df["trend_velocity_score"].mean()
avg_conversion = df["conversion_proxy_rate"].mean()
top_keyword = df.loc[df["trend_velocity_score"].idxmax(), "search_keyword"]
total_searches = df["search_count"].sum()

st.markdown(
    f"""
<div class="kpi-grid">
  <div class="kpi kpi-amber">
    <div class="kpi-label">Unique keywords flagged</div>
    <div class="kpi-value">{total_keywords}</div>
    <div class="kpi-sub">in {total_windows} time windows</div>
  </div>
  <div class="kpi kpi-amber">
    <div class="kpi-label">Avg velocity score</div>
    <div class="kpi-value">{avg_velocity:.2f}</div>
    <div class="kpi-sub">threshold &gt; {st.session_state.active_params["velocity"]:.1f}</div>
  </div>
  <div class="kpi kpi-teal">
    <div class="kpi-label">Avg conversion rate</div>
    <div class="kpi-value">{avg_conversion:.3f}</div>
    <div class="kpi-sub">threshold &lt; {st.session_state.active_params["conversion"]:.3f}</div>
  </div>
  <div class="kpi kpi-white">
    <div class="kpi-label">Total searches in window</div>
    <div class="kpi-value">{total_searches:,}</div>
    <div class="kpi-sub">across {st.session_state.active_params["hours"]}h lookback</div>
  </div>
  <div class="kpi kpi-amber">
    <div class="kpi-label">Top velocity keyword</div>
    <div class="kpi-value" style="font-size:1.3rem">{top_keyword}</div>
    <div class="kpi-sub">highest spike right now</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ── Aggregate per keyword for charts ─────────────────────────────────────────
kw_agg = (
    df.groupby("search_keyword")
    .agg(
        avg_velocity=("trend_velocity_score", "mean"),
        avg_conversion=("conversion_proxy_rate", "mean"),
        total_searches=("search_count", "sum"),
        windows=("search_keyword", "count"),
        top_region=("primary_region", lambda x: x.mode()[0] if not x.empty else "—"),
    )
    .reset_index()
    .sort_values("avg_velocity", ascending=False)
)

# ── Row 1: Opportunity scatter + Velocity bar ─────────────────────────────────
st.markdown('<div class="section-head">Opportunity map</div>', unsafe_allow_html=True)

scatter_col, bar_col = st.columns([3, 2], gap="medium")

with scatter_col:
    # Quadrant: high velocity / low conversion = top-left = opportunity
    fig_scatter = px.scatter(
        kw_agg,
        x="avg_conversion",
        y="avg_velocity",
        size="total_searches",
        color="avg_velocity",
        text="search_keyword",
        color_continuous_scale=[[0, dh.TEAL], [0.5, dh.AMBER], [1, "#EF4444"]],
        size_max=52,
        labels={
            "avg_conversion": "Avg conversion rate  →  higher means already converting",
            "avg_velocity": "Avg trend velocity score  →  higher means bigger spike",
            "total_searches": "Total searches",
        },
        title="Velocity vs. Conversion — keyword opportunity quadrant",
    )

    # Quadrant reference lines
    fig_scatter.add_hline(
        y=trend_velocity_score,
        line_dash="dot",
        line_color=dh.AMBER,
        line_width=1,
        annotation_text="velocity threshold",
        annotation_font_color=dh.AMBER,
        annotation_font_size=10,
    )
    fig_scatter.add_vline(
        x=conversion_proxy_rate,
        line_dash="dot",
        line_color=dh.TEAL,
        line_width=1,
        annotation_text="conversion ceiling",
        annotation_font_color=dh.TEAL,
        annotation_font_size=10,
    )

    fig_scatter.update_traces(
        textposition="top center",
        textfont=dict(family="IBM Plex Sans", size=10, color=dh.WHITE),
        marker=dict(line=dict(width=1, color=dh.SLATE)),
    )
    fig_scatter.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=dh.SLATE_2,
        font=dict(family="IBM Plex Sans", color=dh.MUTED, size=11),
        title_font=dict(color=dh.WHITE, size=13, family="IBM Plex Sans"),
        coloraxis_showscale=False,
        xaxis=dict(
            gridcolor=dh.SLATE_3, zerolinecolor=dh.SLATE_3, title_font=dict(size=10)
        ),
        yaxis=dict(
            gridcolor=dh.SLATE_3, zerolinecolor=dh.SLATE_3, title_font=dict(size=10)
        ),
        margin=dict(l=10, r=10, t=45, b=10),
        height=360,
    )
    st.plotly_chart(fig_scatter, width="stretch")

with bar_col:
    fig_bar = px.bar(
        kw_agg.sort_values("avg_velocity"),
        x="avg_velocity",
        y="search_keyword",
        orientation="h",
        color="avg_velocity",
        color_continuous_scale=[[0, dh.SLATE_3], [0.5, dh.AMBER], [1, "#EF4444"]],
        labels={"avg_velocity": "Avg velocity score", "search_keyword": ""},
        title="Velocity ranking",
        text=kw_agg.sort_values("avg_velocity")["avg_velocity"].apply(
            lambda v: f"{v:.2f}"
        ),
    )
    fig_bar.update_traces(
        textposition="outside",
        textfont=dict(color=dh.WHITE, size=10, family="IBM Plex Mono"),
    )
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=dh.SLATE_2,
        font=dict(family="IBM Plex Sans", color=dh.MUTED, size=11),
        title_font=dict(color=dh.WHITE, size=13, family="IBM Plex Sans"),
        coloraxis_showscale=False,
        xaxis=dict(gridcolor=dh.SLATE_3, zerolinecolor=dh.SLATE_3),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=40, t=45, b=10),
        height=360,
    )
    st.plotly_chart(fig_bar, width="stretch")

# ── Row 2: Time series + Channel breakdown ─────────────────────────────────────
st.markdown(
    '<div class="section-head">Temporal & channel signal</div>', unsafe_allow_html=True
)

ts_col, ch_col = st.columns([3, 2], gap="medium")

with ts_col:
    df_ts = df.copy()
    df_ts["window_start_dt"] = pd.to_datetime(df_ts["window_start"])
    df_ts_pivot = (
        df_ts.groupby(["window_start_dt", "search_keyword"])["trend_velocity_score"]
        .mean()
        .reset_index()
    )

    fig_ts = px.line(
        df_ts_pivot,
        x="window_start_dt",
        y="trend_velocity_score",
        color="search_keyword",
        markers=True,
        labels={
            "window_start_dt": "Window start",
            "trend_velocity_score": "Velocity score",
            "search_keyword": "Keyword",
        },
        title="Velocity score over time — per keyword",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_ts.add_hline(
        y=trend_velocity_score,
        line_dash="dot",
        line_color=dh.AMBER,
        line_width=1,
    )
    fig_ts.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=dh.SLATE_2,
        font=dict(family="IBM Plex Sans", color=dh.MUTED, size=11),
        title_font=dict(color=dh.WHITE, size=13, family="IBM Plex Sans"),
        xaxis=dict(gridcolor=dh.SLATE_3, zerolinecolor=dh.SLATE_3),
        yaxis=dict(gridcolor=dh.SLATE_3, zerolinecolor=dh.SLATE_3),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=dh.MUTED, size=10),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        margin=dict(l=10, r=10, t=50, b=10),
        height=320,
    )
    st.plotly_chart(fig_ts, width="stretch")

with ch_col:
    ch_agg = (
        df.groupby("dominant_channel")
        .agg(
            total_searches=("search_count", "sum"),
            keywords=("search_keyword", "nunique"),
        )
        .reset_index()
    )
    COLOR_MAP = {
        "paid": dh.AMBER,
        "organic": dh.TEAL,
        "social": "#818CF8",
        "direct": "#FB923C",
    }
    fig_ch = px.bar(
        ch_agg,
        x="dominant_channel",
        y="total_searches",
        color="dominant_channel",
        color_discrete_map=COLOR_MAP,
        labels={"dominant_channel": "", "total_searches": "Search volume"},
        title="Search volume by dominant channel",
        text="total_searches",
    )
    fig_ch.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
        textfont=dict(color=dh.WHITE, size=10),
        marker_line_width=0,
    )
    fig_ch.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=dh.SLATE_2,
        font=dict(family="IBM Plex Sans", color=dh.MUTED, size=11),
        title_font=dict(color=dh.WHITE, size=13, family="IBM Plex Sans"),
        showlegend=False,
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(gridcolor=dh.SLATE_3, zerolinecolor=dh.SLATE_3),
        margin=dict(l=10, r=10, t=45, b=10),
        height=320,
    )
    st.plotly_chart(fig_ch, width="stretch")

# ── Row 3: Regional heatmap + Device split ────────────────────────────────────
st.markdown(
    '<div class="section-head">Regional & device distribution</div>',
    unsafe_allow_html=True,
)

reg_col, dev_col = st.columns([3, 2], gap="medium")

with reg_col:
    region_kw = (
        df.groupby(["primary_region", "search_keyword"])["search_count"]
        .sum()
        .reset_index()
    )
    pivot = region_kw.pivot(
        index="primary_region", columns="search_keyword", values="search_count"
    ).fillna(0)

    fig_heat = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[[0, dh.SLATE_2], [0.4, dh.TEAL], [1, dh.AMBER]],
            showscale=True,
            hovertemplate="Region: %{y}<br>Keyword: %{x}<br>Searches: %{z:,}<extra></extra>",
        )
    )
    fig_heat.update_layout(
        title="Search volume — region × keyword",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=dh.SLATE_2,
        font=dict(family="IBM Plex Sans", color=dh.MUTED, size=11),
        title_font=dict(color=dh.WHITE, size=13),
        xaxis=dict(tickfont=dict(size=10, color=dh.MUTED), side="bottom"),
        yaxis=dict(tickfont=dict(size=10, color=dh.MUTED)),
        margin=dict(l=10, r=10, t=45, b=10),
        height=280,
    )
    st.plotly_chart(fig_heat, width="stretch")

with dev_col:
    dev_agg = df.groupby("dominant_device")["search_count"].sum().reset_index()
    fig_dev = px.pie(
        dev_agg,
        names="dominant_device",
        values="search_count",
        hole=0.55,
        color="dominant_device",
        color_discrete_map={
            "mobile": dh.AMBER,
            "desktop": dh.TEAL,
            "tablet": "#818CF8",
        },
        title="Search volume by device",
    )
    fig_dev.update_traces(
        textfont=dict(family="IBM Plex Sans", color=dh.WHITE, size=11),
        marker=dict(line=dict(color=dh.SLATE, width=2)),
    )
    fig_dev.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans", color=dh.MUTED, size=11),
        title_font=dict(color=dh.WHITE, size=13),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=dh.MUTED, size=10),
        ),
        margin=dict(l=10, r=10, t=45, b=10),
        height=280,
    )
    st.plotly_chart(fig_dev, width="stretch")

# ── Raw data table ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-head">Raw signal rows</div>', unsafe_allow_html=True)

with st.expander("Show filtered data table", expanded=False):
    display_df = df[
        [
            "window_start",
            "search_keyword",
            "primary_region",
            "dominant_channel",
            "dominant_device",
            "search_count",
            "trend_velocity_score",
            "conversion_proxy_rate",
            "attributed_revenue",
        ]
    ].copy()
    display_df["trend_velocity_score"] = display_df["trend_velocity_score"].round(3)
    display_df["conversion_proxy_rate"] = display_df["conversion_proxy_rate"].apply(
        lambda x: f"{x:.4f}"
    )
    display_df["attributed_revenue"] = display_df["attributed_revenue"].apply(
        lambda x: f"€{x:,.2f}"
    )
    display_df.columns = [
        "Window start",
        "Keyword",
        "Region",
        "Channel",
        "Device",
        "Searches",
        "Velocity score",
        "Conversion rate",
        "Attributed rev.",
    ]
    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        column_config={
            "Velocity score": st.column_config.ProgressColumn(
                min_value=0,
                max_value=float(display_df["Velocity score"].max()),
                format="%.3f",
            )
        },
    )

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Export CSV",
        data=csv,
        file_name="keyword_velocity_signals.csv",
        mime="text/csv",
        use_container_width=False,
    )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
<div style="margin-top:2rem; padding-top:1rem; border-top:1px solid {dh.SLATE_3};
     font-size:0.72rem; color:{dh.MUTED}; display:flex; justify-content:space-between;">
  <span>Source: <code style="color:{dh.TEAL}">mart.search_keyword_trend</code></span>
  <span>Velocity &gt; {trend_velocity_score:.1f} · Conversion &lt; {conversion_proxy_rate:.3f} · {lookback_hours}h window</span>
</div>
""",
    unsafe_allow_html=True,
)
