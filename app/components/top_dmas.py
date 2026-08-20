"""Top Markets (DMAs) table for audience segment cards."""
import streamlit as st


def _format_audience(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{round(n / 1_000)}K"
    return str(n)


def build_top_dmas_html(top_dmas, accent_color="#5865f2"):
    """
    Build the ranked Top-DMA list as a CSS grid.

    Deliberately NOT a <table>: Streamlit's markdown stylesheet forces cell
    borders, wide padding, and tall rows onto table elements, which inline
    styles cannot fully override. A grid renders compact and unstyled.
    """
    cells = ""
    for dma in top_dmas:
        if dma["index"] >= 120:
            chip_style = f"background-color: {accent_color}; color: #fff;"
        else:
            chip_style = "background-color: #e8eaed; color: #4b5563;"
        cells += f"""<div style="font-size: 0.85rem; color: #444; padding: 3px 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"><span style="color: #aaa; font-variant-numeric: tabular-nums;">{dma['rank']}.</span> {dma['dma_name']}</div>
<div style="font-size: 0.78rem; color: #888; padding: 3px 0; text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap;">{_format_audience(dma['est_audience'])}</div>
<div style="padding: 2px 0 2px 48px; text-align: right;"><span style="display: inline-block; font-size: 0.7rem; font-weight: 600; padding: 2px 8px; border-radius: 10px; font-variant-numeric: tabular-nums; {chip_style}" title="Concentration index: {dma['index']} (100 = US average)">{dma['index']}</span></div>"""

    header_style = (
        "font-size: 0.65rem; font-weight: 600; color: #999; "
        "text-transform: uppercase; letter-spacing: 0.06em; "
        "padding-bottom: 4px; border-bottom: 1px solid #e5e7eb; margin-bottom: 2px;"
    )
    return f"""<div style="display: grid; grid-template-columns: 1fr auto auto; column-gap: 12px; align-items: center;">
<div style="{header_style}">Market</div>
<div style="{header_style} text-align: right;">Est. Audience</div>
<div style="{header_style} text-align: right; padding-left: 48px;">Index</div>
{cells}
</div>
<p style="margin: 8px 0 0 0; font-size: 0.7rem; color: #aaa; line-height: 1.4;">
Index: audience concentration vs the US average (100), from US Census (ACS) data.
Est. audience: people in the market matching this segment's profile (directional).
</p>"""


def display_top_dmas(top_dmas, accent_color="#5865f2"):
    """
    Render the ranked Top-DMA list for a segment. No-op when the segment
    carries no ranking (non-US campaigns, older analyses) — mirrors how the
    demographics breakdown hides itself.

    Expanded by default so the ranking is visible without a click; users can
    collapse it per card.
    """
    if not top_dmas:
        return

    with st.expander("Top Markets (DMAs)", expanded=True):
        st.markdown(build_top_dmas_html(top_dmas, accent_color), unsafe_allow_html=True)
