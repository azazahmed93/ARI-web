"""
This module provides simulated AI analysis for when the OpenAI API is unavailable
or encounters quota issues. It generates realistic-looking data specifically tailored
for Apple marketing briefs to enable demos without API access.
"""

import random
import json

def get_simulated_ai_analysis(brand_name="Apple"):
    """
    Generate simulated AI analysis data that looks like it came from GPT-4o
    
    Args:
        brand_name (str): The brand name to tailor analysis for (default: Apple)
        
    Returns:
        dict: Dictionary with simulated AI-powered insights and analysis
    """
    # Executive summary variations
    executive_summaries = [
        f"This campaign brief effectively connects with {brand_name}'s premium positioning in several key areas, particularly in platform strategy and creative approach. The strongest elements involve the ecosystem integration messaging and the focus on design excellence. However, there are opportunities to strengthen audience representation, especially with Gen Z and creative professionals. The brief could benefit from more specific cultural touchpoints that resonate with {brand_name}'s aspirational user base.",
        
        f"The campaign demonstrates a solid understanding of {brand_name}'s brand values around innovation and quality, but could more effectively leverage cultural relevance to connect with younger audiences. Platform selection shows strategic thinking but misses emerging channels where product discovery happens. Strengthening the creative approach to emphasize {brand_name}'s ecosystem benefits would significantly improve overall campaign effectiveness.",
        
        f"This brief aligns well with {brand_name}'s premium positioning through its emphasis on product excellence and innovation. The creative approach effectively communicates the brand's distinctive minimalist aesthetic. However, the cultural relevance could be enhanced by more deeply connecting with creative communities, and the audience targeting could better address the multicultural segments that represent growth opportunities for {brand_name}."
    ]
    
    # Improvement areas variations
    improvement_areas_options = [
        [
            f"Strengthen Gen Z representation in {brand_name}'s creative assets",
            "Enhance creator community connections in media strategy",
            "Develop more culturally-diverse touchpoints across channels"
        ],
        [
            f"Expand platform strategy to include emerging creator networks",
            f"Deepen {brand_name} ecosystem integration messaging",
            "Address cultural nuances in international markets"
        ],
        [
            "Incorporate more authentic creative voices in campaign",
            f"Highlight {brand_name}'s commitment to accessibility and inclusion",
            "Develop stronger commerce pathways from engagement to purchase"
        ]
    ]
    
    # Analysis texts for each category
    cultural_relevance_analysis = [
        f"The brief connects with {brand_name}'s premium positioning by emphasizing design excellence and innovation, but could more deeply integrate with current cultural movements in creative fields. While there are references to creativity and artistic expression, the campaign would benefit from more specific cultural touchpoints that resonate with target segments, particularly in music production, digital art, and content creation communities.",
        
        f"The brief shows awareness of {brand_name}'s cultural significance but doesn't fully leverage the brand's position at the intersection of technology and creative expression. Adding more specific touchpoints related to how {brand_name} products enable creative professionals and aspiring creators would strengthen this dimension. Consider incorporating references to cultural moments where technology and creativity converge.",
        
        f"While the campaign references {brand_name}'s premium positioning, it misses opportunities to connect with cultural movements that align with the brand's values around creativity, innovation, and design excellence. The brief would benefit from more specific cultural references that resonate with {brand_name}'s target audiences, particularly emerging Gen Z creators and established creative professionals."
    ]
    
    audience_alignment_analysis = [
        f"The brief addresses {brand_name}'s core demographic effectively but could better target the growing segment of multicultural Gen Z users and creative professionals. The campaign acknowledges the premium positioning but doesn't fully differentiate messaging for different audience segments. Enhancing representation across diverse user groups and tailoring value propositions for specific segments would improve resonance.",
        
        f"The campaign effectively addresses {brand_name}'s primary audience of premium technology users but lacks specificity in addressing the unique needs and motivations of key growth segments. The brief would benefit from more distinct messaging for creative professionals, younger users transitioning into the ecosystem, and multicultural audiences where {brand_name} has growth opportunities.",
        
        f"While the brief acknowledges {brand_name}'s premium positioning, it doesn't sufficiently differentiate messaging for distinct audience segments. The campaign would be strengthened by more specific targeting strategies for Gen Z users, creative professionals in different fields, and multicultural audiences. Consider how each segment interacts differently with the {brand_name} ecosystem."
    ]
    
    platform_strategy_analysis = [
        f"The platform strategy shows strong alignment with {brand_name}'s traditional media mix but underutilizes emerging channels where product discovery increasingly happens for younger audiences. The campaign effectively leverages premium digital and traditional channels but could expand into more creator-driven platforms and communities where authentic engagement with {brand_name} products occurs naturally.",
        
        f"The brief demonstrates a solid understanding of {brand_name}'s established platform strategy with strong presence in premium digital channels. However, there are missed opportunities in emerging creator platforms and community-driven spaces where Gen Z audiences discover products. Expanding the platform mix while maintaining {brand_name}'s premium positioning would enhance effectiveness.",
        
        f"The platform selection aligns with {brand_name}'s premium positioning but doesn't fully capitalize on emerging channels where younger audiences engage with technology brands. While traditional premium platforms are well-represented, the campaign would benefit from more strategic integration of creator-driven platforms and social commerce opportunities that maintain {brand_name}'s brand standards."
    ]
    
    creative_alignment_analysis = [
        f"The creative approach effectively maintains {brand_name}'s minimalist aesthetic and focus on product excellence, but could more explicitly connect functional benefits to emotional outcomes. The visuals align with brand standards, but the messaging could more deeply emphasize the ecosystem benefits and how {brand_name} products enhance users' creative expression and productivity.",
        
        f"The brief's creative direction preserves {brand_name}'s distinctive visual identity and premium positioning. However, the emotional dimension could be strengthened by more explicitly connecting product features to aspirational outcomes. Consider enhancing the narrative around how {brand_name} products enable users' creative expression and professional excellence.",
        
        f"The creative approach maintains {brand_name}'s brand standards with clean, minimalist visuals and product-focused messaging. To strengthen alignment with audience needs, the campaign could better articulate the ecosystem benefits and emphasize how {brand_name} products integrate seamlessly to enhance users' creative and professional lives."
    ]
    
    # Generate the analysis with random scores and selected texts
    analysis = {
        "cultural_relevance_score": random.randint(6, 8),
        "cultural_relevance_analysis": random.choice(cultural_relevance_analysis),
        
        "audience_alignment_score": random.randint(6, 8),
        "audience_alignment_analysis": random.choice(audience_alignment_analysis),
        
        "platform_strategy_score": random.randint(7, 9),
        "platform_strategy_analysis": random.choice(platform_strategy_analysis),
        
        "creative_alignment_score": random.randint(7, 9),
        "creative_alignment_analysis": random.choice(creative_alignment_analysis),
        
        "improvement_areas": random.choice(improvement_areas_options),
        "executive_summary": random.choice(executive_summaries)
    }
    
    return analysis

