"""
Psychographic Input Component
This component allows users to either upload their own psychographic research image
or configure AI generation settings that will be used during analysis.
"""
import streamlit as st
import json

def psychographic_input_section(brief_text=None):
    """
    Display the psychographic data configuration section for users.
    Simplified UI that integrates with the main analysis flow.
    
    Args:
        brief_text: The campaign brief text (passed from landing_layout)
    """
    
    # Simple, clean header matching the main design
    st.markdown("### Audience Intelligence Data")
    st.markdown("Configure how to analyze your target audience's psychographic profile.")
    
    # Check if psychographic data already exists
    if 'audience_insights' in st.session_state and st.session_state.audience_insights:
        # Simple success message with change option
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.success("✅ Psychographic data configured")
        with col3:
            if st.button("Reconfigure", key="change_psychographic", type="secondary", use_container_width=True):
                del st.session_state.audience_insights
                if 'psychographic_config' in st.session_state:
                    del st.session_state.psychographic_config
                st.rerun()
    
    else:
        # Create tabs matching the RFP input design
        tab1, tab2 = st.tabs(["AI Generation", "Upload Research"])
        
        with tab1:
            # AI Generation Configuration
            st.markdown('<div style="margin-top: 12px;"></div>', unsafe_allow_html=True)
            
            # Info message
            st.markdown("""
            <div style='background: #f0f9ff; padding: 12px; border-radius: 8px; border-left: 3px solid #3b82f6;'>
                <div style='color: #1e40af; font-weight: 500; margin-bottom: 4px;'>Smart Psychographic Generation</div>
                <div style='color: #475569; font-size: 0.9rem;'>Our AI will analyze your brief and generate a targeted psychographic profile. Optionally customize demographics below.</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div style="margin-top: 16px;"></div>', unsafe_allow_html=True)
            
            # Store configuration in session state
            if 'psychographic_config' not in st.session_state:
                st.session_state.psychographic_config = {
                    'method': 'generate',
                    'demographics': {}
                }
            else:
                st.session_state.psychographic_config['method'] = 'generate'
            
            # Optional demographics with expandable section
            with st.expander("Customize Target Demographics (Optional)", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    age_range = st.text_input(
                        "Age Range",
                        placeholder="e.g., 25-45",
                        help="Enter age range (e.g., 25-45) or leave blank for auto-detection",
                        key="config_age"
                    )
                    
                    # Validate age range format
                    age_error = False
                    if age_range and age_range.strip():
                        # Check for valid format: number-number
                        import re
                        age_pattern = r'^(\d{1,3})\s*[-–]\s*(\d{1,3})$'
                        match = re.match(age_pattern, age_range.strip())
                        
                        if not match:
                            st.error("⚠️ Please enter age range as 'min-max' (e.g., 25-45)")
                            age_error = True
                        else:
                            min_age, max_age = int(match.group(1)), int(match.group(2))
                            if min_age < 0 or max_age > 120:
                                st.error("⚠️ Age must be between 0 and 120")
                                age_error = True
                            elif min_age >= max_age:
                                st.error("⚠️ Maximum age must be greater than minimum age")
                                age_error = True
                    
                    income = st.selectbox(
                        "Income Level",
                        options=["Auto-detect", "Low", "Lower Middle", "Middle", "Upper Middle", "High", "Ultra High"],
                        index=0,
                        key="config_income"
                    )
                
                with col2:
                    gender = st.selectbox(
                        "Gender Focus",
                        options=["Auto-detect", "All Genders", "Male", "Female", "Non-binary"],
                        index=0,
                        key="config_gender"
                    )
                    
                    location = st.selectbox(
                        "Geographic Focus",
                        options=["Auto-detect", "Urban", "Suburban", "Rural", "Mixed"],
                        index=0,
                        key="config_location"
                    )
                
                # Store the configuration (only store valid age range)
                st.session_state.psychographic_config['demographics'] = {
                    'age': age_range if age_range and not age_error else None,
                    'income': income if income != "Auto-detect" else None,
                    'gender': gender if gender not in ["Auto-detect", "All Genders"] else None,
                    'location': location if location != "Auto-detect" else None
                }
            
            # Configuration status
            # config_count = sum(1 for v in st.session_state.psychographic_config['demographics'].values() if v)
            # if config_count > 0:
            #     st.info(f"📊 {config_count} demographic parameter{'s' if config_count != 1 else ''} configured")
            # else:
            #     st.info("📊 Using AI auto-detection for all demographics")
            
        with tab2:
            # Upload Option
            st.markdown('<div style="margin-top: 12px;"></div>', unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Upload Psychographic Research Image",
                type=["png", "jpg", "jpeg"],
                key="psychographic_upload_file",
                help="Supported formats: PNG, JPG, JPEG. Upload a chart or infographic containing demographic and psychographic data."
            )
            
            if uploaded_file:
                # Store configuration
                st.session_state.psychographic_config = {
                    'method': 'upload',
                    'file': uploaded_file
                }
                
                # Display file details in a clean way (matching RFP upload style)
                file_details = {
                    "Filename": uploaded_file.name,
                    "File size": f"{round(uploaded_file.size / 1024, 2)} KB",
                    "File type": uploaded_file.type
                }
                
                # st.markdown("<div style='background: #f8fafc; padding: 12px; border-radius: 8px; margin-top: 12px;'>", unsafe_allow_html=True)
                # st.markdown(f"<div style='font-weight: 500;'>File Details:</div>", unsafe_allow_html=True)
                # for key, value in file_details.items():
                #     st.markdown(f"<div style='font-size: 0.9rem; margin-top: 5px;'><span style='color: #64748b;'>{key}:</span> {value}</div>", unsafe_allow_html=True)
                # st.markdown("</div>", unsafe_allow_html=True)
                
                st.success("File ready for analysis. Click 'Run Predictive Analysis' to process.")
            else:
                st.info("Upload a psychographic research image to use your own data instead of AI generation.")


def process_psychographic_config(brief_text):
    """
    Process the psychographic configuration during analysis.
    This is called when the user clicks "Run Predictive Analysis".
    
    Args:
        brief_text: The campaign brief text
        
    Returns:
        dict: The generated or processed psychographic insights
    """
    from core.ai_insights import generate_audience_insights, generate_pychographic_highlights
    
    # If no config exists, use AI generation with defaults
    if 'psychographic_config' not in st.session_state:
        st.session_state.psychographic_config = {
            'method': 'generate',
            'demographics': {}
        }
    
    config = st.session_state.psychographic_config
    
    try:
        if config['method'] == 'generate':
            # Prepare demographics string
            demo = config.get('demographics', {})
            demo_parts = []
            if demo.get('age'):
                demo_parts.append(f"Age: {demo['age']}")
            if demo.get('gender'):
                demo_parts.append(f"Gender: {demo['gender']}")
            if demo.get('income'):
                demo_parts.append(f"Income: {demo['income']}")
            if demo.get('location'):
                demo_parts.append(f"Location: {demo['location']}")
            
            demographics_info = " | ".join(demo_parts) if demo_parts else "General audience"
            
            # Generate with AI
            insights = generate_audience_insights(
                source_type='generate',
                brief_text=brief_text,
                demographics_info=demographics_info
            )
            
        elif config['method'] == 'upload':
            # Process uploaded file
            uploaded_file = config['file']
            insights = generate_audience_insights(
                source_type='upload',
                uploaded_file=uploaded_file
            )
        else:
            # Default to AI generation
            insights = generate_audience_insights(
                source_type='generate',
                brief_text=brief_text,
                demographics_info="General audience"
            )
        
        # Generate highlights
        if insights:
            try:
                highlights = generate_pychographic_highlights(insights)
                st.session_state.pychographic_highlights = highlights
            except:
                pass
        
        return insights
        
    except Exception as e:
        st.error(f"Error processing psychographic data: {str(e)}")
        return None
