"""
Data models for DAFO Analytics Agent

This module defines the core data structures used throughout the DAFO analysis pipeline.
"""

from datetime import datetime
from typing import List, Optional, Union, Dict, Any
from dataclasses import dataclass
from enum import Enum


class AnalysisStatus(Enum):
    """Analysis session status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class AnalysisDepth(Enum):
    """Analysis depth levels"""
    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"


class DataFormat(Enum):
    """Supported data format types"""
    JSON = "json"
    CSV = "csv"
    TEXT = "text"


@dataclass
class AnalysisRequest:
    """Request model for DAFO analysis"""
    data: Union[str, dict, list]
    format_type: DataFormat
    user_id: str
    session_id: str
    industry_context: Optional[str] = None
    custom_keywords: Optional[List[str]] = None
    analysis_depth: AnalysisDepth = AnalysisDepth.BASIC
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'data': self.data,
            'format_type': self.format_type.value,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'industry_context': self.industry_context,
            'custom_keywords': self.custom_keywords,
            'analysis_depth': self.analysis_depth.value
        }


@dataclass
class DAFOElement:
    """Individual DAFO analysis element"""
    description: str
    supporting_data: List[str]
    confidence_score: float
    category_tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'description': self.description,
            'supporting_data': self.supporting_data,
            'confidence_score': self.confidence_score,
            'category_tags': self.category_tags
        }


@dataclass
class DAFOReport:
    """Complete DAFO analysis report"""
    analysis_id: str
    timestamp: datetime
    debilidades: List[DAFOElement]  # Weaknesses
    amenazas: List[DAFOElement]     # Threats
    fortalezas: List[DAFOElement]   # Strengths
    oportunidades: List[DAFOElement]  # Opportunities
    confidence_score: float
    data_summary: Dict[str, Any]
    analysis_parameters: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'analysis_id': self.analysis_id,
            'timestamp': self.timestamp.isoformat(),
            'debilidades': [elem.to_dict() for elem in self.debilidades],
            'amenazas': [elem.to_dict() for elem in self.amenazas],
            'fortalezas': [elem.to_dict() for elem in self.fortalezas],
            'oportunidades': [elem.to_dict() for elem in self.oportunidades],
            'confidence_score': self.confidence_score,
            'data_summary': self.data_summary,
            'analysis_parameters': self.analysis_parameters
        }


@dataclass
class AnalysisSession:
    """Analysis session management model"""
    session_id: str
    user_id: str
    status: AnalysisStatus
    created_at: datetime
    updated_at: datetime
    progress_percentage: int = 0
    current_stage: str = "initialized"
    websocket_connection_id: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'progress_percentage': self.progress_percentage,
            'current_stage': self.current_stage,
            'websocket_connection_id': self.websocket_connection_id,
            'error_message': self.error_message
        }


@dataclass
class ErrorResponse:
    """Standardized error response model"""
    error_code: str
    error_message: str
    error_details: Dict[str, Any]
    recovery_suggestions: List[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'error_code': self.error_code,
            'error_message': self.error_message,
            'error_details': self.error_details,
            'recovery_suggestions': self.recovery_suggestions,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ProcessedData:
    """Model for processed and validated data"""
    structured_data: Dict[str, Any]
    data_type: str
    record_count: int
    columns: List[str]
    validation_errors: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'structured_data': self.structured_data,
            'data_type': self.data_type,
            'record_count': self.record_count,
            'columns': self.columns,
            'validation_errors': self.validation_errors,
            'metadata': self.metadata
        }


@dataclass
class StatisticalResults:
    """Model for statistical analysis results"""
    quantitative_metrics: Dict[str, Any]
    sentiment_analysis: Dict[str, Any]
    keyword_extraction: Dict[str, Any]
    outliers: List[Dict[str, Any]]
    trends: Dict[str, Any]
    correlations: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'quantitative_metrics': self.quantitative_metrics,
            'sentiment_analysis': self.sentiment_analysis,
            'keyword_extraction': self.keyword_extraction,
            'outliers': self.outliers,
            'trends': self.trends,
            'correlations': self.correlations
        }