"""
DAFO Analytics Agent

Main agent class using Strands framework for DAFO analysis.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from strands_agents import Agent
from strands_agents.tools import tool

from .models import (
    AnalysisRequest, 
    DAFOReport, 
    AnalysisSession,
    AnalysisStatus,
    ErrorResponse
)
from .interfaces import (
    DataProcessorInterface,
    StatisticalAnalyzerInterface, 
    DAFOGeneratorInterface,
    SessionManagerInterface,
    WebSocketManagerInterface,
    StorageManagerInterface
)

# Configure logging
logger = logging.getLogger(__name__)


class DAFOAgent:
    """
    Main DAFO Analytics Agent using Strands framework
    
    This agent orchestrates the complete DAFO analysis pipeline:
    1. Data processing and validation
    2. Statistical analysis
    3. DAFO categorization and report generation
    """
    
    def __init__(
        self,
        data_processor: Optional[DataProcessorInterface] = None,
        statistical_analyzer: Optional[StatisticalAnalyzerInterface] = None,
        dafo_generator: Optional[DAFOGeneratorInterface] = None,
        session_manager: Optional[SessionManagerInterface] = None,
        websocket_manager: Optional[WebSocketManagerInterface] = None,
        storage_manager: Optional[StorageManagerInterface] = None
    ):
        """
        Initialize DAFO Agent with dependency injection
        
        Args:
            data_processor: Data processing component
            statistical_analyzer: Statistical analysis component
            dafo_generator: DAFO generation component
            session_manager: Session management component
            websocket_manager: WebSocket communication component
            storage_manager: Data storage component
        """
        # Store component references for dependency injection
        self.data_processor = data_processor
        self.statistical_analyzer = statistical_analyzer
        self.dafo_generator = dafo_generator
        self.session_manager = session_manager
        self.websocket_manager = websocket_manager
        self.storage_manager = storage_manager
        
        # Initialize Strands agent with tools
        self.agent = Agent(
            model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            tools=[
                self._create_data_processor_tool(),
                self._create_statistical_analyzer_tool(),
                self._create_dafo_generator_tool()
            ],
            system_prompt=self._get_system_prompt()
        )
        
        logger.info("DAFO Agent initialized successfully")
    
    def _get_system_prompt(self) -> str:
        """
        Get specialized system prompt for DAFO analysis
        
        Returns:
            System prompt string for the agent
        """
        return """
        You are a specialized DAFO (Debilidades, Amenazas, Fortalezas, Oportunidades) analysis expert.
        
        Your role is to:
        1. Process and validate business data in various formats
        2. Perform comprehensive statistical and qualitative analysis
        3. Generate strategic insights categorized into DAFO elements
        4. Provide actionable recommendations based on data patterns
        
        Key principles:
        - Focus on business-relevant insights and strategic implications
        - Provide specific, data-backed recommendations
        - Consider industry context when available
        - Maintain objectivity while highlighting critical findings
        - Structure findings clearly into the four DAFO categories
        
        Always ensure your analysis is:
        - Data-driven and evidence-based
        - Contextually relevant to the business domain
        - Actionable and specific
        - Balanced across all DAFO categories
        """
    
    def _create_data_processor_tool(self):
        """Create data processing tool for Strands integration"""
        @tool
        def data_processor(data: str, format_type: str) -> dict:
            """
            Process and validate input data for analysis
            
            Args:
                data: Raw input data (JSON, CSV, or text)
                format_type: Data format identifier ('json', 'csv', 'text')
                
            Returns:
                dict: Processed and structured data with validation results
            """
            if not self.data_processor:
                return {"error": "Data processor not configured"}
            
            try:
                # Validate data first
                validation_errors = self.data_processor.validate_data(data, format_type)
                if validation_errors:
                    return {
                        "success": False,
                        "validation_errors": validation_errors,
                        "error": "Data validation failed"
                    }
                
                # Process data if validation passes
                processed_data = self.data_processor.process_data(data, format_type)
                return {
                    "success": True,
                    "processed_data": processed_data.to_dict()
                }
                
            except Exception as e:
                logger.error(f"Data processing error: {str(e)}")
                return {
                    "success": False,
                    "error": f"Data processing failed: {str(e)}"
                }
        
        return data_processor
    
    def _create_statistical_analyzer_tool(self):
        """Create statistical analysis tool for Strands integration"""
        @tool
        def statistical_analyzer(processed_data: dict, analysis_params: dict) -> dict:
            """
            Perform statistical analysis on processed data
            
            Args:
                processed_data: Cleaned and structured data from data processor
                analysis_params: Analysis configuration parameters
                
            Returns:
                dict: Statistical insights and metrics
            """
            if not self.statistical_analyzer:
                return {"error": "Statistical analyzer not configured"}
            
            try:
                # Convert dict back to ProcessedData object
                from .models import ProcessedData
                data_obj = ProcessedData(**processed_data)
                
                # Perform different types of analysis
                quantitative_results = self.statistical_analyzer.analyze_quantitative_data(data_obj)
                text_results = self.statistical_analyzer.analyze_text_data(data_obj)
                outliers = self.statistical_analyzer.detect_outliers(data_obj)
                
                return {
                    "success": True,
                    "quantitative_metrics": quantitative_results,
                    "text_analysis": text_results,
                    "outliers": outliers,
                    "analysis_params": analysis_params
                }
                
            except Exception as e:
                logger.error(f"Statistical analysis error: {str(e)}")
                return {
                    "success": False,
                    "error": f"Statistical analysis failed: {str(e)}"
                }
        
        return statistical_analyzer
    
    def _create_dafo_generator_tool(self):
        """Create DAFO generation tool for Strands integration"""
        @tool
        def dafo_generator(analysis_results: dict, context_params: dict) -> dict:
            """
            Generate DAFO analysis from statistical results
            
            Args:
                analysis_results: Output from statistical analysis
                context_params: Industry and customization parameters
                
            Returns:
                dict: Structured DAFO report
            """
            if not self.dafo_generator:
                return {"error": "DAFO generator not configured"}
            
            try:
                # Convert analysis results to StatisticalResults object
                from .models import StatisticalResults
                stats_obj = StatisticalResults(
                    quantitative_metrics=analysis_results.get("quantitative_metrics", {}),
                    sentiment_analysis=analysis_results.get("text_analysis", {}).get("sentiment", {}),
                    keyword_extraction=analysis_results.get("text_analysis", {}).get("keywords", {}),
                    outliers=analysis_results.get("outliers", []),
                    trends=analysis_results.get("quantitative_metrics", {}).get("trends", {}),
                    correlations=analysis_results.get("quantitative_metrics", {}).get("correlations", {})
                )
                
                # Generate DAFO categorization
                categorized_findings = self.dafo_generator.categorize_findings(stats_obj, context_params)
                
                # Generate complete report
                metadata = {
                    "analysis_id": str(uuid.uuid4()),
                    "timestamp": datetime.now(),
                    "analysis_parameters": context_params
                }
                
                report = self.dafo_generator.generate_report(categorized_findings, metadata)
                
                return {
                    "success": True,
                    "dafo_report": report.to_dict()
                }
                
            except Exception as e:
                logger.error(f"DAFO generation error: {str(e)}")
                return {
                    "success": False,
                    "error": f"DAFO generation failed: {str(e)}"
                }
        
        return dafo_generator
    
    async def analyze_data(self, request: AnalysisRequest) -> Dict[str, Any]:
        """
        Main analysis entry point
        
        Args:
            request: Analysis request with data and parameters
            
        Returns:
            Dictionary containing analysis results or error information
        """
        session = None
        
        try:
            # Create analysis session if session manager is available
            if self.session_manager:
                session = await self.session_manager.create_session(request.user_id, request)
                logger.info(f"Created analysis session: {session.session_id}")
            
            # Send initial progress update
            if self.websocket_manager and session and session.websocket_connection_id:
                await self.websocket_manager.send_progress_update(
                    session.websocket_connection_id, 0, "analysis_started"
                )
            
            # Prepare analysis context
            analysis_context = {
                "data": request.data,
                "format_type": request.format_type.value,
                "industry_context": request.industry_context,
                "custom_keywords": request.custom_keywords,
                "analysis_depth": request.analysis_depth.value
            }
            
            # Execute analysis through Strands agent
            result = await self.agent.run(
                f"Perform DAFO analysis on the provided data: {analysis_context}"
            )
            
            # Update session status if available
            if self.session_manager and session:
                await self.session_manager.update_session(
                    session.session_id,
                    {
                        "status": AnalysisStatus.COMPLETED,
                        "progress_percentage": 100,
                        "current_stage": "completed"
                    }
                )
            
            # Send completion notification
            if self.websocket_manager and session and session.websocket_connection_id:
                # Extract DAFO report from result if available
                dafo_report = result.get("dafo_report") if isinstance(result, dict) else None
                if dafo_report:
                    from .models import DAFOReport
                    report_obj = DAFOReport(**dafo_report) if isinstance(dafo_report, dict) else dafo_report
                    await self.websocket_manager.send_completion_notification(
                        session.websocket_connection_id, report_obj
                    )
            
            return {
                "success": True,
                "session_id": session.session_id if session else None,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            
            # Update session with error status
            if self.session_manager and session:
                await self.session_manager.update_session(
                    session.session_id,
                    {
                        "status": AnalysisStatus.ERROR,
                        "error_message": str(e)
                    }
                )
            
            # Send error notification
            if self.websocket_manager and session and session.websocket_connection_id:
                await self.websocket_manager.send_error_notification(
                    session.websocket_connection_id,
                    str(e),
                    ["Check data format", "Verify analysis parameters", "Try again with smaller dataset"]
                )
            
            return {
                "success": False,
                "error": str(e),
                "session_id": session.session_id if session else None
            }
    
    async def get_analysis_history(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve analysis history for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary containing user's analysis history
        """
        # This will be implemented in later tasks
        # For now, return placeholder structure
        return {
            "user_id": user_id,
            "analyses": [],
            "total_count": 0
        }
    
    async def get_analysis_report(self, analysis_id: str) -> Optional[DAFOReport]:
        """
        Retrieve specific analysis report
        
        Args:
            analysis_id: Analysis identifier
            
        Returns:
            DAFOReport object or None if not found
        """
        # This will be implemented in later tasks
        # For now, return None
        return None