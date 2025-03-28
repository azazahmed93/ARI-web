"""
Database connection module for real-time benchmark comparisons.
This module handles connections to campaign performance benchmarks databases.
"""

import os
import pandas as pd
import random
import hashlib

# Blocked keywords that should never appear in user-facing content
BLOCKED_KEYWORDS = [
    "The Trade Desk",
    "TradeDesk",
    "TTD",
]

class BenchmarkDatabase:
    """
    Class that handles connections to real-time benchmark databases.
    In a real implementation, this would connect to actual databases.
    """
    
    def __init__(self):
        """Initialize the benchmark database connection."""
        self.connected = True
        
    def get_vertical_benchmarks(self, industry, product_type):
        """
        Retrieve industry vertical benchmarks for comparison.
        
        Args:
            industry (str): The industry classification
            product_type (str): The product type
            
        Returns:
            dict: Benchmark data for the specified industry and product
        """
        # In a real implementation, this would query a database
        # For now, return simulated benchmark data
        
        # Create a deterministic but realistic benchmark based on industry and product
        industry_hash = int(hashlib.md5(industry.encode()).hexdigest(), 16) % 100
        product_hash = int(hashlib.md5(product_type.encode()).hexdigest(), 16) % 100
        
        # Generate industry-specific benchmark values
        benchmarks = {
            "avg_resonance_score": 7.2 + (industry_hash % 10) / 10,
            "median_representation_score": 6.8 + (product_hash % 15) / 10,
            "top_quartile_threshold": 8.3 + (industry_hash % 8) / 10,
            "bottom_quartile_threshold": 5.6 - (product_hash % 10) / 10,
            "typical_improvement_rate": 0.18 + (industry_hash % 15) / 100,
            "campaign_count": 120 + industry_hash + (product_hash % 20),
        }
        
        return benchmarks
    
    def get_campaign_percentile(self, overall_score, industry):
        """
        Calculate the percentile rank of a campaign compared to benchmark data.
        
        Args:
            overall_score (float): The overall campaign score
            industry (str): The industry for benchmark comparison
            
        Returns:
            int: Percentile rank (0-100)
        """
        # In a real implementation, this would calculate actual percentiles
        # from a database of campaigns
        
        # For now, create a realistic percentile based on the score
        base_percentile = min(int(overall_score * 10), 99)
        
        # Add industry-specific variation (deterministic based on industry name)
        industry_hash = int(hashlib.md5(industry.encode()).hexdigest(), 16) % 15
        
        # Calculate final percentile with some randomness but weighted toward the base
        percentile = min(base_percentile + industry_hash - 5, 99)
        percentile = max(percentile, 10)  # Ensure minimum percentile of 10
        
        return percentile
    
    def get_competitive_analysis(self, industry, brand_name, overall_score):
        """
        Retrieve competitive analysis data for a brand in an industry.
        
        Args:
            industry (str): Industry classification
            brand_name (str): Brand name for comparison
            overall_score (float): Overall campaign score
            
        Returns:
            dict: Competitive analysis data
        """
        # In a real implementation, this would query a competitive database
        # For now, simulate competitive analysis with realistic data
        
        # Create deterministic but realistic analysis based on inputs
        industry_hash = int(hashlib.md5(industry.encode()).hexdigest(), 16) % 100
        brand_hash = int(hashlib.md5(brand_name.encode()).hexdigest(), 16) % 100
        
        # Calculate relative position
        position = "leader" if overall_score > 8.5 else ("challenger" if overall_score > 7.5 else "follower")
        
        # Generate analysis data
        analysis = {
            "market_position": position,
            "competitive_index": round(overall_score * 10 + (industry_hash % 10) / 10, 1),
            "share_of_voice": min(industry_hash + brand_hash, 100) / 2,
            "industry_avg_performance": 6.8 + (industry_hash % 20) / 10,
            "recommendation_confidence": min(75 + (brand_hash % 25), 95)
        }
        
        return analysis

# Initialize the database connection
benchmark_db = BenchmarkDatabase()