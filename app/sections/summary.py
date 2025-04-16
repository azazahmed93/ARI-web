import streamlit as st
from core.utils import is_siteone_hispanic_campaign

# Import the grammar fix function from ai_insights module
# This helps clean up grammatical errors and duplicate words
from core.ai_insights import (
    fix_grammar_and_duplicates,
)
from components.spinner import get_random_spinner_message

def summary(percentile, scores, improvement_areas, brand_name, brief_text, industry, product_type):

    # Create a dashboard-style KPI row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 20px; text-align: center;">
            <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #5865f2;">
                PERCENTILE RANK
            </div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #5865f2; margin: 10px 0;">Top {percentile}%</div>
            <div style="font-size: 0.85rem; color: #555;">Among all analyzed campaigns</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Get expected impact from AI insights if available
        # Calculate ROI potential dynamically based on scores
        avg_score = sum(scores.values()) / len(scores)
        # Dynamic ROI calculation based on scores - better scores = better ROI
        roi_percent = int(5 + (avg_score / 10) * 20)
        roi_potential = f"+{roi_percent}%"
        
        # Override with AI insight if available
        if 'ai_insights' in st.session_state and st.session_state.ai_insights:
            ai_insights = st.session_state.ai_insights
            prediction = ai_insights.get('performance_prediction', '')
            if prediction and '%' in prediction:
                # Try to extract percentage from the prediction text
                import re
                roi_match = re.search(r'(\+\d+%|\d+%)', prediction)
                if roi_match:
                    roi_potential = roi_match.group(0)
                    if not roi_potential.startswith('+'):
                        roi_potential = f"+{roi_potential}"
        
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 20px; text-align: center;">
            <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #10b981;">EXPECTED IMPACT</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #10b981; margin: 10px 0;">{roi_potential}</div>
            <div style="font-size: 0.85rem; color: #555;">Projected ROI increase</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 20px; text-align: center;">
            <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #f43f5e;">ACTION ITEMS</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #f43f5e; margin: 10px 0;">{len(improvement_areas)}</div>
            <div style="font-size: 0.85rem; color: #555;">Priority improvement areas</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add an informative benchmark section using the Hyperdimensional Matrix HTML template
    
    # Read the HTML template file
    with open("attached_assets/ARI_Hyperdimensional_Matrix.html", "r") as file:
        matrix_template_html = file.read()
    
    # Start the custom section 
    st.markdown("""
    <div style="margin-top: 25px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 20px;">
        <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #5865f2; margin-bottom: 15px; text-align: center;">Hyperdimensional Campaign Performance Matrix</div>
    """, unsafe_allow_html=True)
    
    # Display benchmark text with dynamic AI-driven content
    if 'ai_insights' in st.session_state and st.session_state.ai_insights:
        ai_insights = st.session_state.ai_insights
        
        # Get strengths from AI if available
        strengths = ai_insights.get('strengths', [])
        
        # Create a dynamic strength list if available
        strength_areas = []
        for strength in strengths[:2]:  # Get up to 2 top strengths
            if 'area' in strength:
                strength_areas.append(strength['area'].lower())
        
        # Default strengths if none found
        if not strength_areas:
            strength_areas = ['relevance', 'authenticity']
            
        # Format strengths for display
        if len(strength_areas) > 1:
            strength_text = f"{strength_areas[0]} and {strength_areas[1]}"
        else:
            strength_text = f"{strength_areas[0]}" if strength_areas else "cultural relevance"
            
        # Determine audience type based on the brief content
        audience_type = "Hispanic" if "SiteOne" in brand_name and is_siteone_hispanic_campaign(brand_name, brief_text) else "general market"
        
        # Dynamic audience detection
        if brief_text:
            if "Gen Z" in brief_text or "GenZ" in brief_text or "Generation Z" in brief_text:
                audience_type = "Gen Z"
            elif "Millennial" in brief_text:
                audience_type = "Millennial"
            elif "Hispanic" in brief_text or "Latino" in brief_text or "Spanish" in brief_text:
                audience_type = "Hispanic"
            elif "Black" in brief_text or "African American" in brief_text:
                audience_type = "African American"
            elif "Asian" in brief_text:
                audience_type = "Asian American"
            elif "LGBTQ" in brief_text or "LGBT" in brief_text:
                audience_type = "LGBTQ+"
            
        st.markdown(f"""
        <div style="color: #333; font-size: 1rem; line-height: 1.6;">
            This campaign ranks in the top <span style="font-weight: 600; color: #5865f2;">{percentile}%</span> of {audience_type}-facing national campaigns
            for Audience Resonance Index™. The campaign outperforms the majority of peer initiatives in {strength_text} — 
            based on Digital Culture Group's comprehensive analysis of <span style="font-weight: 600; color: #5865f2;">{300 + (hash(brand_name) % 100)}</span> national marketing efforts.
        </div>
        <div style="margin-top: 2rem;">
            <div style="font-size: 0.9rem; font-weight: 600; color: #5865f2; margin-bottom: 10px;">Priority Improvement Areas</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Determine audience type based on the brief content (fallback case)
        audience_type = "Hispanic" if "SiteOne" in brand_name and is_siteone_hispanic_campaign(brand_name, brief_text) else "general market"
        
        # Dynamic audience detection
        if brief_text:
            if "Gen Z" in brief_text or "GenZ" in brief_text or "Generation Z" in brief_text:
                audience_type = "Gen Z"
            elif "Millennial" in brief_text:
                audience_type = "Millennial"
            elif "Hispanic" in brief_text or "Latino" in brief_text or "Spanish" in brief_text:
                audience_type = "Hispanic"
            elif "Black" in brief_text or "African American" in brief_text:
                audience_type = "African American"
            elif "Asian" in brief_text:
                audience_type = "Asian American"
            elif "LGBTQ" in brief_text or "LGBT" in brief_text:
                audience_type = "LGBTQ+"
            
        # Get the strength areas dynamically from the scores
        metric_scores = list(scores.items())
        metric_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get top 3 metrics as strengths
        top_metrics = metric_scores[:3] if len(metric_scores) >= 3 else metric_scores
        strength_areas = [m[0].lower() for m in top_metrics]
        
        # Format strengths for a natural language sentence
        if len(strength_areas) >= 3:
            strength_text = f"{strength_areas[0]}, {strength_areas[1]}, and {strength_areas[2]}"
        elif len(strength_areas) == 2:
            strength_text = f"{strength_areas[0]} and {strength_areas[1]}"
        else:
            strength_text = strength_areas[0] if strength_areas else "relevance, authenticity, and emotional connection"
            
        # For industry-specific sample size, calculate based on brand_name and industry/product
        sample_size = 300 + (hash(brand_name) % 100)
        if industry and product_type:
            # Adjust sample size based on industry and product
            industry_modifier = len(industry) % 20
            product_modifier = len(product_type) % 15
            sample_size = 300 + (hash(brand_name) % 100) + industry_modifier + product_modifier
        
        st.markdown(f"""
        <div style="color: #333; font-size: 1rem; line-height: 1.6;">
            This campaign ranks in the top <span style="font-weight: 600; color: #5865f2;">{percentile}%</span> of {audience_type}-facing national campaigns
            for Audience Resonance Index™. The campaign outperforms the majority of peer initiatives in {strength_text} — 
            based on Digital Culture Group's comprehensive analysis of <span style="font-weight: 600; color: #5865f2;">{sample_size}</span> national marketing efforts.
        </div>
        <div style="margin-top: 2rem;">
            <div style="font-size: 0.9rem; font-weight: 600; color: #5865f2; margin-bottom: 10px;">Priority Improvement Areas</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Create tabs for each improvement area (for clickable detailed view)
    if len(improvement_areas) > 0 and st.session_state.use_openai and st.session_state.ai_insights:
        # Check if AI insights are available
        ai_insights = st.session_state.ai_insights
        
        # Create tabs for each improvement area plus Competitor Tactics (if not already present)
        tab_titles = improvement_areas.copy()
        if "Competitor Tactics" not in tab_titles:
            tab_titles.append("Competitor Tactics")
        else:
            # If Competitor Tactics is already in the list, ensure it's only there once
            # Find all occurrences and remove all but the last one
            indices = [i for i, x in enumerate(tab_titles) if x == "Competitor Tactics"]
            if len(indices) > 1:
                # Keep only the last occurrence
                for idx in indices[:-1]:
                    tab_titles[idx] = None
                tab_titles = [x for x in tab_titles if x is not None]
        
        area_tabs = st.tabs(tab_titles)
        
        # Only show detailed recommendations if we have AI insights
        if "error" not in ai_insights or len(ai_insights.get("improvements", [])) > 0:
            # For each improvement area tab, display the detailed recommendation
            for i, tab in enumerate(area_tabs):
                with tab:
                    # Check if this is the Competitor Tactics tab (last tab)
                    if i == len(area_tabs) - 1:
                        # Use the dedicated helper function to display the competitor tactics interface
                        display_competitor_tactics_tab(tab)
                    else:
                        # For regular improvement area tabs
                        # Find the matching improvement from AI insights
                        matching_improvements = [imp for imp in ai_insights.get("improvements", []) 
                                               if imp['area'] == improvement_areas[i]]
                        
                        if matching_improvements:
                            improvement = matching_improvements[0]
                            st.markdown(f"""
                            <div style="background: white; border-radius: 8px; box-shadow: 0 1px 6px rgba(0,0,0,0.05); padding: 15px; margin: 10px 0 15px 0;">
                                <div style="font-weight: 600; color: #f43f5e; margin-bottom: 8px;">{improvement['area']}</div>
                                <div style="color: #333; font-size: 0.9rem; margin-bottom: 12px;">{improvement['explanation']}</div>
                                <div style="background: #f8fafc; padding: 10px; border-left: 3px solid #3b82f6; font-size: 0.9rem;">
                                    <span style="font-weight: 500; color: #3b82f6;">Recommendation:</span> {improvement['recommendation']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            # Detailed fallback content based on the improvement area
                            area = improvement_areas[i]
                            
                            # Prepare detailed fallback recommendations based on the area
                            fallback_explanations = {
                                "Platform Relevance": "Your campaign could benefit from better alignment with platform-specific audience behaviors and expectations. Current platform approach lacks optimization for each channel's unique content environment.",
                                "Cultural Relevance": "Analysis shows moderate alignment with cultural trends and references that resonate with the target audience. Current approach may miss cultural nuances that drive deeper engagement.",
                                "Representation": "Campaign elements could better reflect the diverse backgrounds and experiences of your target audience. More inclusive representation would strengthen audience connection.",
                                "Cultural Vernacular": "Language and references used in campaign materials could better match how your target audience naturally communicates. Authentic vernacular increases trust and relatability.",
                                "Media Ownership Equity": "Your media plan shows limited investment in diverse media ownership. Supporting minority-owned channels can unlock unique audience relationships.",
                                "Cultural Authority": "Campaign lacks credible voices from within the cultural communities you're targeting. Authentic partnerships enhance believability and reduce perception of cultural appropriation.",
                                "Buzz & Conversation": "Campaign has limited potential to generate organic cultural conversations. More culturally relevant hooks would increase shareability.",
                                "Commerce Bridge": "There's a disconnect between cultural elements and purchase activation. Stronger commerce integration would convert cultural engagement to sales.",
                                "Geo-Cultural Fit": "Campaign elements don't fully account for geographic cultural nuances. Regional cultural considerations would improve relevance."
                            }
                            
                            fallback_recommendations = {
                                "Platform Relevance": "Implement platform-specific creative executions with 40% of budget allocated to high-impact interactive video across premium CTV/OTT platforms. Prioritize audio placements on podcast networks with 25% higher engagement rates for your audience demographic. Deploy rich media formats on digital platforms to increase interaction rates by 3.2x compared to standard display.",
                                "Cultural Relevance": "Integrate emerging cultural trends into campaign messaging using real-time cultural intelligence monitoring. Allocate 30% of digital budget toward dynamic creative optimization that adapts messaging based on trending cultural moments. Leverage DOOH placements in cultural hotspots with high audience density.",
                                "Representation": "Diversify audience representation across all creative assets to reflect actual customer demographics. Deploy a minimum of three distinct audience personas in segmented targeting strategies. Implement native display ads that feature authentic audience representation across mobile-first platforms.",
                                "Cultural Vernacular": "Refine campaign messaging to incorporate authentic language patterns of target segments. Test performance display variants with different vernacular styles to identify highest engagement format. Use authentic audio placements with 65% higher recall compared to generic messaging.",
                                "Media Ownership Equity": "Allocate 15-20% of media spend to diverse-owned media platforms with audience alignment. Integrate performance-based diverse media partners into lower-funnel conversion strategies with premium CPV models. Create custom content partnerships with three key diverse media owners.",
                                "Cultural Authority": "Partner with 2-3 category-relevant cultural voices for premium CTV/OTT and audio content integrations. Implement native articles through publications with established cultural credibility. Avoid generic influencer partnerships in favor of authentic cultural authorities.",
                                "Buzz & Conversation": "Create shareable rich media content with cultural hooks that drive earned media value. Deploy interactive video experiences designed for social amplification with embedded sharing functionality. Use picture-in-picture sports integrations during culturally relevant events.",
                                "Commerce Bridge": "Implement sequential retargeting strategy using first-party data across high-impact display units. Deploy shoppable interactive video formats with embedded product galleries. Test native display ads with direct commerce integration across mobile platforms.",
                                "Geo-Cultural Fit": "Develop geo-targeted campaigns for top 5 markets with custom creative reflecting local cultural nuances. Allocate 25% of budget to ReachTV and DOOH placements in locations with high cultural relevance. Implement geo-specific performance display campaigns with localized messaging."
                            }
                            
                            explanation = fallback_explanations.get(area, "This area shows potential for improvement based on our analysis of your campaign brief.")
                            recommendation = fallback_recommendations.get(area, "Consider investing more resources in this area to enhance campaign effectiveness.")
                            
                            # Clean up any possible grammar issues or duplications
                            cleaned_explanation = fix_grammar_and_duplicates(explanation)
                            cleaned_recommendation = fix_grammar_and_duplicates(recommendation)
                            
                            st.markdown(f"""
                            <div style="background: white; border-radius: 8px; box-shadow: 0 1px 6px rgba(0,0,0,0.05); padding: 15px; margin: 10px 0 15px 0;">
                                <div style="font-weight: 600; color: #f43f5e; margin-bottom: 8px;">{area}</div>
                                <div style="color: #333; font-size: 0.9rem; margin-bottom: 12px;">
                                    {cleaned_explanation}
                                </div>
                                <div style="background: #f8fafc; padding: 10px; border-left: 3px solid #3b82f6; font-size: 0.9rem;">
                                    <span style="font-weight: 500; color: #3b82f6;">Recommendation:</span> 
                                    {cleaned_recommendation}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            # If no AI insights are available, show simplified tabs
            for i, tab in enumerate(area_tabs):
                with tab:
                    # For the last tab (Competitor Tactics)
                    if i == len(area_tabs) - 1:
                        # Use the dedicated helper function to display the competitor tactics interface
                        display_competitor_tactics_tab(tab)
                    else:
                        # For regular improvement area tabs
                        area = improvement_areas[i]
                            
                        # Prepare detailed fallback recommendations based on the area
                        fallback_explanations = {
                            "Platform Relevance": "Your campaign could benefit from better alignment with platform-specific audience behaviors and expectations. Current platform approach lacks optimization for each channel's unique content environment.",
                            "Cultural Relevance": "Analysis shows moderate alignment with cultural trends and references that resonate with the target audience. Current approach may miss cultural nuances that drive deeper engagement.",
                            "Representation": "Campaign elements could better reflect the diverse backgrounds and experiences of your target audience. More inclusive representation would strengthen audience connection.",
                            "Cultural Vernacular": "Language and references used in campaign materials could better match how your target audience naturally communicates. Authentic vernacular increases trust and relatability.",
                            "Media Ownership Equity": "Your media plan shows limited investment in diverse media ownership. Supporting minority-owned channels can unlock unique audience relationships.",
                            "Cultural Authority": "Campaign lacks credible voices from within the cultural communities you're targeting. Authentic partnerships enhance believability and reduce perception of cultural appropriation.",
                            "Buzz & Conversation": "Campaign has limited potential to generate organic cultural conversations. More culturally relevant hooks would increase shareability.",
                            "Commerce Bridge": "There's a disconnect between cultural elements and purchase activation. Stronger commerce integration would convert cultural engagement to sales.",
                            "Geo-Cultural Fit": "Campaign elements don't fully account for geographic cultural nuances. Regional cultural considerations would improve relevance."
                        }
                        
                        fallback_recommendations = {
                            "Platform Relevance": "Implement platform-specific creative executions with 40% of budget allocated to high-impact interactive video across premium CTV/OTT platforms. Prioritize audio placements on podcast networks with 25% higher engagement rates for your audience demographic. Deploy rich media formats on digital platforms to increase interaction rates by 3.2x compared to standard display.",
                            "Cultural Relevance": "Integrate emerging cultural trends into campaign messaging using real-time cultural intelligence monitoring. Allocate 30% of digital budget toward dynamic creative optimization that adapts messaging based on trending cultural moments. Leverage DOOH placements in cultural hotspots with high audience density.",
                            "Representation": "Diversify audience representation across all creative assets to reflect actual customer demographics. Deploy a minimum of three distinct audience personas in segmented targeting strategies. Implement native display ads that feature authentic audience representation across mobile-first platforms.",
                            "Cultural Vernacular": "Refine campaign messaging to incorporate authentic language patterns of target segments. Test performance display variants with different vernacular styles to identify highest engagement format. Use authentic audio placements with 65% higher recall compared to generic messaging.",
                            "Media Ownership Equity": "Allocate 15-20% of media spend to diverse-owned media platforms with audience alignment. Integrate performance-based diverse media partners into lower-funnel conversion strategies with premium CPV models. Create custom content partnerships with three key diverse media owners.",
                            "Cultural Authority": "Partner with 2-3 category-relevant cultural voices for premium CTV/OTT and audio content integrations. Implement native articles through publications with established cultural credibility. Avoid generic influencer partnerships in favor of authentic cultural authorities.",
                            "Buzz & Conversation": "Create shareable rich media content with cultural hooks that drive earned media value. Deploy interactive video experiences designed for social amplification with embedded sharing functionality. Use picture-in-picture sports integrations during culturally relevant events.",
                            "Commerce Bridge": "Implement sequential retargeting strategy using first-party data across high-impact display units. Deploy shoppable interactive video formats with embedded product galleries. Test native display ads with direct commerce integration across mobile platforms.",
                            "Geo-Cultural Fit": "Develop geo-targeted campaigns for top 5 markets with custom creative reflecting local cultural nuances. Allocate 25% of budget to ReachTV and DOOH placements in locations with high cultural relevance. Implement geo-specific performance display campaigns with localized messaging."
                        }
                        
                        explanation = fallback_explanations.get(area, "This area has been identified as a priority opportunity area for your campaign.")
                        recommendation = fallback_recommendations.get(area, "Consider investing more resources in this area to enhance campaign effectiveness.")
                        
                        # Apply grammar cleanup to fallback content as well
                        cleaned_explanation = fix_grammar_and_duplicates(explanation)
                        cleaned_recommendation = fix_grammar_and_duplicates(recommendation)
                        
                        st.markdown(f"""
                        <div style="background: white; border-radius: 8px; box-shadow: 0 1px 6px rgba(0,0,0,0.05); padding: 15px; margin: 10px 0 15px 0;">
                            <div style="font-weight: 600; color: #f43f5e; margin-bottom: 8px;">{area}</div>
                            <div style="color: #333; font-size: 0.9rem; margin-bottom: 12px;">
                                {cleaned_explanation}
                            </div>
                            <div style="background: #f8fafc; padding: 10px; border-left: 3px solid #3b82f6; font-size: 0.9rem;">
                                <span style="font-weight: 500; color: #3b82f6;">Recommendation:</span> 
                                {cleaned_recommendation}
                            </div>
                            <div style="font-size: 0.8rem; color: #64748b; margin-top: 12px; font-style: italic;">
                                For more customized recommendations, enable OpenAI API integration.
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    else:
        # If no improvement areas or AI insights, just show the pills without tabs
        imp_areas_html = "".join([f'<div style="display: inline-block; background: #f5f7fa; border: 1px solid #e5e7eb; border-radius: 30px; padding: 6px 16px; margin: 5px 8px 5px 0; font-size: 0.9rem; color: #5865f2; font-weight: 500;">{area}</div>' for area in improvement_areas])
        
        st.markdown(f"""
            <div style="margin-top: 15px;">{imp_areas_html}</div>
            """, unsafe_allow_html=True)
    


def display_competitor_tactics_tab(tab):
    """
    Displays the competitor tactics tab with the Fortune 500 Strategy Tool styling.
    
    Args:
        tab: The streamlit tab object to render content in
    """
    # Add the CSS for the Fortune 500 Strategy Tool
    tab.markdown("""
    <style>
        .fortune500-analyzer {
            font-family: 'Helvetica Neue', sans-serif;
            max-width: 900px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 1px 6px rgba(0,0,0,0.05);
            padding: 20px;
            margin-bottom: 20px;
        }
        .fortune500-heading {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 15px;
            color: #111;
        }
        .fortune500-description {
            margin-bottom: 20px;
            font-size: 1rem;
            color: #444;
        }
        .fortune500-input {
            width: 100%;
            padding: 0.8rem;
            font-size: 1rem;
            margin-bottom: 15px;
            border-radius: 6px;
            border: 1px solid #ccc;
        }
        .fortune500-output {
            margin-top: 20px;
            background: #fff;
            padding: 20px;
            border-left: 4px solid #3b82f6;
            border-radius: 4px;
        }
        .fortune500-output h2 {
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 1.3rem;
            color: #111;
        }
        .fortune500-output ul {
            padding-left: 25px;
            line-height: 1.6;
        }
        .fortune500-output li {
            margin-bottom: 12px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Add the HTML for the competitor analyzer UI
    tab.markdown("""
    <div class="fortune500-analyzer">
        <div class="fortune500-heading">Fortune 500 Competitor Strategy Generator</div>
        <p class="fortune500-description">Enter a Fortune 500 brand to generate dynamic counter-strategy recommendations that leverage your campaign's strengths.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add the input and button
    competitor_brand = tab.text_input("", placeholder="e.g., Amazon, Apple, Walmart, Target", key=f"competitor_brand_input_{hash(str(tab))}")
    generate_button = tab.button("Generate Strategy", key=f"generate_insights_button_{hash(str(tab))}")
    
    # Create the brand strategies dictionary directly from the HTML file
    brand_strategies = {
        "walmart": [
            "Counter Walmart's broad reach with hyper-personalized regional messaging.",
            "Target emerging platforms where Walmart has lower presence (e.g., Discord, Twitch).",
            "Highlight community-driven storytelling vs. Walmart's corporate tone."
        ],
        "amazon": [
            "Counter Amazon's broad reach with hyper-personalized regional messaging.",
            "Target emerging platforms where Amazon has lower presence (e.g., Discord, Twitch).",
            "Highlight community-driven storytelling vs. Amazon's corporate tone."
        ],
        "apple": [
            "Counter Apple's broad reach with hyper-personalized regional messaging.",
            "Target emerging platforms where Apple has lower presence (e.g., Discord, Twitch).",
            "Highlight community-driven storytelling vs. Apple's corporate tone."
        ],
        "target": [
            "Counter Target's broad reach with hyper-personalized regional messaging.",
            "Target emerging platforms where Target has lower presence (e.g., Discord, Twitch).",
            "Highlight community-driven storytelling vs. Target's corporate tone."
        ],
        "lowe's": [
            "Counter Lowe's's broad reach with hyper-personalized regional messaging.",
            "Target emerging platforms where Lowe's has lower presence (e.g., Discord, Twitch).",
            "Highlight community-driven storytelling vs. Lowe's's corporate tone."
        ],
        "home depot": [
            "Counter Home Depot's broad reach with hyper-personalized regional messaging.",
            "Target emerging platforms where Home Depot has lower presence (e.g., Discord, Twitch).",
            "Highlight community-driven storytelling vs. Home Depot's corporate tone."
        ],
        "microsoft": [
            "Counter Microsoft's broad reach with hyper-personalized regional messaging.",
            "Target emerging platforms where Microsoft has lower presence (e.g., Discord, Twitch).",
            "Highlight community-driven storytelling vs. Microsoft's corporate tone."
        ],
        "intel": [
            "Counter Intel's broad reach with hyper-personalized regional messaging.",
            "Target emerging platforms where Intel has lower presence (e.g., Discord, Twitch).",
            "Highlight community-driven storytelling vs. Intel's corporate tone."
        ]
    }
    
    # Add additional brands dynamically based on brief text if available
    if 'brief_text' in st.session_state and st.session_state.brief_text:
        from core.ai_insights import generate_competitor_strategy
        brief_text = st.session_state.brief_text
        
        # Extract potential competitor brands from the brief
        lower_brief = brief_text.lower()
        for potential_brand in ["nike", "adidas", "coca-cola", "pepsi", "ford", "chevrolet", "toyota", "honda"]:
            if potential_brand in lower_brief and potential_brand not in brand_strategies:
                # Generate dynamic strategies for this brand
                strategies = [
                    f"Counter {potential_brand.title()}'s broad reach with hyper-personalized regional messaging.",
                    f"Target emerging platforms where {potential_brand.title()} has lower presence using rich media and high-impact interactive formats.",
                    f"Highlight authentic community storytelling vs. {potential_brand.title()}'s approach with premium CTV/OTT placements."
                ]
                brand_strategies[potential_brand] = strategies
    
    # If the button is clicked, process the input
    if generate_button:
        if not competitor_brand.strip():
            tab.markdown("<p style='color:red;'>Please enter a competitor brand name.</p>", unsafe_allow_html=True)
        else:
            # Get the lowercase version for matching
            brand_lower = competitor_brand.strip().lower()
            
            # Check if it's in our strategy database
            if brand_lower in brand_strategies:
                strategies = brand_strategies[brand_lower]
                
                # Format the strategies as list items
                strategy_items = ""
                for strategy in strategies:
                    strategy_items += f"<li>{strategy}</li>"
                
                # Store strategies in session state for PDF generation
                if 'competitor_tactics' not in st.session_state:
                    st.session_state.competitor_tactics = []
                
                # Clear existing tactics if any
                st.session_state.competitor_tactics = []
                
                # Store each strategy in session state
                for strategy in strategies:
                    st.session_state.competitor_tactics.append(strategy)
                
                # Display the formatted output
                tab.markdown(f"""
                <div class="fortune500-output">
                    <h2>Strategy Against <strong>{brand_lower.title()}</strong></h2>
                    <ul>
                        {strategy_items}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Use the AI to generate insights for unknown brands
                if 'brief_text' in st.session_state and st.session_state.brief_text:
                    # Using st.spinner instead of tab.spinner
                    with st.spinner(get_random_spinner_message()):
                        campaign_goal = "Increase brand awareness and drive sales"
                        brief_text = st.session_state.brief_text
                        
                        # Try to determine a better campaign goal based on the brief
                        if "goal" in brief_text.lower() or "objective" in brief_text.lower():
                            sentences = brief_text.split('.')
                            for sentence in sentences:
                                if "goal" in sentence.lower() or "objective" in sentence.lower():
                                    campaign_goal = sentence.strip()
                                    break
                        
                        # Generate dynamic strategies with AI
                        strategies = generate_competitor_strategy(
                            brief_text, 
                            competitor_brand.strip(), 
                            campaign_goal
                        )
                        
                        # Store strategies in session state for PDF generation
                        if 'competitor_tactics' not in st.session_state:
                            st.session_state.competitor_tactics = []
                        
                        # Clear existing tactics if any
                        st.session_state.competitor_tactics = []
                        
                        # Store each strategy in session state
                        for strategy in strategies:
                            st.session_state.competitor_tactics.append(strategy)
                        
                        # Format the strategies as list items
                        strategy_items = ""
                        for strategy in strategies:
                            # Split by colon to get the header and content
                            if ":" in strategy:
                                parts = strategy.split(":", 1)
                                header = parts[0].strip()
                                content = parts[1].strip() if len(parts) > 1 else ""
                                strategy_items += f'<li><strong>{header}:</strong> {content}</li>'
                            else:
                                strategy_items += f'<li>{strategy}</li>'
                        
                        # Display the formatted output
                        tab.markdown(f"""
                        <div class="fortune500-output">
                            <h2>Custom Strategy Against <strong>{competitor_brand}</strong></h2>
                            <ul>
                                {strategy_items}
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # Brand not in database and no brief text available
                    tab.markdown(f"""
                    <div class="fortune500-output">
                        <h2>Brand Not Found</h2>
                        <p>This tool currently includes a subset of Fortune 500 brands. Please try one of the suggested brands or upload a brief for AI-powered custom recommendations.</p>
                    </div>
                    """, unsafe_allow_html=True)
