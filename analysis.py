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

def analyze_campaign_brief(brief_text):
    """
    Analyze a campaign brief text and return ARI metrics scores.
    
    This performs NLP analysis on the brief to determine scores for each
    metric in the Audience Resonance Index framework.
    
    Args:
        brief_text (str): The campaign brief text to analyze
        
    Returns:
        dict: Dictionary with scores for each ARI metric
    """
    if not brief_text or brief_text.strip() == "":
        return None
    
    # Initialize sentiment analyzer
    sia = SentimentIntensityAnalyzer()
    
    # Tokenize text
    tokens = word_tokenize(brief_text.lower())
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    # Get text features
    word_count = len(filtered_tokens)
    unique_words = len(set(filtered_tokens))
    sentiment = sia.polarity_scores(brief_text)
    
    # Check for key marketing terms
    marketing_terms = ['audience', 'target', 'demographic', 'segment', 'campaign', 'social media',
                       'platform', 'viral', 'engagement', 'conversion', 'brand', 'identity',
                       'culture', 'trend', 'community', 'influencer', 'authentic', 'voice',
                       'representation', 'diversity', 'equity', 'inclusion', 'relevance',
                       'resonance', 'buzzworthy', 'viral', 'shareability', 'commerce']
    
    term_counts = {term: brief_text.lower().count(term) for term in marketing_terms}
    
    # Calculate synthetic scores based on text features
    # This is a simplified algorithmic approach that would be replaced by a more
    # sophisticated model in a real production environment
    
    # Base scores are calculated from a combination of:
    # - Presence of relevant marketing terms
    # - Sentiment analysis
    # - Text complexity (unique word ratio)
    
    scores = {}
    
    # Representation score
    representation_terms = ['representation', 'diverse', 'diversity', 'inclusive', 'inclusion', 
                           'identity', 'perspective', 'voice', 'authentic']
    rep_score = sum(term_counts.get(term, 0) for term in representation_terms) * 1.5
    rep_score += sentiment['compound'] * 2
    scores["Representation"] = min(9.8, max(6.8, 7.5 + rep_score/10))
    
    # Cultural Relevance score
    cultural_terms = ['culture', 'relevant', 'resonance', 'trend', 'trending', 'zeitgeist',
                      'music', 'sports', 'fashion', 'lifestyle']
    cult_score = sum(term_counts.get(term, 0) for term in cultural_terms) * 1.2
    cult_score += sentiment['pos'] * 3
    scores["Cultural Relevance"] = min(9.6, max(7.0, 7.2 + cult_score/10))
    
    # Platform Relevance score
    platform_terms = ['platform', 'social media', 'channel', 'tiktok', 'instagram', 'youtube',
                      'twitter', 'facebook', 'discord', 'twitch', 'digital']
    plat_score = sum(term_counts.get(term, 0) for term in platform_terms) * 1.3
    scores["Platform Relevance"] = min(9.0, max(5.8, 6.5 + plat_score/10))
    
    # Cultural Vernacular score
    vernacular_terms = ['slang', 'language', 'tone', 'voice', 'messaging', 'speak', 'talk',
                         'conversation', 'dialogue', 'authentic', 'natural']
    vern_score = sum(term_counts.get(term, 0) for term in vernacular_terms) * 1.4
    vern_score += unique_words / (word_count + 1) * 5  # Language complexity
    scores["Cultural Vernacular"] = min(9.5, max(7.0, 7.5 + vern_score/10))
    
    # Media Ownership Equity score
    equity_terms = ['equity', 'ownership', 'representative', 'diverse', 'inclusive', 
                    'minority', 'owned', 'investment', 'budget', 'allocation']
    equity_score = sum(term_counts.get(term, 0) for term in equity_terms) * 1.5
    scores["Media Ownership Equity"] = min(8.5, max(5.5, 6.0 + equity_score/10))
    
    # Cultural Authority score
    authority_terms = ['credible', 'authentic', 'authority', 'expert', 'leader', 'influence',
                      'trustworthy', 'reliable', 'respected', 'insider']
    auth_score = sum(term_counts.get(term, 0) for term in authority_terms) * 1.4
    auth_score += sentiment['pos'] * 2
    scores["Cultural Authority"] = min(9.4, max(7.2, 8.0 + auth_score/10))
    
    # Buzz & Conversation score
    buzz_terms = ['viral', 'buzz', 'conversation', 'talk', 'discuss', 'share', 'trending',
                 'engaging', 'engagement', 'interaction', 'response', 'reaction', 'meme']
    buzz_score = sum(term_counts.get(term, 0) for term in buzz_terms) * 1.6
    buzz_score += sentiment['compound'] * 2
    scores["Buzz & Conversation"] = min(9.2, max(7.0, 7.8 + buzz_score/10))
    
    # Commerce Bridge score
    commerce_terms = ['commerce', 'purchase', 'buy', 'shop', 'shopping', 'transaction',
                     'conversion', 'customer', 'consumer', 'acquisition', 'funnel', 'sale']
    commerce_score = sum(term_counts.get(term, 0) for term in commerce_terms) * 1.5
    scores["Commerce Bridge"] = min(9.6, max(8.0, 8.5 + commerce_score/10))
    
    # Geo-Cultural Fit score
    geo_terms = ['location', 'region', 'area', 'local', 'community', 'city', 'urban',
                'rural', 'neighborhood', 'territory', 'market', 'geographical']
    geo_score = sum(term_counts.get(term, 0) for term in geo_terms) * 1.4
    scores["Geo-Cultural Fit"] = min(9.0, max(6.5, 7.4 + geo_score/10))
    
    # Round all scores to 1 decimal place
    for key in scores:
        scores[key] = round(scores[key], 1)
    
    return scores

def get_score_level(score):
    """
    Determine the level (high, medium, low) based on the score.
    
    Args:
        score (float): Score value
        
    Returns:
        str: Level descriptor
    """
    if score >= 9.0:
        return "high"
    elif score >= 7.0:
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
