import streamlit as st

from core.disclaimer import RCC_DISCLAIMER


def display_rcc_disclaimer():
    """Render the persistent RCC disclaimer banner."""
    st.markdown(
        f"""
        <p style="border: 1px solid #e2e8f0; background-color: #f8fafc;
                  border-radius: 6px; padding: 12px 16px; font-size: 0.8rem;
                  line-height: 1.5; color: #475569; margin-bottom: 0.5rem;">
            {RCC_DISCLAIMER}
        </p>
        """,
        unsafe_allow_html=True,
    )
