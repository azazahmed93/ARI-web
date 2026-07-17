import re
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

# Import AI-based industry classifier
try:
    from core.ai_insights import classify_industry, INDUSTRY_LEGACY_MAP
    AI_CLASSIFIER_AVAILABLE = True
except ImportError:
    AI_CLASSIFIER_AVAILABLE = False
    print("⚠️ AI industry classifier not available, using keyword fallback only")

# Legacy industry keywords - kept for backward compatibility and fallback
# NOTE: These are simplified keywords. The AI classifier (classify_industry) handles disambiguation
industry_keywords = {
    "Sports": ["sports", "athletic", "athlete", "championship", "tournament", "league", "stadium"],
    "Technology": ["software", "saas", "api", "cloud", "cybersecurity", "machine learning", "electronics"],
    "Fashion": ["fashion", "clothing", "apparel", "footwear", "runway", "couture", "designer"],
    "Food & Beverage": ["restaurant", "cuisine", "chef", "recipe", "food", "beverage", "dining"],
    "Beauty": ["cosmetics", "skincare", "makeup", "fragrance", "haircare", "beauty", "grooming"],
    "Automotive": ["car", "vehicle", "automobile", "dealership", "automotive", "suv", "sedan"],
    "Finance": ["bank", "investment", "insurance", "credit card", "loan", "mortgage", "fintech"],
    "Healthcare": ["hospital", "pharmaceutical", "medical device", "clinical", "doctor", "patient care"],
    "Entertainment": ["movie", "film", "television", "streaming", "music", "gaming", "esports"],
    "Home & Living": ["furniture", "home decor", "interior design", "real estate", "home appliance"],
    "Wellness": ["wellness", "fitness", "gym", "yoga", "meditation", "mindfulness", "holistic"],
    "Luxury": ["luxury", "high-end", "exclusive", "prestige", "heritage", "craftsmanship"],
    "Travel": ["travel", "hotel", "airline", "resort", "vacation", "tourism", "destination"],
    "Retail": ["retail", "ecommerce", "marketplace", "shopping", "store", "checkout"],
    "Education": ["education", "university", "school", "course", "curriculum", "student", "learning"]
}

