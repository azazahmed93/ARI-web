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

# Expected terms per metric for critical scrutiny scoring
# Terms a strong RFP SHOULD include - absence results in penalties
EXPECTED_METRIC_TERMS = {
    "Representation": {
        "critical": ["diversity", "diverse", "inclusive", "representation"],  # -1.0 each if missing
        "important": ["community", "authentic", "multicultural", "underrepresented", "identity"],  # -0.5 each (up to 3)
        "bonus": ["intersectional", "belonging", "visibility", "equitable"]  # +0.3 if present (up to 4)
    },
    "Cultural Relevance": {
        "critical": ["culture", "cultural", "relevant", "trend"],
        "important": ["lifestyle", "music", "entertainment", "zeitgeist", "moment"],
        "bonus": ["pop culture", "cultural moment", "fandom", "movement"]
    },
    "Platform Relevance": {
        "critical": ["platform", "social", "digital", "channel"],
        "important": ["tiktok", "instagram", "youtube", "streaming", "mobile", "video"],
        "bonus": ["connected tv", "ctv", "ott", "programmatic", "podcast"]
    },
    "Cultural Vernacular": {
        "critical": ["voice", "tone", "language", "messaging"],
        "important": ["authentic", "relatable", "conversational", "natural"],
        "bonus": ["in-culture", "colloquial", "community language", "culturally fluent"]
    },
    "Media Ownership Equity": {
        "critical": ["media", "investment", "budget"],
        "important": ["diverse", "equity", "partnership", "owned"],
        "bonus": ["minority-owned", "bipoc", "community media", "diverse suppliers"]
    },
    "Cultural Authority": {
        "critical": ["credible", "authentic", "trust"],
        "important": ["expert", "leader", "influencer", "partnership", "endorsement"],
        "bonus": ["thought leader", "grassroots", "community trust", "cultural insider"]
    },
    "Buzz & Conversation": {
        "critical": ["engagement", "conversation", "social"],
        "important": ["share", "viral", "trending", "buzz", "community"],
        "bonus": ["ugc", "earned media", "social listening", "word of mouth"]
    },
    "Commerce Bridge": {
        "critical": ["purchase", "conversion", "customer"],
        "important": ["sales", "acquisition", "journey", "funnel", "action"],
        "bonus": ["path to purchase", "attribution", "roi", "direct response"]
    },
    "Geo-Cultural Fit": {
        "critical": ["market", "audience", "target"],
        "important": ["local", "regional", "community", "geographic", "location"],
        "bonus": ["hyper-local", "dma", "diaspora", "micromarket", "regional trends"]
    }
}

