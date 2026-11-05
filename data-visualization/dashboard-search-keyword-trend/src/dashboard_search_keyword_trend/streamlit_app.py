"""
Search Keyword Trends & Operational Intelligence Hub
-----------------------------------------------------
Landing page with card-based navigation to sub-dashboards.
"""

from pathlib import Path

import streamlit as st

from dashboard_search_keyword_trend.style import DashboardColors as dh
from dashboard_search_keyword_trend.style import set_header

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Search Keyword Trends Hub",
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

  .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }}
  header[data-testid="stHeader"] {{ background: {dh.SLATE}; }}

  /* ── Nav cards ────────────────────────────────────────────────────────── */
  .nav-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.25rem;
    margin: 1.5rem 0 2rem;
  }}

  .nav-card {{
    background: {dh.SLATE_2};
    border: 1px solid {dh.SLATE_3};
    border-radius: 8px;
    padding: 1.5rem 1.75rem 1.4rem;
    text-decoration: none;
    display: block;
    transition: border-color 0.15s ease, background 0.15s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
  }}
  .nav-card:hover {{
    border-color: {dh.AMBER};
    background: #1a2a3a;
    text-decoration: none;
  }}
  .nav-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, {dh.AMBER}, {dh.TEAL});
    opacity: 0;
    transition: opacity 0.15s ease;
  }}
  .nav-card:hover::before {{ opacity: 1; }}

  .nav-card-icon {{
    font-size: 1.75rem;
    margin-bottom: 0.65rem;
    display: block;
  }}
  .nav-card-title {{
    font-size: 1rem;
    font-weight: 600;
    color: {dh.WHITE};
    margin: 0 0 0.4rem;
    letter-spacing: -0.01em;
  }}
  .nav-card-desc {{
    font-size: 0.8rem;
    color: {dh.MUTED};
    line-height: 1.5;
    margin: 0 0 1rem;
  }}
  .nav-card-meta {{
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }}
  .nav-tag {{
    font-size: 0.65rem;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 500;
    letter-spacing: 0.04em;
    padding: 0.15rem 0.5rem;
    border-radius: 3px;
  }}
  .nav-tag-amber {{
    background: rgba(245,158,11,0.12);
    color: {dh.AMBER};
    border: 1px solid rgba(245,158,11,0.3);
  }}
  .nav-tag-teal {{
    background: rgba(20,184,166,0.12);
    color: {dh.TEAL};
    border: 1px solid rgba(20,184,166,0.3);
  }}
  .nav-tag-violet {{
    background: rgba(129,140,248,0.12);
    color: #818CF8;
    border: 1px solid rgba(129,140,248,0.3);
  }}
  .nav-card-arrow {{
    position: absolute;
    bottom: 1.2rem;
    right: 1.4rem;
    font-size: 0.85rem;
    color: {dh.MUTED};
    font-family: 'IBM Plex Mono', monospace;
    opacity: 0;
    transition: opacity 0.15s ease;
  }}
  .nav-card:hover .nav-card-arrow {{ opacity: 1; color: {dh.AMBER}; }}

  /* ── Docs section ─────────────────────────────────────────────────────── */
  .docs-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-top: 0.5rem;
  }}
  .docs-block {{
    background: {dh.SLATE_2};
    border: 1px solid {dh.SLATE_3};
    border-radius: 4px;
    padding: 1.1rem 1.25rem;
  }}
  .docs-block h4 {{
    font-size: 0.8rem;
    font-weight: 600;
    color: {dh.WHITE};
    margin: 0 0 0.6rem;
    letter-spacing: 0.02em;
  }}
  .docs-block p, .docs-block li {{
    font-size: 0.78rem;
    color: {dh.MUTED};
    line-height: 1.6;
    margin: 0.2rem 0;
  }}
  .docs-block code {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: {dh.TEAL};
    background: rgba(20,184,166,0.1);
    border-radius: 2px;
    padding: 0.05rem 0.3rem;
  }}

  /* ── Section heading ──────────────────────────────────────────────────── */
  .section-head {{
    font-size: 0.75rem;
    font-weight: 600;
    color: {dh.MUTED};
    letter-spacing: 0.06em;
    text-transform: uppercase;
    border-bottom: 1px solid {dh.SLATE_3};
    padding-bottom: 0.4rem;
    margin: 2rem 0 0.9rem;
  }}
