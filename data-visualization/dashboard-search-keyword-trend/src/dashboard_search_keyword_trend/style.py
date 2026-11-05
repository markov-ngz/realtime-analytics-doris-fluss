import base64
from pathlib import Path

import streamlit as st


class DashboardColors:
    AMBER = "#F59E0B"
    TEAL = "#14B8A6"
    SLATE = "#0F172A"
    SLATE_2 = "#1E293B"
    SLATE_3 = "#334155"
    MUTED = "#94A3B8"
    WHITE = "#F8FAFC"
    VIOLET = "#818CF8"
    ORANGE = "#FB923C"


def set_header(
    title: str,
    description: str | None = None,
    background_image_path: str | Path | None = None,
) -> None:
    img_base64 = (
        _get_base64_image(background_image_path) if background_image_path else ""
    )

    st.markdown(
        f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

      .header {{
        position: relative;
        height: 230px;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 1.5rem;
        background:
          linear-gradient(
            90deg,
            rgba(10, 20, 40, 0.88) 0%,
            rgba(20, 50, 70, 0.60) 55%,
            rgba(245, 158, 11, 0.15) 100%
          ),
          url("data:image/png;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        display: flex;
        align-items: flex-end;
        padding: 0;
      }}
      .header-inner {{
        padding: 1.5rem 2rem 1.4rem;
        width: 100%;
      }}
      .header-tag {{
        display: inline-block;
        background: rgba(245, 158, 11, 0.18);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 3px;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        padding: 0.15rem 0.55rem;
        margin-bottom: 0.55rem;
        font-family: 'IBM Plex Mono', monospace;
      }}
      .header h1 {{
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 1.65rem;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #F8FAFC;
        margin: 0 0 0.3rem;
        text-shadow: 0 1px 8px rgba(0,0,0,0.45);
      }}
      .header p {{
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.875rem;
        color: rgba(248, 250, 252, 0.75);
        margin: 0;
        max-width: 640px;
        line-height: 1.55;
        text-shadow: 0 1px 4px rgba(0,0,0,0.4);
      }}
    </style>
    <div class="header">
      <div class="header-inner">
        <h1>{title}</h1>
        {f"<p>{description}</p>" if description else ""}
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def _get_base64_image(image_path: str) -> str:
    if image_path.exists():
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    raise FileNotFoundError(f"Could not file at path : {image_path}")