def calculate_metric_score_with_scrutiny(brief_text, metric_name, base_score=7.5):
    """
    Calculate metric score with critical scrutiny.
    Starts at neutral baseline, penalizes for missing expected terms.

    Args:
        brief_text: The RFP/brief content
        metric_name: One of the 9 metrics
        base_score: Starting point (default 7.5 = neutral)

    Returns:
        float: Final score (capped between 4.0 and 9.5)
    """
    text_lower = brief_text.lower()
    terms = EXPECTED_METRIC_TERMS.get(metric_name, {})

    score = base_score

    # CRITICAL terms: -0.6 penalty for EACH missing (max -2.4 for 4 missing)
    critical_terms = terms.get("critical", [])
    critical_found = sum(1 for term in critical_terms if term in text_lower)
    critical_missing = len(critical_terms) - critical_found
    score -= critical_missing * 0.6

    # IMPORTANT terms: -0.3 penalty for each missing (up to 3, max -0.9)
    important_terms = terms.get("important", [])
    important_found = sum(1 for term in important_terms if term in text_lower)
    important_missing = min(3, len(important_terms) - important_found)
    score -= important_missing * 0.3

    # BONUS for critical terms found: +0.3 each (reward specificity)
    score += critical_found * 0.3

    # BONUS for important terms found: +0.2 each (up to 3)
    important_found_capped = min(3, important_found)
    score += important_found_capped * 0.2

    # BONUS terms: +0.4 for each present (up to 3)
    bonus_terms = terms.get("bonus", [])
    bonus_found = min(3, sum(1 for term in bonus_terms if term in text_lower))
    score += bonus_found * 0.4

    # Cap score between 4.0 and 9.5
    return max(4.0, min(9.5, score))

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

    # Special case handling for Apple TV+ (before AI classification)
    if ("apple" in text) and any(tv_term in text for tv_term in ["tv+", "tv plus", "apple tv", "streaming", "original series"]):
        brand_name = "Apple"
        industry = "Entertainment"
        product_type = "Streaming"
        return brand_name, industry, product_type

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
    
    # Helper function for scrutiny-based scoring with industry adjustments
    def scrutiny_score(metric_name, base_min, base_max, industry_boost_list=None):
        """
        Calculate a scrutiny-based score that penalizes missing expected terms.

        Args:
            metric_name (str): Name of the metric (must match EXPECTED_METRIC_TERMS keys)
            base_min (float): Minimum allowed score for the metric
            base_max (float): Maximum allowed score for the metric
            industry_boost_list (list, optional): List of industries that get a small boost

        Returns:
            float: The calculated score with scrutiny penalties applied
        """
        # Start with scrutiny-based score (penalizes missing terms)
        scrutiny_base = calculate_metric_score_with_scrutiny(brief_text, metric_name)

        # Apply small industry bonus (reduced from old system: max +0.3)
        ind_bonus = 0.3 if industry in (industry_boost_list or []) else 0

        # Add small variation for natural feel (+/- 0.3)
        variation = ((brief_hash % 100) / 100 - 0.5) * 0.6

        final_score = scrutiny_base + ind_bonus + variation

        # Ensure within bounds
        return max(base_min, min(base_max, final_score))

    # Representation score - Critical scrutiny for diversity/inclusion terms
    scores["Representation"] = round(scrutiny_score(
        "Representation",
        4.0, 9.5,
        ["Fashion", "Beauty", "Entertainment", "Sports"]
    ), 1)

    # Cultural Relevance score - Critical scrutiny for culture/trend terms
    scores["Cultural Relevance"] = round(scrutiny_score(
        "Cultural Relevance",
        4.0, 9.5,
        ["Fashion", "Entertainment", "Sports"]
    ), 1)

    # Platform Relevance score - Critical scrutiny for platform/digital terms
    scores["Platform Relevance"] = round(scrutiny_score(
        "Platform Relevance",
        4.0, 9.5,
        ["Technology", "Entertainment"]
    ), 1)

    # Cultural Vernacular score - Critical scrutiny for voice/language terms
    scores["Cultural Vernacular"] = round(scrutiny_score(
        "Cultural Vernacular",
        4.0, 9.5,
        ["Entertainment", "Fashion"]
    ), 1)

    # Media Ownership Equity score - Critical scrutiny for media/investment terms
    scores["Media Ownership Equity"] = round(scrutiny_score(
        "Media Ownership Equity",
        4.0, 9.0,
        ["Healthcare", "Finance"]
    ), 1)

    # Cultural Authority score - Critical scrutiny for credibility/trust terms
    scores["Cultural Authority"] = round(scrutiny_score(
        "Cultural Authority",
        4.0, 9.5,
        ["Healthcare", "Finance", "Automotive"]
    ), 1)

    # Buzz & Conversation score - Critical scrutiny for engagement/social terms
    scores["Buzz & Conversation"] = round(scrutiny_score(
        "Buzz & Conversation",
        4.0, 9.5,
        ["Entertainment", "Fashion", "Sports"]
    ), 1)

    # Commerce Bridge score - Critical scrutiny for purchase/conversion terms
    scores["Commerce Bridge"] = round(scrutiny_score(
        "Commerce Bridge",
        4.0, 9.5,
        ["Automotive", "Finance", "Technology", "Retail"]
    ), 1)

    # Geo-Cultural Fit score - Critical scrutiny for market/location terms
    scores["Geo-Cultural Fit"] = round(scrutiny_score(
        "Geo-Cultural Fit",
        4.0, 9.2,
        ["Food & Beverage", "Healthcare", "Automotive", "Travel"]
    ), 1)
    
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
    Identify the top areas for improvement based on the scores and brief content.
    
    This enhanced function considers not just the raw scores but also keywords and
    themes in the brief text to better prioritize improvement areas that will have
    the most impact for this specific campaign.
    
    The function now guarantees that the lowest scoring metric (key_opportunity) is 
    always included as the first improvement area to ensure consistency with the 
    executive summary.
    
    Args:
        scores (dict): Dictionary of metric scores
        brief_text (str, optional): The campaign brief text to analyze for keywords
        brand_name (str, optional): Brand name for context-specific improvements
        industry (str, optional): Industry for sector-specific improvements
        
    Returns:
        list: List of metrics that need improvement, prioritized by impact
    """
    # Ensure we have scores to work with
    if not scores:
        # Default fallback if no scores are available
        return ["Cultural Relevance", "Platform Relevance", "Buzz & Conversation", "Competitor Tactics"]
    
    # First get the bottom scores (initial candidates for improvement)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1])
    
    # Get the lowest scoring metric - this will always be included as the first improvement area
    # This ensures the key_opportunity in the executive summary is always included in improvement areas
    key_opportunity = sorted_scores[0][0] if sorted_scores else "Platform Relevance"
    
    # Take more candidates to filter from
    candidate_areas = sorted_scores[:5]  
    
    # Initialize improvement areas list with key_opportunity as first element
    improvement_areas = [key_opportunity]
    
    # Keywords that indicate importance of specific metrics
    importance_keywords = {
        "Platform Relevance": ["platform", "channel", "tiktok", "instagram", "social", "digital", "mobile"],
        "Cultural Relevance": ["culture", "trend", "music", "fashion", "lifestyle", "generation"],
        "Representation": ["diversity", "inclusive", "representation", "community", "minority"],
        "Cultural Vernacular": ["language", "slang", "authentic", "voice", "speak", "tone", "vernacular"],
        "Media Ownership Equity": ["diverse media", "minority owned", "equity", "representation", "ownership"],
        "Cultural Authority": ["authority", "expert", "influencer", "authentic voice", "credibility"],
        "Buzz & Conversation": ["viral", "share", "engagement", "conversation", "buzz", "talk"],
        "Commerce Bridge": ["conversion", "purchase", "buy", "sale", "revenue", "attribution"],
        "Geo-Cultural Fit": ["local", "regional", "geographic", "location", "community"]
    }
    
    # If we have brief text, use it to prioritize improvement areas
    if brief_text:
        brief_lower = brief_text.lower()
        
        # Calculate priority scores based on keyword mentions
        priority_scores = {}
        for area, keywords in importance_keywords.items():
            if area != key_opportunity:  # Skip key_opportunity as it's already included
                # Count keyword mentions in the brief
                mention_count = sum(1 for keyword in keywords if keyword.lower() in brief_lower)
                # Adjust score based on mentions (more mentions means higher priority)
                priority_scores[area] = mention_count * 2
        
        # Adjust priorities based on industry if available
        if industry:
            industry_lower = industry.lower()
            # Industry-specific adjustments
            if "retail" in industry_lower and "Commerce Bridge" != key_opportunity:
                priority_scores["Commerce Bridge"] = priority_scores.get("Commerce Bridge", 0) + 3
            elif "technology" in industry_lower and "Platform Relevance" != key_opportunity:
                priority_scores["Platform Relevance"] = priority_scores.get("Platform Relevance", 0) + 3
            elif ("fashion" in industry_lower or "beauty" in industry_lower):
                if "Cultural Relevance" != key_opportunity:
                    priority_scores["Cultural Relevance"] = priority_scores.get("Cultural Relevance", 0) + 3
                if "Buzz & Conversation" != key_opportunity:
                    priority_scores["Buzz & Conversation"] = priority_scores.get("Buzz & Conversation", 0) + 2
        
        # Adjust scores based on the original ARI scores
        for area, score in scores.items():
            if area != key_opportunity:  # Skip key_opportunity as it's already included
                # Inverse relationship - lower scores get higher priority
                priority_scores[area] = priority_scores.get(area, 0) + (10 - score) * 1.5
        
        # Get the next 2 priority areas based on combined factors (since key_opportunity is already added)
        sorted_priorities = sorted(priority_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Add top 2 priorities that aren't already in improvement_areas
        for area, _ in sorted_priorities:
            if area not in improvement_areas:
                improvement_areas.append(area)
                if len(improvement_areas) >= 3:  # We want exactly 3 metrics
                    break
    else:
        # Fallback to simple score-based improvement areas if no brief text
        # Start from the second lowest as the lowest is already included
        for area, _ in sorted_scores[1:]:  
            if area not in improvement_areas:
                improvement_areas.append(area)
                if len(improvement_areas) >= 3:  # We want exactly 3 metrics
                    break
    
    # Ensure we have exactly 3 improvement areas
    while len(improvement_areas) < 3:
        # Add missing areas from the lowest scores
        for area, _ in candidate_areas:
            if area not in improvement_areas:
                improvement_areas.append(area)
                break
    
    # If we somehow have more than 3, trim
    improvement_areas = improvement_areas[:3]
    
    # Always add "Competitor Tactics" as the 4th item
    improvement_areas.append("Competitor Tactics")
    
    return improvement_areas