</style>
""",
    unsafe_allow_html=True,
)

# ── Header ─────────────────────────────────────────────────────────────────────
set_header(
    title="Search Keyword Trends Hub",
    description=(
        "Unified analytics portal for search demand intelligence. "
        "Surface activation opportunities, post-purchase curiosity gaps, "
        "and conversion anomalies across all keyword windows."
    ),
    background_image_path=Path(__file__).resolve().parent
    / "pages"
    / "assets"
    / "hub_header.png",
)

# ── Connection error banner ────────────────────────────────────────────────────
if st.session_state.get("connection_error"):
    st.error(f"Failed to connect to Doris backend: {st.session_state.connection_error}")
    st.stop()

# ── Card navigation ────────────────────────────────────────────────────────────
st.markdown('<div class="section-head">Dashboards</div>', unsafe_allow_html=True)

st.markdown(
    """
<div class="nav-grid">

  <a class="nav-card" href="/post_purchase_intent_analytics" target="_self">
    <span class="nav-card-icon"></span>
    <div class="nav-card-title">Post-Purchase Intent Analytics</div>
    <div class="nav-card-desc">
      Identify keywords with high post-order search velocity relative to initial conversion —
      revealing demand gaps for bundles, accessories, and recommendation improvements.
    </div>
    <div class="nav-card-meta">
      <span class="nav-tag nav-tag-teal">post_to_pre_ratio</span>
      <span class="nav-tag nav-tag-violet">revenue gap</span>
      <span class="nav-tag nav-tag-amber">funnel analysis</span>
    </div>
    <span class="nav-card-arrow">→</span>
  </a>

  <a class="nav-card" href="/search_trends" target="_self">
    <span class="nav-card-icon"></span>
    <div class="nav-card-title">Keyword Velocity Intelligence</div>
    <div class="nav-card-desc">
      Surfaces keywords where search demand is spiking faster than the baseline
      but conversion hasn't followed — your live activation windows.
    </div>
    <div class="nav-card-meta">
      <span class="nav-tag nav-tag-amber">trend_velocity_score</span>
      <span class="nav-tag nav-tag-teal">conversion gap</span>
      <span class="nav-tag nav-tag-amber">opportunity map</span>
    </div>
    <span class="nav-card-arrow">→</span>
  </a>

</div>
""",
    unsafe_allow_html=True,
)

# ── Mart documentation ─────────────────────────────────────────────────────────
st.markdown(
    '<div class="section-head">Mart documentation</div>', unsafe_allow_html=True
)

st.markdown(
    """
<div class="docs-grid">
  <div class="docs-block">
    <h4>mart.search_keyword_trend — overview</h4>
    <p>
      Pre-aggregated hopping windows (1 h) over the raw search event stream.
      Each row is a unique <code>(window_start, window_end, search_keyword)</code> triple,
      enriched with baseline comparison, regional attribution, and channel/device breakdown.
      Used as the single source of truth for all search demand dashboards.
    </p>
  </div>
  <div class="docs-block">
    <h4>Core field definitions</h4>
    <p><code>trend_velocity_score</code> — rate of search volume acceleration expressed as a
    Z-score against the 24 h baseline (<code>baseline_search_count</code>).
    Values above 2 indicate a statistically significant spike.</p>
    <p><code>post_to_pre_search_ratio</code> — post-purchase queries ÷ pre-order checks.
    High ratio signals accessory demand, troubleshooting, or upsell opportunities
    not captured by current recommendation flows.</p>
    <p><code>conversion_proxy_rate</code> — attributed orders ÷ search count.
    A low rate on a high-velocity keyword is the primary activation signal.</p>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
<div style="margin-top:2.5rem; padding-top:1rem; border-top:1px solid {dh.SLATE_3};
     font-size:0.72rem; color:{dh.MUTED}; display:flex; justify-content:space-between;">
  <span>Source: <code style="color:{dh.TEAL}">mart.search_keyword_trend</code></span>
  <span>Search Keyword Trends Hub · {dh.SLATE}</span>
</div>
""",
    unsafe_allow_html=True,
)
