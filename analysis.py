import re
import random
import numpy as np
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer

# Download NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('sentiment/vader_lexicon')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('vader_lexicon')
    nltk.download('stopwords')

# Ensure punkt_tab is downloaded
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    # Since punkt_tab might not be directly downloadable, we'll modify our code to use punkt instead
    pass

def extract_brand_info(brief_text):
    """
    Extract brand name and industry from the campaign brief.
    
    Args:
        brief_text (str): The campaign brief text to analyze
        
    Returns:
        tuple: (brand_name, industry, product_type)
    """
    text = brief_text.lower()
    
    # Common brand indicators in RFPs
    brand_indicators = [
        r'brand:\s*([A-Za-z0-9\s]+)', 
        r'client:\s*([A-Za-z0-9\s]+)',
        r'company:\s*([A-Za-z0-9\s]+)',
        r'([A-Za-z0-9\s]+)\s*campaign',
        r'([A-Za-z0-9\s]+)\s*brand',
    ]
    
    # Common industry indicators
    industry_indicators = [
        r'industry:\s*([A-Za-z0-9\s]+)',
        r'sector:\s*([A-Za-z0-9\s]+)',
        r'category:\s*([A-Za-z0-9\s]+)'
    ]
    
    # Common product type indicators
    product_indicators = [
        r'product:\s*([A-Za-z0-9\s]+)',
        r'product type:\s*([A-Za-z0-9\s]+)',
        r'offering:\s*([A-Za-z0-9\s]+)'
    ]
    
    # Default values
    brand_name = "Unknown"
    industry = "General"
    product_type = "Product"
    
    # Try to extract brand name
    for pattern in brand_indicators:
        matches = re.search(pattern, text)
        if matches:
            brand_name = matches.group(1).strip().title()
            break
    
    # If brand name still unknown, look for capitalized names that appear frequently
    if brand_name == "Unknown":
        # Find all capitalized words (potential brand names)
        words = re.findall(r'\b[A-Z][a-zA-Z]*\b', brief_text)
        word_count = {}
        for word in words:
            if len(word) > 1:  # Ignore single letters
                word_count[word] = word_count.get(word, 0) + 1
        
        # Get most frequent capitalized word
        if word_count:
            brand_name = max(word_count.items(), key=lambda x: x[1])[0]
    
    # Try to extract industry
    for pattern in industry_indicators:
        matches = re.search(pattern, text)
        if matches:
            industry = matches.group(1).strip().title()
            break
    
    # If industry still unknown, try to infer from content
    if industry == "General":
        industry_keywords = {
            "Sports": ["sports", "athletic", "fitness", "running", "training", "performance", "athleisure"],
            "Technology": ["tech", "digital", "software", "hardware", "electronics", "device", "app", "technology"],
            "Fashion": ["fashion", "clothing", "apparel", "wear", "style", "outfit", "collection", "designer"],
            "Food & Beverage": ["food", "drink", "beverage", "restaurant", "taste", "flavor", "menu", "cuisine"],
            "Beauty": ["beauty", "cosmetic", "skincare", "makeup", "fragrance", "personal care", "grooming"],
            "Automotive": ["car", "vehicle", "automotive", "drive", "driving", "model", "engine", "motor"],
            "Finance": ["bank", "finance", "credit", "loan", "payment", "wallet", "money", "financial"],
            "Healthcare": ["health", "medical", "wellness", "treatment", "patient", "clinic", "care", "therapeutic"],
            "Entertainment": ["entertainment", "movie", "music", "streaming", "game", "gaming", "artist", "show"]
        }
        
        # Count industry keywords in text
        industry_scores = {ind: 0 for ind in industry_keywords}
        for ind, keywords in industry_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    industry_scores[ind] += text.count(keyword)
        
        # Get industry with highest score
        if any(industry_scores.values()):
            industry = max(industry_scores.items(), key=lambda x: x[1])[0]
    
    # Try to extract product type
    for pattern in product_indicators:
        matches = re.search(pattern, text)
        if matches:
            product_type = matches.group(1).strip().title()
            break
    
    # If product type still unknown, try to infer from content
    if product_type == "Product":
        product_keywords = {
            "Footwear": ["shoe", "sneaker", "footwear", "boot", "trainer"],
            "Apparel": ["clothing", "apparel", "wear", "outfit", "garment", "jacket", "pants"],
            "Electronics": ["device", "gadget", "electronic", "smartphone", "laptop", "tablet"],
            "Software": ["app", "application", "software", "platform", "program", "digital"],
            "Food": ["food", "snack", "meal", "nutrition", "diet", "edible"],
            "Beverage": ["drink", "beverage", "liquid", "refreshment", "hydration"],
            "Service": ["service", "assistance", "support", "help", "subscription"]
        }
        
        # Count product keywords in text
        product_scores = {prod: 0 for prod in product_keywords}
        for prod, keywords in product_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    product_scores[prod] += text.count(keyword)
        
        # Get product with highest score
        if any(product_scores.values()):
            product_type = max(product_scores.items(), key=lambda x: x[1])[0]
    
    return brand_name, industry, product_type

