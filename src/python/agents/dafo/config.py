"""
Configuration settings for DAFO Analytics Agent

This module contains configuration constants and settings used throughout the DAFO agent.
"""

from typing import Dict, Any

# Agent Configuration
AGENT_CONFIG = {
    "model": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "max_tokens": 4000,
    "temperature": 0.1,
    "timeout": 300  # 5 minutes
}

# Analysis Configuration
ANALYSIS_CONFIG = {
    "max_data_size": 10 * 1024 * 1024,  # 10MB
    "supported_formats": ["json", "csv", "text"],
    "max_records": 100000,
    "confidence_threshold": 0.7,
    "min_dafo_elements": 3,
    "max_dafo_elements": 5
}

# Data Processing Configuration
DATA_PROCESSING_CONFIG = {
    "csv_delimiter": ",",
    "csv_encoding": "utf-8",
    "text_chunk_size": 1000,
    "max_text_length": 50000,
    "required_columns": [],
    "validation_rules": {
        "min_rows": 1,
        "max_rows": 100000,
        "min_columns": 1,
        "max_columns": 100
    }
}

# Statistical Analysis Configuration
STATISTICAL_CONFIG = {
    "outlier_threshold": 2.0,  # Standard deviations
    "correlation_threshold": 0.5,
    "sentiment_confidence_threshold": 0.6,
    "keyword_min_frequency": 2,
    "trend_window": 30  # Days for trend analysis
}

# WebSocket Configuration
WEBSOCKET_CONFIG = {
    "progress_update_interval": 10,  # Percentage points
    "connection_timeout": 3600,  # 1 hour
    "max_message_size": 32768  # 32KB
}

# Storage Configuration
STORAGE_CONFIG = {
    "temp_data_ttl": 86400,  # 24 hours in seconds
    "analysis_result_ttl": 7776000,  # 90 days in seconds
    "s3_prefix": "dafo-analysis",
    "dynamodb_table_prefix": "dafo"
}

# Error Handling Configuration
ERROR_CONFIG = {
    "max_retries": 3,
    "retry_delay": 1.0,  # Initial delay in seconds
    "backoff_multiplier": 2.0,
    "circuit_breaker_threshold": 5,
    "circuit_breaker_timeout": 300  # 5 minutes
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "retention_days": 90
}

# Industry Context Mappings
INDUSTRY_CONTEXTS = {
    "technology": {
        "keywords": ["innovation", "digital", "automation", "efficiency", "scalability"],
        "weights": {"innovation": 1.5, "efficiency": 1.3, "scalability": 1.2}
    },
    "finance": {
        "keywords": ["revenue", "profit", "cost", "risk", "compliance", "regulation"],
        "weights": {"revenue": 1.4, "risk": 1.3, "compliance": 1.2}
    },
    "healthcare": {
        "keywords": ["patient", "quality", "safety", "compliance", "efficiency"],
        "weights": {"quality": 1.5, "safety": 1.4, "compliance": 1.3}
    },
    "retail": {
        "keywords": ["customer", "sales", "inventory", "market", "competition"],
        "weights": {"customer": 1.4, "sales": 1.3, "market": 1.2}
    },
    "manufacturing": {
        "keywords": ["production", "quality", "efficiency", "cost", "supply"],
        "weights": {"production": 1.4, "quality": 1.3, "efficiency": 1.2}
    }
}

# Default Analysis Parameters
DEFAULT_PARAMS = {
    "industry_context": None,
    "custom_keywords": [],
    "analysis_depth": "basic",
    "include_recommendations": True,
    "language": "es"  # Spanish for DAFO terminology
}


def get_config(section: str) -> Dict[str, Any]:
    """
    Get configuration for a specific section
    
    Args:
        section: Configuration section name
        
    Returns:
        Dictionary containing configuration values
    """
    config_map = {
        "agent": AGENT_CONFIG,
        "analysis": ANALYSIS_CONFIG,
        "data_processing": DATA_PROCESSING_CONFIG,
        "statistical": STATISTICAL_CONFIG,
        "websocket": WEBSOCKET_CONFIG,
        "storage": STORAGE_CONFIG,
        "error": ERROR_CONFIG,
        "logging": LOGGING_CONFIG,
        "industry": INDUSTRY_CONTEXTS,
        "defaults": DEFAULT_PARAMS
    }
    
    return config_map.get(section, {})


def get_industry_config(industry: str) -> Dict[str, Any]:
    """
    Get industry-specific configuration
    
    Args:
        industry: Industry identifier
        
    Returns:
        Dictionary containing industry-specific settings
    """
    return INDUSTRY_CONTEXTS.get(industry.lower(), {
        "keywords": [],
        "weights": {}
    })