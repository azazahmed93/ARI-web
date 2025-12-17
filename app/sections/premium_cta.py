import streamlit as st
from core.utils import (
    create_pdf_download_link,
    create_infographic_download_link,
)

# Import export functionality
try:
    from core.export_orchestrator import export_to_pptx
    from core.s3_export_service import S3ExportService, export_to_s3_and_stitch
    EXPORT_AVAILABLE = True
    S3_EXPORT_AVAILABLE = True
except ImportError as e:
    print(f"Export import error: {e}")
    EXPORT_AVAILABLE = False
    S3_EXPORT_AVAILABLE = False

def premium_cta(scores, improvement_areas, percentile, brand_name, industry, product_type, brief_text):
  # Create container with custom CSS for styling
    st.markdown('<div class="premium-container"></div>', unsafe_allow_html=True)
    premium_container = st.container()
    with premium_container:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Header and introduction - full width
        st.markdown('<span class="tag-enterprise">Enterprise Analytics</span>', unsafe_allow_html=True)
        st.markdown("### Ready to take your marketing to the next level?")
        st.write("Download our comprehensive enterprise report with detailed metrics, actionable insights, and competitive benchmarking to optimize your campaign performance.")
        
        # Create a container for the checkmarks
        check_container = st.container()
        with check_container:
            # Use columns for the checkmarks - make more visible
            check1, check2, check3 = st.columns(3)
            with check1:
                st.markdown('<div style="display: flex; align-items: center;"><span style="color: #5865f2; font-size: 1.2rem; margin-right: 8px;">✓</span> <span style="font-weight: 500;">Advanced Metrics</span></div>', unsafe_allow_html=True)
            with check2:
                st.markdown('<div style="display: flex; align-items: center;"><span style="color: #5865f2; font-size: 1.2rem; margin-right: 8px;">✓</span> <span style="font-weight: 500;">Competitive Analysis</span></div>', unsafe_allow_html=True)
            with check3:
                st.markdown('<div style="display: flex; align-items: center;"><span style="color: #5865f2; font-size: 1.2rem; margin-right: 8px;">✓</span> <span style="font-weight: 500;">Executive Summary</span></div>', unsafe_allow_html=True)
                
        # Add space between sections
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Customize Your Report section with improved styling
        st.markdown("""
        <div style="background-color: #f8fafc; border-radius: 12px; padding: 25px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
            <h3 style="margin-top: 0; color: #1e293b; font-size: 1.5rem; margin-bottom: 15px; display: flex; align-items: center;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#5865f2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 10px;">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
                Customize Your Report
            </h3>
            <p style="color: #475569; margin-bottom: 20px; font-size: 1rem;">Select which sections to include in your PDF report:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create a clean two-column layout for the checkboxes
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="margin-bottom: 12px; font-weight: 600; color: #0369a1; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">
                Core Analytics
            </div>
            """, unsafe_allow_html=True)
            include_metrics = st.checkbox("Advanced Metrics", value=True, key="metrics")
            include_benchmark = st.checkbox("Benchmark Comparison", value=True, key="benchmark")
            include_media = st.checkbox("Media Affinities", value=True, key="media")
            include_tv = st.checkbox("TV Networks", value=True, key="tv")
            include_streaming = st.checkbox("Streaming Platforms", value=True, key="streaming")
        
        with col2:
            st.markdown("""
            <div style="margin-bottom: 12px; font-weight: 600; color: #0f766e; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">
                Audience Intelligence
            </div>
            """, unsafe_allow_html=True)
            include_psychographic = st.checkbox("Psychographic Highlights", value=True, key="psychographic")
            include_audience = st.checkbox("Audience Summary", value=True, key="audience")
            
            # Additional checkbox for trend analysis with highlight styling
            include_trends = st.checkbox("Marketing Trend Analysis", value=True, help="Include the marketing trend heatmap and key trend insights in your report", key="trends")
            
            # Add competitor tactics checkbox
            # Use a different key name to avoid conflicts with session state
            include_competitor_tactics = st.checkbox("Competitor Tactics", value=True, help="Include competitor strategy recommendations in your report", key="include_competitor_tactics")
        
        # Create dictionary of sections to include
        include_sections = {
            'metrics': include_metrics,
            'benchmark': include_benchmark,
            'media_affinities': include_media,
            'tv_networks': include_tv,
            'streaming': include_streaming,
            'psychographic': include_psychographic,
            'audience': include_audience,
            'next_steps': False,  # Removed Next Steps option as requested
            'trends': include_trends,
            'competitor_tactics': include_competitor_tactics if isinstance(include_competitor_tactics, bool) else True
        }
        
        # Generate and display the PDF download link with section selections
        st.markdown("""
        <div style="margin-top: 25px; text-align: center;">
            <div style="background-color: #f8f7ff; padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px dashed #c7d2fe;">
                <p style="margin: 0; color: #4338ca; font-weight: 500;">Your custom report is ready for download</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        pdf_link = create_pdf_download_link(scores, improvement_areas, percentile, brand_name, industry, product_type, include_sections, brief_text)
        st.markdown(f'<div style="text-align: center;">{pdf_link}</div>', unsafe_allow_html=True)
        
        # Add infographic download option for email sharing
        st.markdown('<div style="text-align: center; margin-top: 15px;">', unsafe_allow_html=True)
        # Get the primary audience segment if available
        # top_audience = None
        # if st.session_state.audience_segments and 'primary' in st.session_state.audience_segments:
        #     top_audience = st.session_state.audience_segments['primary']

        # infographic_link = create_infographic_download_link(scores, improvement_areas, percentile, brand_name, top_audience)
        # st.markdown(f'{infographic_link}', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Export to PowerPoint section
        if EXPORT_AVAILABLE:
            st.markdown("""
            <div style="margin-top: 25px; text-align: center;">
                <div style="background-color: #f0fdf4; padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px dashed #86efac;">
                    <p style="margin: 0; color: #166534; font-weight: 500;">Export your report as a PowerPoint presentation</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Use the export_id from session state (generated early in results.py)
            # This ensures React components and Streamlit use the same export session
            export_id = st.session_state.get('export_id')
            if not export_id:
                import uuid
                export_id = str(uuid.uuid4())
                st.session_state.export_id = export_id

            export_col1, export_col2, export_col3 = st.columns([1, 2, 1])
            with export_col2:
                if st.button("📥 Export to PowerPoint", type="secondary", use_container_width=True, key="pptx_export_btn"):
                    with st.spinner("Generating and uploading presentation..."):
                        try:
                            # Create a progress placeholder
                            progress_placeholder = st.empty()

                            def update_progress(percent, message):
                                progress_placeholder.progress(percent / 100, text=message)

                            if S3_EXPORT_AVAILABLE:
                                # Use S3 export pipeline with the session's export_id
                                result = export_to_s3_and_stitch(
                                    session_state=dict(st.session_state),
                                    brand_name=brand_name,
                                    industry=industry,
                                    components=['streamlit_complete', 'cultural_moments'],
                                    progress_callback=update_progress,
                                    export_id=export_id  # Use the session's export_id
                                )

                                progress_placeholder.empty()

                                if result.success and result.download_url:
                                    # Store download URL in session state for persistence
                                    st.session_state['pptx_download_url'] = result.download_url
                                    st.session_state['pptx_export_id'] = result.export_id

                                    # Show download link
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
                                # Fallback to direct download
                                pptx_bytes = export_to_pptx(
                                    session_state=dict(st.session_state),
                                    brand_name=brand_name,
                                    industry=industry,
                                    progress_callback=update_progress
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

                # Show existing download URL if available (persists across reruns)
                elif st.session_state.get('pptx_download_url'):
                    st.link_button(
                        label="⬇️ Download Presentation",
                        url=st.session_state['pptx_download_url'],
                        type="primary",
                        use_container_width=True
                    )

        # Close the outer div
        st.markdown('</div>', unsafe_allow_html=True)
    