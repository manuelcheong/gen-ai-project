"""
Base interfaces for DAFO Analytics Agent

This module defines the core interfaces and abstract base classes for the analysis pipeline.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from .models import (
    AnalysisRequest, 
    ProcessedData, 
    StatisticalResults, 
    DAFOReport,
    AnalysisSession
)


class DataProcessorInterface(ABC):
    """Interface for data processing components"""
    
    @abstractmethod
    def validate_data(self, data: Any, format_type: str) -> List[str]:
        """
        Validate input data structure and content
        
        Args:
            data: Raw input data
            format_type: Data format identifier
            
        Returns:
            List of validation error messages (empty if valid)
        """
        pass
    
    @abstractmethod
    def process_data(self, data: Any, format_type: str) -> ProcessedData:
        """
        Process and structure input data for analysis
        
        Args:
            data: Raw input data
            format_type: Data format identifier
            
        Returns:
            ProcessedData object with structured data
        """
        pass


class StatisticalAnalyzerInterface(ABC):
    """Interface for statistical analysis components"""
    
    @abstractmethod
    def analyze_quantitative_data(self, data: ProcessedData) -> Dict[str, Any]:
        """
        Perform statistical analysis on numerical data
        
        Args:
            data: Processed data object
            
        Returns:
            Dictionary containing statistical metrics
        """
        pass
    
    @abstractmethod
    def analyze_text_data(self, data: ProcessedData) -> Dict[str, Any]:
        """
        Perform text analysis including sentiment and keyword extraction
        
        Args:
            data: Processed data object
            
        Returns:
            Dictionary containing text analysis results
        """
        pass
    
    @abstractmethod
    def detect_outliers(self, data: ProcessedData) -> List[Dict[str, Any]]:
        """
        Identify outliers in the dataset
        
        Args:
            data: Processed data object
            
        Returns:
            List of outlier records with metadata
        """
        pass


class DAFOGeneratorInterface(ABC):
    """Interface for DAFO report generation components"""
    
    @abstractmethod
    def categorize_findings(self, results: StatisticalResults, context: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize analysis findings into DAFO elements
        
        Args:
            results: Statistical analysis results
            context: Industry and customization parameters
            
        Returns:
            Dictionary with categorized DAFO elements
        """
        pass
    
    @abstractmethod
    def generate_report(self, categorized_findings: Dict[str, Any], metadata: Dict[str, Any]) -> DAFOReport:
        """
        Generate complete DAFO analysis report
        
        Args:
            categorized_findings: Categorized DAFO elements
            metadata: Analysis metadata and parameters
            
        Returns:
            Complete DAFOReport object
        """
        pass


class SessionManagerInterface(ABC):
    """Interface for session management components"""
    
    @abstractmethod
    async def create_session(self, user_id: str, request: AnalysisRequest) -> AnalysisSession:
        """
        Create new analysis session
        
        Args:
            user_id: User identifier
            request: Analysis request object
            
        Returns:
            Created AnalysisSession object
        """
        pass
    
    @abstractmethod
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> AnalysisSession:
        """
        Update existing analysis session
        
        Args:
            session_id: Session identifier
            updates: Dictionary of fields to update
            
        Returns:
            Updated AnalysisSession object
        """
        pass
    
    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[AnalysisSession]:
        """
        Retrieve analysis session by ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            AnalysisSession object or None if not found
        """
        pass


class WebSocketManagerInterface(ABC):
    """Interface for WebSocket communication components"""
    
    @abstractmethod
    async def send_progress_update(self, connection_id: str, progress: int, stage: str) -> bool:
        """
        Send progress update via WebSocket
        
        Args:
            connection_id: WebSocket connection identifier
            progress: Progress percentage (0-100)
            stage: Current processing stage
            
        Returns:
            True if message sent successfully
        """
        pass
    
    @abstractmethod
    async def send_error_notification(self, connection_id: str, error_message: str, recovery_suggestions: List[str]) -> bool:
        """
        Send error notification via WebSocket
        
        Args:
            connection_id: WebSocket connection identifier
            error_message: Error description
            recovery_suggestions: List of suggested recovery actions
            
        Returns:
            True if message sent successfully
        """
        pass
    
    @abstractmethod
    async def send_completion_notification(self, connection_id: str, report: DAFOReport) -> bool:
        """
        Send analysis completion notification via WebSocket
        
        Args:
            connection_id: WebSocket connection identifier
            report: Complete DAFO analysis report
            
        Returns:
            True if message sent successfully
        """
        pass


class StorageManagerInterface(ABC):
    """Interface for data storage components"""
    
    @abstractmethod
    async def store_temporary_data(self, session_id: str, data: Any) -> str:
        """
        Store temporary data for analysis session
        
        Args:
            session_id: Session identifier
            data: Data to store temporarily
            
        Returns:
            Storage key/identifier for retrieval
        """
        pass
    
    @abstractmethod
    async def retrieve_temporary_data(self, storage_key: str) -> Any:
        """
        Retrieve temporary data by storage key
        
        Args:
            storage_key: Storage identifier
            
        Returns:
            Retrieved data object
        """
        pass
    
    @abstractmethod
    async def cleanup_temporary_data(self, session_id: str) -> bool:
        """
        Clean up temporary data for completed session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if cleanup successful
        """
        pass
    
    @abstractmethod
    async def store_analysis_result(self, report: DAFOReport) -> str:
        """
        Store completed analysis result
        
        Args:
            report: Complete DAFO analysis report
            
        Returns:
            Storage identifier for the result
        """
        pass