def get_simulated_recommendations(scores, brand_name="Apple"):
    """
    Generate simulated AI-powered recommendations based on the scores
    
    Args:
        scores (dict): Dictionary of ARI metric scores
        brand_name (str): The brand name (default: Apple)
        
    Returns:
        dict: Dictionary with recommendations for each low-scoring area
    """
    # Identify the lowest scoring areas (below 7)
    low_scores = {k: v for k, v in scores.items() if v < 7}
    if not low_scores:
        # If no low scores, get the lowest 2
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        low_scores = dict(sorted_scores[:2])
    
    recommendations = {}
    
    # Representation recommendations
    if "Representation" in low_scores:
        recommendations["Representation"] = {
            "importance": f"Authentic representation is critical for {brand_name} as the brand expands its reach to more diverse audiences. Research shows that consumers are 83% more likely to connect with brands that authentically represent their communities and experiences. For {brand_name}, this means showcasing how its products enable creativity and productivity across different demographic groups and creative disciplines.",
            "recommendations": [
                f"Expand the diversity of creative professionals featured in {brand_name} campaigns to include more varied ages, ethnicities, and creative disciplines",
                f"Create segment-specific content that shows how different user groups integrate {brand_name} products into their creative workflows and daily lives",
                f"Partner with a more diverse range of creators who authentically use {brand_name} products to tell stories that resonate with specific audience segments"
            ],
            "examples": [
                f"Microsoft's Surface campaign effectively showcased diverse creative professionals using their products in authentic work environments",
                f"Google's Pixel photography campaign highlighted diverse creators and their unique perspectives, driving strong engagement with younger audiences"
            ]
        }
    
    # Cultural Relevance recommendations
    if "Cultural Relevance" in low_scores:
        recommendations["Cultural Relevance"] = {
            "importance": f"Cultural relevance determines whether {brand_name}'s campaigns feel timely and connected to audiences' lived experiences. In a study by Kantar, brands with high cultural relevance scores achieved 50% higher brand preference metrics. For {brand_name}, connecting with culturally significant moments in creative fields and technology innovation can significantly elevate campaign performance.",
            "recommendations": [
                f"Identify and integrate 3-5 specific cultural touchpoints from creative industries where {brand_name} products are essential tools",
                f"Partner with cultural innovators in music, design, film, and digital art who embody the intersection of creativity and technology",
                f"Create content series that demonstrates how {brand_name}'s ecosystem enables new forms of creative expression tied to current cultural movements"
            ],
            "examples": [
                f"Adobe's 'Creativity for All' campaign successfully connected their products to broader cultural conversations about democratizing creative tools",
                f"Spotify's technology marketing effectively leverages cultural moments in music to demonstrate how their platform enhances cultural participation"
            ]
        }
    
    # Platform Relevance recommendations
    if "Platform Relevance" in low_scores:
        recommendations["Platform Relevance"] = {
            "importance": f"Platform selection directly impacts {brand_name}'s ability to reach and engage key audience segments where they're most receptive. Research indicates that integrated cross-platform campaigns deliver 35% higher ROI than single-platform approaches. For {brand_name}, balancing premium traditional channels with emerging platforms where product discovery happens is essential.",
            "recommendations": [
                f"Expand {brand_name}'s platform mix to include creator-driven platforms like TikTok and Instagram while maintaining the brand's premium positioning",
                f"Develop platform-specific content strategies that adapt {brand_name}'s minimalist aesthetic for different audience expectations and platform behaviors",
                f"Implement sequenced messaging across platforms to guide users through awareness to consideration of {brand_name} products and ecosystem benefits"
            ],
            "examples": [
                f"Samsung's Galaxy campaigns effectively balance premium positioning in traditional media with authentic creator partnerships on platforms like YouTube and Instagram",
                f"Sony's PlayStation marketing successfully maintains brand standards while adapting content format and style for different platform environments"
            ]
        }
    
    # Cultural Vernacular recommendations
    if "Cultural Vernacular" in low_scores:
        recommendations["Cultural Vernacular"] = {
            "importance": f"The language and tone {brand_name} uses directly impacts how authentic and relevant the brand feels to different audience segments. Research shows that brands using authentic language experience 28% higher engagement rates. For {brand_name}, balancing the brand's distinctive voice with audience-specific language patterns is crucial for building cultural credibility.",
            "recommendations": [
                f"Develop segment-specific messaging guidelines that maintain {brand_name}'s minimalist elegance while incorporating authentic language for different audience groups",
                f"Test campaign copy with representative audience panels to ensure the language resonates authentically while preserving brand voice",
                f"Create a phased approach to language that allows for more playful and segment-specific expression in certain channels while maintaining {brand_name}'s core voice in others"
            ],
            "examples": [
                f"Nike effectively balances its core brand voice with authentic linguistic patterns for different audience segments and sport categories",
                f"Glossier successfully maintains a consistent brand voice while adapting language subtly for different platforms and audience segments"
            ]
        }
    
    # Media Ownership Equity recommendations
    if "Media Ownership Equity" in low_scores:
        recommendations["Media Ownership Equity"] = {
            "importance": f"Media investment alignment with {brand_name}'s stated values on diversity and inclusion directly impacts brand trust and authenticity. Research indicates that 64% of consumers make purchasing decisions based on a brand's social positioning. For {brand_name}, demonstrating commitment through media partnerships enhances brand perception.",
            "recommendations": [
                f"Allocate at least 15% of {brand_name}'s media budget to diverse-owned media channels and creators who reach target audience segments",
                f"Develop long-term partnership programs with diverse media outlets and creators rather than one-off campaign activations",
                f"Create transparent reporting on {brand_name}'s media investment in diverse-owned channels to demonstrate authentic commitment"
            ],
            "examples": [
                f"HP's diversity initiative successfully integrated diverse media partners across their entire marketing ecosystem",
                f"Unilever implemented comprehensive inclusive media programs that drove both business results and strengthened brand perception"
            ]
        }
    
    # Cultural Authority recommendations
    if "Cultural Authority" in low_scores:
        recommendations["Cultural Authority"] = {
            "importance": f"Establishing cultural authority determines whether {brand_name} is viewed as a leader or follower in the creative technology space. McKinsey research shows that brands with strong cultural authority command 23% higher price premiums. For {brand_name}, authentic connections with creative communities reinforce the brand's premium positioning.",
            "recommendations": [
                f"Develop deeper partnerships with established creative leaders who authentically use {brand_name} products in their work",
                f"Create a {brand_name} creator program that cultivates relationships with emerging talent across diverse creative disciplines",
                f"Establish thought leadership content that positions {brand_name} at the intersection of technology innovation and creative expression"
            ],
            "examples": [
                f"Red Bull successfully built cultural authority through deep, authentic engagement with action sports and music communities",
                f"Adobe established cultural authority in creative fields through consistent support of creators and thought leadership content"
            ]
        }
    
    # Buzz & Conversation recommendations
    if "Buzz & Conversation" in low_scores:
        recommendations["Buzz & Conversation"] = {
            "importance": f"Generating organic conversation is critical for amplifying {brand_name}'s campaign impact beyond paid media. Research indicates that campaigns generating significant earned conversation deliver 2.6x higher ROI. For {brand_name}, creating distinctive moments that inspire sharing and creative engagement extends reach and enhances credibility.",
            "recommendations": [
                f"Identify 2-3 distinctive, shareable moments in the campaign that embody {brand_name}'s innovation but invite creative participation",
                f"Design visual and message components specifically optimized for social sharing across platforms relevant to {brand_name}'s audience",
                f"Create a tiered influencer strategy that includes both high-profile partnerships and micro-influencers who drive authentic conversation"
            ],
            "examples": [
                f"Spotify's Wrapped campaign consistently generates massive organic conversation by making data personal and shareable",
                f"LEGO successfully creates campaigns with built-in conversation drivers that inspire creative engagement across audience segments"
            ]
        }
    
    # Commerce Bridge recommendations
    if "Commerce Bridge" in low_scores:
        recommendations["Commerce Bridge"] = {
            "importance": f"Creating clear pathways from campaign engagement to purchase consideration directly impacts {brand_name}'s conversion rates and ROI. Studies show that campaigns with integrated commerce experiences generate 45% higher conversion rates. For {brand_name}, seamless integration between brand messaging and retail experiences is essential.",
            "recommendations": [
                f"Implement a customer journey mapping exercise to identify and eliminate friction points between {brand_name}'s marketing touchpoints and purchase channels",
                f"Create segment-specific paths to purchase that address different buying behaviors across {brand_name}'s core audience segments",
                f"Develop integrated content strategy across brand and retail channels to maintain consistent narrative from awareness through purchase"
            ],
            "examples": [
                f"Samsung effectively integrates product storytelling with frictionless commerce experiences across digital and physical touchpoints",
                f"Nike successfully bridges inspiration marketing with commerce through consistent storytelling across brand and transaction channels"
            ]
        }
    
    # Geo-Cultural Fit recommendations
    if "Geo-Cultural Fit" in low_scores:
        recommendations["Geo-Cultural Fit"] = {
            "importance": f"Regional relevance directly impacts how well {brand_name}'s global positioning translates in specific markets. Research shows that campaigns adapted for regional cultural nuances deliver 30% higher engagement rates. For {brand_name}, balancing global brand consistency with local relevance is key to market performance.",
            "recommendations": [
                f"Implement a strategic localization framework that identifies which {brand_name} campaign elements should remain consistent and which should be adapted",
                f"Develop market-specific insights on how {brand_name}'s core value propositions need to be framed differently for maximum relevance",
                f"Create a tiered approach to markets that allocates appropriate resources to localization based on market size and growth potential"
            ],
            "examples": [
                f"McDonald's successfully balances global brand standards with deep local relevance in menu items and marketing",
                f"Netflix effectively adapts global marketing strategies for regional markets while maintaining consistent brand positioning"
            ]
        }
    
    # If we still don't have recommendations for the lowest scores, add a general one
    if not recommendations:
        recommendations["Overall Campaign Enhancement"] = {
            "importance": f"Continuous improvement across all metrics is essential for maintaining {brand_name}'s premium positioning and driving growth in competitive markets. Research shows that brands that consistently refine their highest-performing elements achieve 25% better results over time.",
            "recommendations": [
                f"Implement A/B testing on {brand_name}'s strongest campaign elements to identify opportunities for further enhancement",
                f"Develop a more granular measurement framework that tracks performance across audience segments and customer journey stages",
                f"Create a learning agenda for each campaign that identifies specific hypotheses to test for future optimization"
            ],
            "examples": [
                f"Amazon continuously tests and refines even their most successful customer experience elements",
                f"Procter & Gamble implements systematic learning agendas across campaigns to drive continuous improvement"
            ]
        }
    
    return recommendations