def analyze_campaign_brief(brief_text):
    """
    Analyze a campaign brief text and return ARI metrics scores.
    
    This performs NLP analysis on the brief to determine scores for each
    metric in the Audience Resonance Index framework. It dynamically adapts
    to different brands and industries mentioned in the brief.
    
    Args:
        brief_text (str): The campaign brief text to analyze
        
    Returns:
        dict: Dictionary with scores for each ARI metric
    """
    if not brief_text or brief_text.strip() == "":
        return None
    
    # Extract brand information
    brand_name, industry, product_type = extract_brand_info(brief_text)
    
    # Initialize sentiment analyzer
    sia = SentimentIntensityAnalyzer()
    
    # Tokenize text - simple implementation to avoid punkt_tab dependency
    text = brief_text.lower()
    # Replace punctuation with spaces
    for punct in '.,;:!?()[]{}"\'':
        text = text.replace(punct, ' ')
    # Split on whitespace
    tokens = text.split()
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    # Get text features
    word_count = len(filtered_tokens)
    unique_words = len(set(filtered_tokens))
    sentiment = sia.polarity_scores(brief_text)
    
    # Base marketing terms
    marketing_terms = ['audience', 'target', 'demographic', 'segment', 'campaign', 'social media',
                       'platform', 'viral', 'engagement', 'conversion', 'brand', 'identity',
                       'culture', 'trend', 'community', 'influencer', 'authentic', 'voice',
                       'representation', 'diversity', 'equity', 'inclusion', 'relevance',
                       'resonance', 'buzzworthy', 'viral', 'shareability', 'commerce']
    
    # Industry-specific term customization
    industry_terms = {
        "Sports": ['athlete', 'performance', 'training', 'fitness', 'sport', 'athletic', 'competition', 
                   'team', 'match', 'game', 'player', 'coach', 'victory', 'championship'],
        "Technology": ['innovation', 'digital', 'user', 'tech', 'interface', 'device', 'app', 'software', 
                       'hardware', 'solution', 'experience', 'network', 'connection', 'smart'],
        "Fashion": ['style', 'trend', 'collection', 'runway', 'designer', 'sustainable', 'luxury', 
                    'vintage', 'streetwear', 'outfit', 'wardrobe', 'accessory', 'season'],
        "Food & Beverage": ['flavor', 'taste', 'ingredient', 'chef', 'recipe', 'menu', 'restaurant', 
                            'quality', 'organic', 'sustainable', 'nutrition', 'delicious', 'craft'],
        "Beauty": ['skincare', 'makeup', 'beauty', 'cosmetic', 'fragrance', 'formula', 'texture', 
                   'ingredient', 'routine', 'natural', 'enhancing', 'complexion', 'regimen'],
        "Automotive": ['driver', 'vehicle', 'model', 'performance', 'engine', 'design', 'safety', 
                       'efficiency', 'technology', 'driving', 'road', 'journey', 'speed'],
        "Finance": ['banking', 'investment', 'financial', 'security', 'wealth', 'budget', 'savings', 
                    'credit', 'payment', 'transaction', 'digital', 'portfolio', 'account'],
        "Healthcare": ['wellness', 'health', 'patient', 'care', 'treatment', 'medical', 'professional', 
                       'therapy', 'diagnosis', 'prevention', 'solution', 'provider', 'clinic'],
        "Entertainment": ['audience', 'viewer', 'fan', 'artist', 'streaming', 'content', 'platform', 
                          'subscription', 'experience', 'show', 'episode', 'release', 'premiere'],
        "General": ['customer', 'consumer', 'client', 'market', 'industry', 'sector', 'service', 
                    'solution', 'innovation', 'strategy', 'initiative', 'program']
    }
    
    # Add industry-specific terms to marketing terms
    if industry in industry_terms:
        marketing_terms.extend(industry_terms[industry])
    else:
        marketing_terms.extend(industry_terms["General"])
    
    # Add the brand name and product type as terms
    if brand_name != "Unknown":
        marketing_terms.append(brand_name.lower())
    if product_type != "Product":
        marketing_terms.append(product_type.lower())
    
    # Count terms in brief
    term_counts = {term: brief_text.lower().count(term) for term in marketing_terms}
    
    # Calculate synthetic scores based on text features and brand/industry context
    scores = {}
    
    # Dynamic scoring multipliers based on industry
    industry_multipliers = {
        "Sports": {
            "representation": 1.6, "cultural": 1.4, "platform": 1.3, "vernacular": 1.5,
            "equity": 1.2, "authority": 1.4, "buzz": 1.7, "commerce": 1.5, "geo": 1.3
        },
        "Technology": {
            "representation": 1.3, "cultural": 1.2, "platform": 1.7, "vernacular": 1.4,
            "equity": 1.3, "authority": 1.5, "buzz": 1.5, "commerce": 1.6, "geo": 1.2
        },
        "Fashion": {
            "representation": 1.7, "cultural": 1.8, "platform": 1.5, "vernacular": 1.6,
            "equity": 1.4, "authority": 1.3, "buzz": 1.6, "commerce": 1.5, "geo": 1.3
        },
        "Food & Beverage": {
            "representation": 1.4, "cultural": 1.5, "platform": 1.3, "vernacular": 1.4,
            "equity": 1.3, "authority": 1.4, "buzz": 1.5, "commerce": 1.6, "geo": 1.5
        },
        "Beauty": {
            "representation": 1.8, "cultural": 1.6, "platform": 1.4, "vernacular": 1.5,
            "equity": 1.5, "authority": 1.3, "buzz": 1.5, "commerce": 1.5, "geo": 1.3
        },
        "Automotive": {
            "representation": 1.3, "cultural": 1.4, "platform": 1.3, "vernacular": 1.4,
            "equity": 1.2, "authority": 1.6, "buzz": 1.4, "commerce": 1.7, "geo": 1.5
        },
        "Finance": {
            "representation": 1.2, "cultural": 1.1, "platform": 1.4, "vernacular": 1.3,
            "equity": 1.5, "authority": 1.7, "buzz": 1.2, "commerce": 1.6, "geo": 1.4
        },
        "Healthcare": {
            "representation": 1.6, "cultural": 1.3, "platform": 1.2, "vernacular": 1.4,
            "equity": 1.6, "authority": 1.7, "buzz": 1.3, "commerce": 1.4, "geo": 1.5
        },
        "Entertainment": {
            "representation": 1.7, "cultural": 1.8, "platform": 1.6, "vernacular": 1.7,
            "equity": 1.4, "authority": 1.5, "buzz": 1.8, "commerce": 1.4, "geo": 1.3
        },
        "General": {
            "representation": 1.5, "cultural": 1.4, "platform": 1.4, "vernacular": 1.4,
            "equity": 1.4, "authority": 1.4, "buzz": 1.5, "commerce": 1.5, "geo": 1.4
        }
    }
    
    # Default multipliers if industry not found
    multipliers = industry_multipliers.get(industry, industry_multipliers["General"])
    
    # Representation score
    representation_terms = ['representation', 'diverse', 'diversity', 'inclusive', 'inclusion', 
                           'identity', 'perspective', 'voice', 'authentic']
    rep_score = sum(term_counts.get(term, 0) for term in representation_terms) * multipliers["representation"]
    rep_score += sentiment['compound'] * 2
    rep_base = 7.0 if industry in ["Fashion", "Beauty", "Entertainment", "Sports"] else 6.8
    scores["Representation"] = min(9.8, max(6.5, rep_base + rep_score/10))
    
    # Cultural Relevance score
    cultural_terms = ['culture', 'relevant', 'resonance', 'trend', 'trending', 'zeitgeist',
                      'music', 'sports', 'fashion', 'lifestyle']
    cult_score = sum(term_counts.get(term, 0) for term in cultural_terms) * multipliers["cultural"]
    cult_score += sentiment['pos'] * 3
    cult_base = 7.5 if industry in ["Fashion", "Entertainment", "Sports"] else 7.0
    scores["Cultural Relevance"] = min(9.6, max(6.8, cult_base + cult_score/10))
    
    # Platform Relevance score
    platform_terms = ['platform', 'social media', 'channel', 'tiktok', 'instagram', 'youtube',
                      'twitter', 'facebook', 'discord', 'twitch', 'digital']
    plat_score = sum(term_counts.get(term, 0) for term in platform_terms) * multipliers["platform"]
    plat_base = 7.0 if industry in ["Technology", "Entertainment"] else 6.5
    scores["Platform Relevance"] = min(9.5, max(5.8, plat_base + plat_score/10))
    
    # Cultural Vernacular score
    vernacular_terms = ['slang', 'language', 'tone', 'voice', 'messaging', 'speak', 'talk',
                         'conversation', 'dialogue', 'authentic', 'natural']
    vern_score = sum(term_counts.get(term, 0) for term in vernacular_terms) * multipliers["vernacular"]
    vern_score += unique_words / (word_count + 1) * 5  # Language complexity
    vern_base = 7.8 if industry in ["Entertainment", "Fashion"] else 7.2
    scores["Cultural Vernacular"] = min(9.5, max(6.5, vern_base + vern_score/10))
    
    # Media Ownership Equity score
    equity_terms = ['equity', 'ownership', 'representative', 'diverse', 'inclusive', 
                    'minority', 'owned', 'investment', 'budget', 'allocation']
    equity_score = sum(term_counts.get(term, 0) for term in equity_terms) * multipliers["equity"]
    equity_base = 6.5 if industry in ["Healthcare", "Finance"] else 6.0
    scores["Media Ownership Equity"] = min(8.8, max(5.5, equity_base + equity_score/10))
    
    # Cultural Authority score
    authority_terms = ['credible', 'authentic', 'authority', 'expert', 'leader', 'influence',
                      'trustworthy', 'reliable', 'respected', 'insider']
    auth_score = sum(term_counts.get(term, 0) for term in authority_terms) * multipliers["authority"]
    auth_score += sentiment['pos'] * 2
    auth_base = 8.2 if industry in ["Healthcare", "Finance", "Automotive"] else 7.5
    scores["Cultural Authority"] = min(9.6, max(7.0, auth_base + auth_score/10))
    
    # Buzz & Conversation score
    buzz_terms = ['viral', 'buzz', 'conversation', 'talk', 'discuss', 'share', 'trending',
                 'engaging', 'engagement', 'interaction', 'response', 'reaction', 'meme']
    buzz_score = sum(term_counts.get(term, 0) for term in buzz_terms) * multipliers["buzz"]
    buzz_score += sentiment['compound'] * 2
    buzz_base = 8.0 if industry in ["Entertainment", "Fashion", "Sports"] else 7.2
    scores["Buzz & Conversation"] = min(9.5, max(6.8, buzz_base + buzz_score/10))
    
    # Commerce Bridge score
    commerce_terms = ['commerce', 'purchase', 'buy', 'shop', 'shopping', 'transaction',
                     'conversion', 'customer', 'consumer', 'acquisition', 'funnel', 'sale']
    commerce_score = sum(term_counts.get(term, 0) for term in commerce_terms) * multipliers["commerce"]
    commerce_base = 8.5 if industry in ["Automotive", "Finance", "Technology"] else 8.0
    scores["Commerce Bridge"] = min(9.6, max(7.5, commerce_base + commerce_score/10))
    
    # Geo-Cultural Fit score
    geo_terms = ['location', 'region', 'area', 'local', 'community', 'city', 'urban',
                'rural', 'neighborhood', 'territory', 'market', 'geographical']
    geo_score = sum(term_counts.get(term, 0) for term in geo_terms) * multipliers["geo"]
    geo_base = 7.5 if industry in ["Food & Beverage", "Healthcare", "Automotive"] else 7.0
    scores["Geo-Cultural Fit"] = min(9.2, max(6.2, geo_base + geo_score/10))
    
    # Round all scores to 1 decimal place
    for key in scores:
        scores[key] = round(scores[key], 1)
    
    return scores, brand_name, industry, product_type

def get_score_level(score):
    """
    Determine the level (high, medium, low) based on the score.
    
    Args:
        score (float): Score value
        
    Returns:
        str: Level descriptor
    """
    if score >= 8.0:
        return "high"
    elif score >= 6.0:
        return "medium"
    else:
        return "low"

def calculate_benchmark_percentile(scores):
    """
    Calculate a percentile rank for the campaign based on benchmark data.
    
    Args:
        scores (dict): Dictionary of metric scores
        
    Returns:
        float: Percentile rank for the campaign
    """
    # Average the scores to get an overall score
    overall_score = sum(scores.values()) / len(scores)
    
    # Calculate a synthetic percentile based on the overall score
    # In a real implementation, this would compare to actual benchmark data
    percentile = min(99, max(1, round((overall_score - 6.0) * 16)))
    
    return percentile

def get_improvement_areas(scores):
    """
    Identify the top areas for improvement based on the scores.
    
    Args:
        scores (dict): Dictionary of metric scores
        
    Returns:
        list: List of metrics that need improvement
    """
    # Sort the scores and get the bottom 3
    sorted_scores = sorted(scores.items(), key=lambda x: x[1])
    improvement_areas = [item[0] for item in sorted_scores[:3]]
    
    return improvement_areas
