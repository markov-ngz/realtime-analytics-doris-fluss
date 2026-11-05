"""
Post-Purchase Intent Analytics
--------------------------------
Identifies keywords with high post-order search activity relative to
initial conversion — revealing demand gaps for bundles, accessories,
and recommendation improvements.
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
    page_title="Post-Purchase Intent Analytics",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS (mirrors keyword velocity dashboard) ───────────────────────────
st.markdown(
    f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: {dh.SLATE};
    color: {dh.WHITE};
  }}

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
  .kpi-sub   {{ font-size: 0.72rem; color: {dh.MUTED}; margin-top: 0.25rem; }}
  .kpi-amber .kpi-value {{ color: {dh.AMBER}; }}
  .kpi-teal  .kpi-value {{ color: {dh.TEAL};  }}
  .kpi-violet .kpi-value {{ color: {dh.VIOLET}; }}
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

  /* Revenue gap callout */
  .gap-callout {{
    background: rgba(245,158,11,0.07);
    border: 1px solid rgba(245,158,11,0.22);
    border-radius: 4px;
    padding: 0.8rem 1.1rem;
    font-size: 0.82rem;
    color: {dh.WHITE};
    margin-bottom: 1rem;
    line-height: 1.55;
  }}
  .gap-callout strong {{ color: {dh.AMBER}; }}

  /* Plotly transparent bg */
  .js-plotly-plot .plotly .bg {{ fill: transparent !important; }}
</style>
""",
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────
set_header(
    title="Post-Purchase Intent Analytics",
    description=(
        "Identify keywords with high post-order search velocity relative to initial conversion — "
        "revealing demand gaps for product bundles, accessories, and recommendation improvements."
    ),
    background_image_path=Path(__file__).resolve().parent
    / "assets"
    / "post_purchase_intent_analytics_headers.png",
)

# ── Parameter form ────────────────────────────────────────────────────────────
with st.form("post_search_parameters_form"):
    st.markdown(
        "**Funnel threshold parameters**",
        help="Filters applied against mart.search_keyword_trend to surface post-purchase curiosity signals",
    )

    col1, col2 = st.columns(2)

    with col1:
        min_post_searches = st.slider(
            "Min post-order search count",
            min_value=100,
            max_value=2000,
            value=1000,
            step=50,
            help="Minimum number of searches occurring after an order — low bar finds more keywords, high bar focuses on the loudest signals.",
        )
        max_conv_rate = st.slider(
            "Max initial conversion rate",
            min_value=0.0,
            max_value=0.05,
            value=0.01,
            step=0.001,
            format="%.3f",
            help="Filters out keywords that already convert well — keep only those where first-touch demand wasn't captured.",
        )

    with col2:
        min_ratio = st.slider(
            "Min post-to-pre search ratio",
            min_value=1.0,
            max_value=8.0,
            value=2.0,
            step=0.1,
            help="How many times more people search after ordering vs. before. High ratio = strong post-purchase curiosity.",
        )
        lookback_days = st.slider(
            "Lookback window (days)",
            min_value=1,
            max_value=30,
            value=7,
            help="How many days of hopping windows to include.",
        )

    submitted = st.form_submit_button(
        "🔍 Search / Refresh Data", width="stretch"
    )

# ── Data fetch ────────────────────────────────────────────────────────────────
if submitted or "post_search_df" not in st.session_state:
    with st.spinner("Scanning post-purchase curiosity signals..."):
        # st.session_state.post_search_df = st.session_state.keyword_service.fetch_post_to_pre_search_ratio(
        #     min_post_order_search_count=min_post_searches,
        #     max_conversion_proxy_rate=max_conv_rate,
        #     min_post_to_pre_ratio=min_ratio,
        #     lookback_days=lookback_days,
        # )
        generator = SearchKeywordTrendMockGenerator(seed=randint(1, 10))
        st.session_state.post_search_df = generator.generate_funnel_analysis_mock(
            hours_back=lookback_days * 24,
            min_post_searches=min_post_searches,
            max_conversion_rate=max_conv_rate,
            min_ratio=min_ratio,
        )
        st.session_state.post_search_params = dict(
            min_post=min_post_searches,
            max_conv=max_conv_rate,
            min_ratio=min_ratio,
            days=lookback_days,
        )