def extract_brand_info(brief_text):
    """
    Extract brand name and industry from the campaign brief.
    Uses AI-first classification for industry detection with keyword fallback.

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

    # =====================================================================
    # AI-FIRST INDUSTRY CLASSIFICATION
    # Uses GPT-4o for accurate industry detection, falls back to keywords
    # =====================================================================
    if AI_CLASSIFIER_AVAILABLE:
        try:
            classification = classify_industry(brief_text)
            if classification and classification.get("confidence", 0) >= 0.5:
                # Use the legacy name for backward compatibility with existing code
                industry = classification.get("industry_legacy", classification.get("industry", "General"))
                print(f"🎯 Industry classified by AI: {industry} (confidence: {classification.get('confidence', 0):.2f})")
            else:
                # Low confidence - fall back to keyword matching
                print(f"⚠️ AI classification confidence too low ({classification.get('confidence', 0):.2f}), using keywords")
                industry = _extract_industry_by_keywords(text)
        except Exception as e:
            print(f"⚠️ AI classification error: {e}, falling back to keywords")
            industry = _extract_industry_by_keywords(text)
    else:
        # AI classifier not available, use keyword matching
        industry = _extract_industry_by_keywords(text)

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
            "Service": ["service", "assistance", "support", "help", "subscription"],
            "Streaming": ["streaming", "content", "show", "episode", "series", "tv+", "tv plus", "original"],
            "Wellness": ["wellness", "self-care", "holistic", "mindfulness", "meditation", "yoga"]
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


def _extract_industry_by_keywords(text):
    """
    Fallback function to extract industry using keyword matching.
    This is used when AI classification is unavailable or has low confidence.

    Args:
        text (str): Lowercase brief text

    Returns:
        str: The detected industry name
    """
    # Check for explicit industry indicators first
    industry_indicators = [
        r'industry:\s*([A-Za-z0-9\s&]+)',
        r'sector:\s*([A-Za-z0-9\s&]+)',
        r'category:\s*([A-Za-z0-9\s&]+)'
    ]

    for pattern in industry_indicators:
        matches = re.search(pattern, text)
        if matches:
            return matches.group(1).strip().title()

    # Count industry keywords in text
    industry_scores = {ind: 0 for ind in industry_keywords}
    for ind, keywords in industry_keywords.items():
        for keyword in keywords:
            # Use word boundary matching to avoid false positives
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.findall(pattern, text)
            industry_scores[ind] += len(matches)

    # Get industry with highest score
    if any(industry_scores.values()):
        return max(industry_scores.items(), key=lambda x: x[1])[0]

    return "General"

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
    
    # Industry-specific term customization (updated for 15 industries)
    industry_terms = {
        # Original 9 industries
        "Sports": ['athlete', 'athletic', 'championship', 'tournament', 'league', 'stadium',
                   'team', 'match', 'player', 'coach', 'victory', 'competition'],
        "Technology": ['innovation', 'digital', 'user', 'tech', 'interface', 'device', 'app', 'software',
                       'hardware', 'solution', 'experience', 'network', 'connection', 'smart', 'api', 'cloud'],
        "Fashion": ['style', 'trend', 'collection', 'runway', 'designer', 'sustainable', 'couture',
                    'vintage', 'streetwear', 'outfit', 'wardrobe', 'accessory', 'season', 'apparel'],
        "Food & Beverage": ['flavor', 'taste', 'ingredient', 'chef', 'recipe', 'menu', 'restaurant',
                            'quality', 'organic', 'sustainable', 'nutrition', 'delicious', 'craft', 'cuisine'],
        "Beauty": ['skincare', 'makeup', 'beauty', 'cosmetic', 'fragrance', 'formula', 'texture',
                   'ingredient', 'routine', 'natural', 'enhancing', 'complexion', 'regimen', 'haircare'],
        "Automotive": ['driver', 'vehicle', 'automobile', 'engine', 'design', 'safety',
                       'efficiency', 'car', 'suv', 'sedan', 'dealership', 'automotive'],
        "Finance": ['banking', 'investment', 'financial', 'security', 'wealth', 'budget', 'savings',
                    'credit', 'payment', 'transaction', 'digital', 'portfolio', 'account', 'fintech'],
        "Healthcare": ['hospital', 'patient', 'care', 'treatment', 'medical', 'professional',
                       'therapy', 'diagnosis', 'prevention', 'provider', 'clinic', 'pharmaceutical'],
        "Entertainment": ['audience', 'viewer', 'fan', 'artist', 'streaming', 'content', 'platform',
                          'subscription', 'experience', 'show', 'episode', 'release', 'premiere',
                          'original', 'series', 'awards', 'video', 'film', 'movie', 'gaming', 'esports',
                          'documentary', 'drama', 'comedy', 'talent', 'director', 'producer'],
        # New 6 industries
        "Home & Living": ['furniture', 'decor', 'interior', 'design', 'home', 'living', 'kitchen',
                          'bedroom', 'renovation', 'property', 'real estate', 'household', 'appliance'],
        "Wellness": ['wellness', 'fitness', 'yoga', 'meditation', 'mindfulness', 'holistic', 'self-care',
                     'balance', 'harmony', 'wellbeing', 'nutrition', 'mental health', 'relaxation'],
        "Luxury": ['luxury', 'premium', 'exclusive', 'prestige', 'heritage', 'craftsmanship', 'bespoke',
                   'elite', 'affluent', 'sophisticated', 'high-end', 'artisan'],
        "Travel": ['travel', 'hotel', 'airline', 'resort', 'vacation', 'tourism', 'destination',
                   'hospitality', 'booking', 'journey', 'adventure', 'accommodation', 'experience'],
        "Retail": ['retail', 'ecommerce', 'marketplace', 'shopping', 'store', 'checkout', 'consumer',
                   'purchase', 'inventory', 'cart', 'online store', 'shop'],
        "Education": ['education', 'university', 'school', 'course', 'curriculum', 'student', 'learning',
                      'edtech', 'certification', 'academic', 'classroom', 'teacher', 'instruction'],
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
    
    # Create a unique hash from the brief_text to seed the randomness 
    # but keep it deterministic for the same brief
    import hashlib
    brief_hash = int(hashlib.md5(brief_text.encode()).hexdigest(), 16) % 10000
    
    # Create a more dynamic multiplier system that varies based on the actual brief content
    # rather than using static industry values
    
    # First set up base multipliers influenced by the brief hash
    base_multipliers = {
        "representation": 1.2 + (brief_hash % 100) / 200,  # Range: 1.2-1.7
        "cultural": 1.1 + (brief_hash % 120) / 200,  # Range: 1.1-1.7
        "platform": 1.2 + (brief_hash % 140) / 200,  # Range: 1.2-1.9
        "vernacular": 1.2 + (brief_hash % 80) / 200,  # Range: 1.2-1.6
        "equity": 1.1 + (brief_hash % 100) / 200,  # Range: 1.1-1.6
        "authority": 1.2 + (brief_hash % 110) / 200,  # Range: 1.2-1.75
        "buzz": 1.2 + (brief_hash % 120) / 200,  # Range: 1.2-1.8
        "commerce": 1.3 + (brief_hash % 90) / 200,  # Range: 1.3-1.75
        "geo": 1.1 + (brief_hash % 80) / 200,  # Range: 1.1-1.5
    }
    
    # Now adjust these multipliers based on keyword presence in the brief
    # This ensures the scores directly reflect the brief content
    keyword_adjustments = {
        "representation": ["representation", "diversity", "inclusive", "identity"],
        "cultural": ["culture", "cultural", "relevant", "lifestyle", "trend"],
        "platform": ["platform", "social", "channel", "digital", "online"],
        "vernacular": ["voice", "language", "tone", "message", "authentic"],
        "equity": ["equity", "minority", "owned", "diverse", "representation"],
        "authority": ["expert", "authority", "credible", "trusted", "leader"],
        "buzz": ["viral", "buzz", "conversation", "trending", "engagement"],
        "commerce": ["purchase", "conversion", "consumer", "shop", "acquisition"],
        "geo": ["local", "region", "community", "area", "market"]
    }
    
    # Count how many keywords from each category appear in the brief
    # and adjust multipliers accordingly
    dynamic_multipliers = base_multipliers.copy()
    for category, keywords in keyword_adjustments.items():
        keyword_count = sum(1 for keyword in keywords if keyword in brief_text.lower())
        # Adjust multiplier: more keywords = higher multiplier (up to +0.5)
        adjustment = min(0.5, keyword_count * 0.1)
        dynamic_multipliers[category] += adjustment
    
    # Further adjust based on industry, but make it a smaller factor
    # compared to the actual brief content
    # Updated to include all 15 industries
    industry_bonus = {
        # Original 9 industries
        "Sports": {"buzz": 0.2, "cultural": 0.15, "representation": 0.1},
        "Technology": {"platform": 0.2, "commerce": 0.15, "authority": 0.1},
        "Fashion": {"cultural": 0.2, "representation": 0.15, "vernacular": 0.1},
        "Food & Beverage": {"commerce": 0.15, "geo": 0.2, "cultural": 0.1},
        "Beauty": {"representation": 0.2, "cultural": 0.15, "commerce": 0.1},
        "Automotive": {"authority": 0.15, "commerce": 0.2, "geo": 0.1},
        "Finance": {"authority": 0.2, "commerce": 0.15, "equity": 0.1},
        "Healthcare": {"authority": 0.2, "equity": 0.15, "representation": 0.1},
        "Entertainment": {"buzz": 0.2, "cultural": 0.2, "platform": 0.15},
        # New 6 industries
        "Home & Living": {"geo": 0.2, "commerce": 0.15, "cultural": 0.1},
        "Wellness": {"representation": 0.15, "cultural": 0.2, "authority": 0.1},
        "Luxury": {"authority": 0.2, "cultural": 0.15, "vernacular": 0.1},
        "Travel": {"geo": 0.2, "cultural": 0.15, "buzz": 0.1},
        "Retail": {"commerce": 0.2, "platform": 0.15, "geo": 0.1},
        "Education": {"authority": 0.2, "representation": 0.15, "equity": 0.1},
        "General": {}
    }
    
    # Apply industry bonus if industry is recognized
    if industry in industry_bonus:
        for category, bonus in industry_bonus[industry].items():
            dynamic_multipliers[category] += bonus
    
    # Use these dynamic multipliers for scoring
    multipliers = dynamic_multipliers
    
    # Use the brief_hash to create variable scores
    import random
    random.seed(brief_hash)
    
    # Helper function to create more variability in scores
    def dynamic_score(terms, base_min, base_max, industry_boost_list=None, sentiment_factor=0.0):
        """
        Calculate a dynamic score based on term occurrences and industry context.
        
        Args:
            terms (list): List of terms to look for in the brief
            base_min (float): Minimum base score for the metric
            base_max (float): Maximum base score for the metric
            industry_boost_list (list, optional): List of industries that get a boost
            sentiment_factor (float, optional): Additional sentiment adjustment
            
        Returns:
            float: The calculated score
        """
        # Base score with randomization from brief hash
        industry_bonus = 0.4 if industry in (industry_boost_list or []) else 0
        base = base_min + (random.random() * (base_max - base_min)) + industry_bonus
        
        # Calculate term score with higher sensitivity to brief content
        term_score = sum(term_counts.get(term, 0) * (1.5 + random.random()) for term in terms)
        
        # Add sentiment factor if applicable (convert to float to be safe)
        sentiment_factor = float(sentiment_factor)
        if sentiment_factor:
            term_score += sentiment_factor
        
        # More dramatic impact of content on score
        score = base + (term_score/8) * (0.8 + random.random() * 0.4)
        
        # Return score with brief-specific variation
        return score + ((brief_hash % 200) / 200 - 0.5) * 0.6
    
    # Representation score
    representation_terms = ['representation', 'diverse', 'diversity', 'inclusive', 'inclusion', 
                           'identity', 'perspective', 'voice', 'authentic']
    scores["Representation"] = min(9.8, max(5.8, dynamic_score(
        representation_terms, 
        6.3, 7.0, 
        ["Fashion", "Beauty", "Entertainment", "Sports"],
        sentiment['compound'] * 2
    )))
    
    # Cultural Relevance score
    cultural_terms = ['culture', 'relevant', 'resonance', 'trend', 'trending', 'zeitgeist',
                      'music', 'sports', 'fashion', 'lifestyle']
    scores["Cultural Relevance"] = min(9.6, max(6.0, dynamic_score(
        cultural_terms, 
        6.4, 7.3, 
        ["Fashion", "Entertainment", "Sports"],
        sentiment['pos'] * 3
    )))
    
    # Platform Relevance score
    platform_terms = ['platform', 'social media', 'channel', 'tiktok', 'instagram', 'youtube',
                      'twitter', 'facebook', 'discord', 'twitch', 'digital']
    scores["Platform Relevance"] = min(9.5, max(5.5, dynamic_score(
        platform_terms, 
        6.0, 7.0, 
        ["Technology", "Entertainment"],
        0
    )))
    
    # Cultural Vernacular score
    vernacular_terms = ['slang', 'language', 'tone', 'voice', 'messaging', 'speak', 'talk',
                         'conversation', 'dialogue', 'authentic', 'natural']
    # Add language complexity as a sentiment factor
    lang_complexity = unique_words / (word_count + 1) * 5
    scores["Cultural Vernacular"] = min(9.5, max(6.0, dynamic_score(
        vernacular_terms, 
        6.2, 7.4, 
        ["Entertainment", "Fashion"],
        lang_complexity
    )))
    
    # Media Ownership Equity score
    equity_terms = ['equity', 'ownership', 'representative', 'diverse', 'inclusive', 
                    'minority', 'owned', 'investment', 'budget', 'allocation']
    scores["Media Ownership Equity"] = min(8.8, max(5.0, dynamic_score(
        equity_terms, 
        5.3, 6.5, 
        ["Healthcare", "Finance"],
        0
    )))
    
    # Cultural Authority score
    authority_terms = ['credible', 'authentic', 'authority', 'expert', 'leader', 'influence',
                      'trustworthy', 'reliable', 'respected', 'insider']
    scores["Cultural Authority"] = min(9.6, max(6.2, dynamic_score(
        authority_terms, 
        6.4, 7.8, 
        ["Healthcare", "Finance", "Automotive"],
        sentiment['pos'] * 2
    )))
    
    # Buzz & Conversation score
    buzz_terms = ['viral', 'buzz', 'conversation', 'talk', 'discuss', 'share', 'trending',
                 'engaging', 'engagement', 'interaction', 'response', 'reaction', 'meme']
    scores["Buzz & Conversation"] = min(9.5, max(6.0, dynamic_score(
        buzz_terms, 
        6.5, 7.8, 
        ["Entertainment", "Fashion", "Sports"],
        sentiment['compound'] * 2
    )))
    
    # Commerce Bridge score - Make this especially variable based on brief content
    commerce_terms = ['commerce', 'purchase', 'buy', 'shop', 'shopping', 'transaction',
                     'conversion', 'customer', 'consumer', 'acquisition', 'funnel', 'sale']
    # Use a wider range of base scores and increased term sensitivity for commerce
    # This ensures Commerce Bridge isn't always highest
    scores["Commerce Bridge"] = min(9.6, max(5.5, dynamic_score(
        commerce_terms, 
        5.8, 7.8,  # Much wider range than before
        ["Automotive", "Finance", "Technology", "Retail"],
        0
    ) * (0.8 + (random.random() * 0.4))))
    
    # Geo-Cultural Fit score
    geo_terms = ['location', 'region', 'area', 'local', 'community', 'city', 'urban',
                'rural', 'neighborhood', 'territory', 'market', 'geographical']
    scores["Geo-Cultural Fit"] = min(9.2, max(5.5, dynamic_score(
        geo_terms, 
        6.0, 7.5, 
        ["Food & Beverage", "Healthcare", "Automotive"],
        0
    )))
    
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
    # Import the benchmark database for real-time comparisons
    from core.database import benchmark_db
    import streamlit as st
    
    # Average the scores to get an overall score
    overall_score = sum(scores.values()) / len(scores)
    
    # Get the industry from session state if available
    industry = st.session_state.get('industry', 'General')
    
    # Use the benchmark database to get the percentile based on real-time industry data
    percentile = benchmark_db.get_campaign_percentile(overall_score, industry)
    
    return percentile

def get_improvement_areas(scores, brief_text=None, brand_name=None, industry=None):
    """
    Identify the priority improvement areas: strictly the three lowest-scoring
    metrics, followed by a fixed "Competitor Tactics" entry.

    Score-driven to match the dashboard. The previous brief-keyword / industry
    weighting (which could surface a metric that was not actually among the
    lowest scorers) has been removed. brief_text / brand_name / industry are
    accepted for backward compatibility but no longer affect the selection.
    """
    if not scores:
        # Default fallback if no scores are available
        return ["Cultural Relevance", "Platform Relevance", "Buzz & Conversation", "Competitor Tactics"]

    # Strictly the three lowest-scoring metrics, ascending.
    sorted_scores = sorted(scores.items(), key=lambda x: x[1])
    improvement_areas = [area for area, _ in sorted_scores[:3]]

    # "Competitor Tactics" is always appended as a non-metric 4th entry - the UI
    # renders it as a dedicated tab (the Competitor Strategy tool), not a metric.
    improvement_areas.append("Competitor Tactics")

    return improvement_areas
