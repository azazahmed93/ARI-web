import streamlit as st
from core.utils import (
    create_pdf_download_link,
    create_infographic_download_link,
)

# Import export functionality
try:
    from core.export_orchestrator import export_to_pptx, export_to_pptx_with_screenshots
    from core.s3_export_service import S3ExportService, export_to_s3_and_stitch
    EXPORT_AVAILABLE = True
    S3_EXPORT_AVAILABLE = True
except ImportError as e:
    print(f"Export import error: {e}")
    EXPORT_AVAILABLE = False
    S3_EXPORT_AVAILABLE = False

# Check if screenshot service is available
try:
    from core.streamlit_screenshot import capture_streamlit_screenshots
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False

def premium_cta(scores, improvement_areas, percentile, brand_name, industry, product_type, brief_text):
    # Create container with custom CSS for styling
    st.markdown('<div class="premium-container"></div>', unsafe_allow_html=True)
    premium_container = st.container()
    with premium_container:
        st.markdown("<br>", unsafe_allow_html=True)

        # Compact header
        st.markdown('<span class="tag-enterprise">Enterprise Analytics</span>', unsafe_allow_html=True)
        st.markdown("### Export Your Report")
        st.write("Download your analysis as PDF or PowerPoint with customizable sections.")

        # Create tabs for PDF and PowerPoint
        pptx_tab, pdf_tab = st.tabs(["📊 PowerPoint", "📄 PDF Report"])

        # =====================================================================
        # POWERPOINT TAB
        # =====================================================================
        with pptx_tab:
            if EXPORT_AVAILABLE:
                # Compact expander for customization options
                with st.expander("Customize PowerPoint sections", expanded=False):
                    pptx_col1, pptx_col2 = st.columns(2)
                    with pptx_col1:
                        st.markdown('<p style="font-weight: 600; color: #166534; font-size: 0.85rem; margin-bottom: 8px;">CORE ANALYTICS</p>', unsafe_allow_html=True)
                        pptx_include_metrics = st.checkbox("Advanced Metrics", value=True, key="pptx_metrics", help="Score Card + Detailed Metrics")
                        pptx_include_benchmark = st.checkbox("Benchmark", value=True, key="pptx_benchmark", help="Advanced Analysis")
                        pptx_include_media = st.checkbox("Media Affinities", value=True, key="pptx_media")
                        pptx_include_trends = st.checkbox("Marketing Trends", value=True, key="pptx_trends")
                        pptx_include_cultural = st.checkbox("Cultural Moments", value=True, key="pptx_cultural")
                    with pptx_col2:
                        st.markdown('<p style="font-weight: 600; color: #0f766e; font-size: 0.85rem; margin-bottom: 8px;">AUDIENCE INTELLIGENCE</p>', unsafe_allow_html=True)
                        pptx_include_psychographic = st.checkbox("Psychographic Highlights", value=True, key="pptx_psychographic")
                        pptx_include_growth = st.checkbox("Growth Audience", value=True, key="pptx_growth")
                        pptx_include_emerging = st.checkbox("Emerging Audience", value=True, key="pptx_emerging")
                        pptx_include_competitor = st.checkbox("Competitor Tactics", value=True, key="pptx_competitor")
                        pptx_include_resonance = st.checkbox("Resonance Pathway", value=True, key="pptx_resonance")

                # Build include_sections dict for PPTX export
                pptx_include_sections = {
                    'advanced_metrics': pptx_include_metrics,
                    'benchmark': pptx_include_benchmark,
                    'psychographic': pptx_include_psychographic,
                    'growth_audience': pptx_include_growth,
                    'emerging_audience': pptx_include_emerging,
                    'media_affinities': pptx_include_media,
                    'trends': pptx_include_trends,
                    'competitor_tactics': pptx_include_competitor,
                }

                # Build components list dynamically
                pptx_components = ['streamlit_complete']
                if pptx_include_cultural:
                    pptx_components.append('cultural_moments')
                if pptx_include_resonance:
                    pptx_components.append('resonance_pathway')

                # Export ID
                export_id = st.session_state.get('export_id')
                if not export_id:
                    import uuid
                    export_id = str(uuid.uuid4())
                    st.session_state.export_id = export_id

                # Visual capture mode toggle (compact)
                use_screenshots = st.checkbox(
                    "Use visual capture mode",
                    value=SCREENSHOT_AVAILABLE,
                    disabled=not SCREENSHOT_AVAILABLE,
                    help="Pixel-perfect screenshots. Disable for faster generation.",
                    key="use_screenshot_export"
                ) if SCREENSHOT_AVAILABLE else False

                # Export button
                export_col1, export_col2, export_col3 = st.columns([1, 2, 1])
                with export_col2:
                    if st.button("Export to PowerPoint", type="primary", use_container_width=True, key="pptx_export_btn"):
                        with st.spinner("Generating and uploading presentation..."):
                            try:
                                progress_placeholder = st.empty()

                                def update_progress(percent, message):
                                    progress_placeholder.progress(percent / 100, text=message)

                                if S3_EXPORT_AVAILABLE:
                                    import os
                                    app_url = os.environ.get('STREAMLIT_APP_URL', 'http://localhost:3006')
                                    result = export_to_s3_and_stitch(
                                        session_state=dict(st.session_state),
                                        brand_name=brand_name,
                                        industry=industry,
                                        components=pptx_components,
                                        progress_callback=update_progress,
                                        export_id=export_id,
                                        use_screenshots=use_screenshots,
                                        app_url=app_url,
                                        include_sections=pptx_include_sections
                                    )
                                    progress_placeholder.empty()
                                    if result.success and result.download_url:
                                        st.session_state['pptx_download_url'] = result.download_url
                                        st.session_state['pptx_export_id'] = result.export_id
                                        st.success("Presentation generated successfully!")
                                        st.link_button(
                                            label="⬇️ Download Presentation",
                                            url=result.download_url,
                                            type="primary",
                                            use_container_width=True
                                        )
                                    else:
                                        st.error(f"Export failed: {result.error}")
                                else:
                                    if use_screenshots:
                                        import os
                                        app_url = os.environ.get('STREAMLIT_APP_URL', 'http://localhost:3006')
                                        pptx_bytes = export_to_pptx_with_screenshots(
                                            session_state=dict(st.session_state),
                                            brand_name=brand_name,
                                            industry=industry,
                                            app_url=app_url,
                                            use_live_capture=True,
                                            progress_callback=update_progress,
                                            include_sections=pptx_include_sections
                                        )
                                    else:
                                        pptx_bytes = export_to_pptx(
                                            session_state=dict(st.session_state),
                                            brand_name=brand_name,
                                            industry=industry,
                                            progress_callback=update_progress,
                                            include_sections=pptx_include_sections
                                        )
                                    progress_placeholder.empty()
                                    st.download_button(
                                        label="⬇️ Download Presentation",
                                        data=pptx_bytes,
                                        file_name=f"ARI_Report_{brand_name.replace(' ', '_')}.pptx",
                                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                        type="primary"
                                    )
                                    st.success("Presentation generated successfully!")
                            except Exception as e:
                                print(e)
                                st.error(f"Error generating presentation: {str(e)}")

                    elif st.session_state.get('pptx_download_url'):
                        st.link_button(
                            label="⬇️ Download Presentation",
                            url=st.session_state['pptx_download_url'],
                            type="primary",
                            use_container_width=True
                        )


        # =====================================================================
        # PDF TAB
        # =====================================================================
        with pdf_tab:
            # Compact expander for customization options
            with st.expander("Customize PDF sections", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<p style="font-weight: 600; color: #0369a1; font-size: 0.85rem; margin-bottom: 8px;">CORE ANALYTICS</p>', unsafe_allow_html=True)
                    include_metrics = st.checkbox("Advanced Metrics", value=True, key="metrics")
                    include_benchmark = st.checkbox("Benchmark Comparison", value=True, key="benchmark")
                    include_media = st.checkbox("Media Affinities", value=True, key="media")
                    include_tv = st.checkbox("TV Networks", value=True, key="tv")
                    include_streaming = st.checkbox("Streaming Platforms", value=True, key="streaming")
                with col2:
                    st.markdown('<p style="font-weight: 600; color: #0f766e; font-size: 0.85rem; margin-bottom: 8px;">AUDIENCE INTELLIGENCE</p>', unsafe_allow_html=True)
                    include_psychographic = st.checkbox("Psychographic Highlights", value=True, key="psychographic")
                    include_audience = st.checkbox("Audience Summary", value=True, key="audience")
                    include_trends = st.checkbox("Marketing Trends", value=True, key="trends")
                    include_competitor_tactics = st.checkbox("Competitor Tactics", value=True, key="include_competitor_tactics")

            # Create dictionary of sections to include
            include_sections = {
                'metrics': include_metrics,
                'benchmark': include_benchmark,
                'media_affinities': include_media,
                'tv_networks': include_tv,
                'streaming': include_streaming,
                'psychographic': include_psychographic,
                'audience': include_audience,
                'next_steps': False,
                'trends': include_trends,
                'competitor_tactics': include_competitor_tactics if isinstance(include_competitor_tactics, bool) else True
            }

            # PDF download button
            pdf_link = create_pdf_download_link(scores, improvement_areas, percentile, brand_name, industry, product_type, include_sections, brief_text)
            st.markdown(f'<div style="text-align: center; margin-top: 15px;">{pdf_link}</div>', unsafe_allow_html=True)

        # Close the outer div
        st.markdown('</div>', unsafe_allow_html=True)
    