df: pd.DataFrame = st.session_state.post_search_df.copy()

st.divider()

# ── Empty state ───────────────────────────────────────────────────────────────
if df.empty:
    st.info(
        "No keywords meet the current funnel thresholds. "
        "Try lowering **Min post-order search count**, raising **Max initial conversion rate**, "
        "or reducing the **Min post-to-pre ratio**, then refresh."
    )
    st.stop()

# ── Derived fields ────────────────────────────────────────────────────────────
df["window_start_dt"] = pd.to_datetime(df["window_start"])
df["revenue_gap"] = (df["post_order_revenue"] - df["attributed_revenue"]).clip(lower=0)

# ── KPI strip ─────────────────────────────────────────────────────────────────
total_keywords = df["search_keyword"].nunique()
total_windows = len(df)
total_post_vol = df["post_order_search_count"].sum()
avg_ratio = df["post_to_pre_search_ratio"].mean()
total_rev_gap = df["revenue_gap"].sum()
top_keyword = df.loc[df["post_to_pre_search_ratio"].idxmax(), "search_keyword"]

st.markdown(
    f"""
<div class="kpi-grid">
  <div class="kpi kpi-amber">
    <div class="kpi-label">Flagged keywords</div>
    <div class="kpi-value">{total_keywords}</div>
    <div class="kpi-sub">across {total_windows} time windows</div>
  </div>
  <div class="kpi kpi-teal">
    <div class="kpi-label">Total post-order searches</div>
    <div class="kpi-value">{total_post_vol:,}</div>
    <div class="kpi-sub">demand after the sale</div>
  </div>
  <div class="kpi kpi-amber">
    <div class="kpi-label">Avg post-to-pre ratio</div>
    <div class="kpi-value">{avg_ratio:.1f}×</div>
    <div class="kpi-sub">threshold ≥ {st.session_state.post_search_params["min_ratio"]:.1f}×</div>
  </div>
  <div class="kpi kpi-violet">
    <div class="kpi-label">Est. revenue gap</div>
    <div class="kpi-value">€{total_rev_gap:,.0f}</div>
    <div class="kpi-sub">post − attributed revenue</div>
  </div>
  <div class="kpi kpi-white">
    <div class="kpi-label">Top curiosity keyword</div>
    <div class="kpi-value" style="font-size:1.3rem">{top_keyword}</div>
    <div class="kpi-sub">highest post-to-pre ratio</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ── Revenue gap callout ───────────────────────────────────────────────────────
p = st.session_state.post_search_params
st.markdown(
    f"""
<div class="gap-callout">
  <strong>{total_keywords} keywords</strong> show post-purchase curiosity
  with a post-to-pre ratio above <strong>{p["min_ratio"]:.1f}×</strong>
  and initial conversion below <strong>{p["max_conv"]:.1%}</strong> —
  indicating shoppers who bought once are searching again but not finding what they need.
  Estimated uncaptured revenue across this window: <strong>€{total_rev_gap:,.0f}</strong>.
  These are prime candidates for bundle recommendations, upsell email triggers, and paid retargeting.
</div>
""",
    unsafe_allow_html=True,
)

# ── Aggregate per keyword ─────────────────────────────────────────────────────
kw_agg = (
    df.groupby("search_keyword")
    .agg(
        avg_ratio=("post_to_pre_search_ratio", "mean"),
        total_post_vol=("post_order_search_count", "sum"),
        total_pre_vol=("pre_order_search_count", "sum"),
        total_rev_gap=("revenue_gap", "sum"),
        windows=("search_keyword", "count"),
        top_channel=("dominant_channel", lambda x: x.mode()[0] if not x.empty else "—"),
    )
    .reset_index()
    .sort_values("avg_ratio", ascending=False)
)

# ── Row 1: Ratio bubble chart + Revenue gap bar ───────────────────────────────
st.markdown(
    '<div class="section-head">Curiosity signal strength</div>', unsafe_allow_html=True
)

ratio_col, rev_col = st.columns([3, 2], gap="medium")

with ratio_col:
    fig_bubble = px.scatter(
        kw_agg,
        x="total_pre_vol",
        y="total_post_vol",
        size="avg_ratio",
        color="avg_ratio",
        text="search_keyword",
        color_continuous_scale=[[0, dh.TEAL], [0.5, dh.AMBER], [1, "#EF4444"]],
        size_max=55,
        labels={
            "total_pre_vol": "Pre-order searches  →  initial demand",
            "total_post_vol": "Post-order searches  →  curiosity after purchase",
            "avg_ratio": "Avg post-to-pre ratio",
        },
        title="Pre vs. Post-order search volume — bubble size = ratio",
    )
    # Diagonal parity line: equal pre/post volume
    max_val = max(kw_agg["total_pre_vol"].max(), kw_agg["total_post_vol"].max()) * 1.1
    fig_bubble.add_trace(
        go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode="lines",
            line=dict(color=dh.SLATE_3, dash="dot", width=1),
            name="parity",
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig_bubble.update_traces(
        textposition="top center",
        textfont=dict(family="IBM Plex Sans", size=10, color=dh.WHITE),
        marker=dict(line=dict(width=1, color=dh.SLATE)),
        selector=dict(mode="markers+text"),
    )
    fig_bubble.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=dh.SLATE_2,
        font=dict(family="IBM Plex Sans", color=dh.MUTED, size=11),
        title_font=dict(color=dh.WHITE, size=13),
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
    st.plotly_chart(fig_bubble, width="stretch")
    st.caption(
        "Keywords above the dotted parity line generate more post-purchase searches than pre-purchase — "
        "demand is growing *after* the sale."
    )

with rev_col:
    fig_rev = px.bar(
        kw_agg.sort_values("total_rev_gap"),
        x="total_rev_gap",
        y="search_keyword",
        orientation="h",
        color="total_rev_gap",
        color_continuous_scale=[[0, dh.SLATE_3], [0.4, dh.VIOLET], [1, dh.AMBER]],
        labels={"total_rev_gap": "Est. revenue gap (€)", "search_keyword": ""},
        title="Revenue gap by keyword",
        text=kw_agg.sort_values("total_rev_gap")["total_rev_gap"].apply(
            lambda v: f"€{v:,.0f}"
        ),
    )
    fig_rev.update_traces(
        textposition="outside",
        textfont=dict(color=dh.WHITE, size=10, family="IBM Plex Mono"),
    )
    fig_rev.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=dh.SLATE_2,
        font=dict(family="IBM Plex Sans", color=dh.MUTED, size=11),
        title_font=dict(color=dh.WHITE, size=13),
        coloraxis_showscale=False,
        xaxis=dict(gridcolor=dh.SLATE_3, zerolinecolor=dh.SLATE_3),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=55, t=45, b=10),
        height=360,
    )
    st.plotly_chart(fig_rev, width="stretch")

# ── Row 2: Time trend + Channel split ─────────────────────────────────────────
st.markdown(
    '<div class="section-head">Temporal & channel breakdown</div>',
    unsafe_allow_html=True,
)

ts_col, ch_col = st.columns([3, 2], gap="medium")

with ts_col:
    ts_agg = (
        df.groupby(["window_start_dt", "search_keyword"])
        .agg(
            post_vol=("post_order_search_count", "sum"),
            ratio=("post_to_pre_search_ratio", "mean"),
        )
        .reset_index()
    )
    fig_ts = px.line(
        ts_agg,
        x="window_start_dt",
        y="ratio",
        color="search_keyword",
        markers=True,
        labels={
            "window_start_dt": "Window start",
            "ratio": "Post-to-pre ratio",
            "search_keyword": "Keyword",
        },
        title="Post-to-pre ratio over time",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_ts.add_hline(
        y=p["min_ratio"],
        line_dash="dot",
        line_color=dh.AMBER,
        line_width=1,
        annotation_text="min ratio threshold",
        annotation_font_color=dh.AMBER,
        annotation_font_size=10,
    )
    fig_ts.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=dh.SLATE_2,
        font=dict(family="IBM Plex Sans", color=dh.MUTED, size=11),
        title_font=dict(color=dh.WHITE, size=13),
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
        height=300,
    )
    st.plotly_chart(fig_ts, width="stretch")

with ch_col:
    ch_agg = (
        df.groupby("dominant_channel")
        .agg(
            post_vol=("post_order_search_count", "sum"),
            keywords=("search_keyword", "nunique"),
        )
        .reset_index()
    )
    COLOR_MAP = {
        "paid": dh.AMBER,
        "organic": dh.TEAL,
        "social": dh.VIOLET,
        "direct": dh.ORANGE,
    }
    fig_ch = px.bar(
        ch_agg,
        x="dominant_channel",
        y="post_vol",
        color="dominant_channel",
        color_discrete_map=COLOR_MAP,
        labels={"dominant_channel": "", "post_vol": "Post-order search vol."},
        title="Post-order search volume by channel",
        text="post_vol",
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
        title_font=dict(color=dh.WHITE, size=13),
        showlegend=False,
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(gridcolor=dh.SLATE_3, zerolinecolor=dh.SLATE_3),
        margin=dict(l=10, r=10, t=45, b=10),
        height=300,
    )
    st.plotly_chart(fig_ch, width="stretch")

# ── Row 3: Top 10 ratio ranking (window selector) ─────────────────────────────
st.markdown(
    '<div class="section-head">Window-level ranking</div>', unsafe_allow_html=True
)

available_windows = sorted(df["window_start"].unique(), reverse=True)
selected_window = st.selectbox(
    "Inspect hopping window:",
    available_windows,
    index=0,
    help="Drill into a specific 1-hour window to see which keywords ranked highest in that period.",
)
df_window = df[df["window_start"] == selected_window]

top10 = df_window.sort_values("post_to_pre_search_ratio", ascending=False).head(10)

if top10.empty:
    st.warning("No records for this window with the current thresholds.")
else:
    rank_col, detail_col = st.columns([3, 2], gap="medium")

    with rank_col:
        fig_rank = px.bar(
            top10.sort_values("post_to_pre_search_ratio"),
            x="post_to_pre_search_ratio",
            y="search_keyword",
            orientation="h",
            color="post_order_search_count",
            color_continuous_scale=[[0, dh.TEAL], [1, dh.AMBER]],
            labels={
                "post_to_pre_search_ratio": "Post-to-pre search ratio",
                "search_keyword": "",
                "post_order_search_count": "Post-order volume",
            },
            title=f"Top keywords — window {selected_window[:16]}",
            text=top10.sort_values("post_to_pre_search_ratio")[
                "post_to_pre_search_ratio"
            ].apply(lambda v: f"{v:.1f}×"),
        )
        fig_rank.update_traces(
            textposition="outside",
            textfont=dict(color=dh.WHITE, size=11, family="IBM Plex Mono"),
        )
        fig_rank.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=dh.SLATE_2,
            font=dict(family="IBM Plex Sans", color=dh.MUTED, size=11),
            title_font=dict(color=dh.WHITE, size=13),
            coloraxis_showscale=False,
            xaxis=dict(gridcolor=dh.SLATE_3, zerolinecolor=dh.SLATE_3),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            margin=dict(l=10, r=50, t=45, b=10),
            height=340,
        )
        st.plotly_chart(fig_rank, width="stretch")

    with detail_col:
        # Mini revenue waterfall: attributed vs post-order per keyword
        waterfall_df = top10.head(6)[
            ["search_keyword", "attributed_revenue", "post_order_revenue"]
        ].copy()
        waterfall_df = waterfall_df.sort_values("post_order_revenue", ascending=True)

        fig_wf = go.Figure()
        fig_wf.add_trace(
            go.Bar(
                name="Attributed revenue",
                y=waterfall_df["search_keyword"],
                x=waterfall_df["attributed_revenue"],
                orientation="h",
                marker_color=dh.TEAL,
                text=waterfall_df["attributed_revenue"].apply(lambda v: f"€{v:,.0f}"),
                textposition="inside",
                textfont=dict(size=9, color=dh.SLATE, family="IBM Plex Mono"),
            )
        )
        fig_wf.add_trace(
            go.Bar(
                name="Post-order revenue",
                y=waterfall_df["search_keyword"],
                x=waterfall_df["post_order_revenue"],
                orientation="h",
                marker_color=dh.AMBER,
                text=waterfall_df["post_order_revenue"].apply(lambda v: f"€{v:,.0f}"),
                textposition="inside",
                textfont=dict(size=9, color=dh.SLATE, family="IBM Plex Mono"),
            )
        )
        fig_wf.update_layout(
            barmode="group",
            title="Attributed vs post-order revenue",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=dh.SLATE_2,
            font=dict(family="IBM Plex Sans", color=dh.MUTED, size=11),
            title_font=dict(color=dh.WHITE, size=13),
            legend=dict(
                bgcolor="rgba(0,0,0,0)",
                font=dict(color=dh.MUTED, size=10),
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
            ),
            xaxis=dict(gridcolor=dh.SLATE_3, zerolinecolor=dh.SLATE_3),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            margin=dict(l=10, r=10, t=50, b=10),
            height=340,
        )
        st.plotly_chart(fig_wf, width="stretch")

# ── Raw data table ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-head">Detailed dataset</div>', unsafe_allow_html=True)

with st.expander("Show full filtered dataset", expanded=False):
    display_df = df[
        [
            "window_start",
            "search_keyword",
            "primary_region",
            "dominant_channel",
            "search_count",
            "pre_order_search_count",
            "post_order_search_count",
            "post_to_pre_search_ratio",
            "attributed_revenue",
            "post_order_revenue",
        ]
    ].copy()
    display_df["post_to_pre_search_ratio"] = display_df[
        "post_to_pre_search_ratio"
    ].round(2)
    display_df["attributed_revenue"] = display_df["attributed_revenue"].apply(
        lambda v: f"€{v:,.2f}"
    )
    display_df["post_order_revenue"] = display_df["post_order_revenue"].apply(
        lambda v: f"€{v:,.2f}"
    )
    display_df.columns = [
        "Window",
        "Keyword",
        "Region",
        "Channel",
        "Total searches",
        "Pre-order searches",
        "Post-order searches",
        "Post/pre ratio",
        "Attributed rev.",
        "Post-order rev.",
    ]
    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        column_config={
            "Post/pre ratio": st.column_config.ProgressColumn(
                min_value=0,
                max_value=float(display_df["Post/pre ratio"].max()),
                format="%.2f×",
            )
        },
    )

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Export CSV",
        data=csv,
        file_name="post_purchase_intent_signals.csv",
        mime="text/csv",
    )

# ── Footer ─────────────────────────────────────────────────────────────────────
params = st.session_state.post_search_params
st.markdown(
    f"""
<div style="margin-top:2rem; padding-top:1rem; border-top:1px solid {dh.SLATE_3};
     font-size:0.72rem; color:{dh.MUTED}; display:flex; justify-content:space-between;">
  <span>Source: <code style="color:{dh.TEAL}">mart.search_keyword_trend</code></span>
  <span>Post searches &gt; {params["min_post"]:,} · Conv &lt; {params["max_conv"]:.3f} · Ratio &gt; {params["min_ratio"]:.1f}× · {params["days"]}d window</span>
</div>
""",
    unsafe_allow_html=True,
)
