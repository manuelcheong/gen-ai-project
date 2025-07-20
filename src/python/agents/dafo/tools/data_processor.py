"""
Data Processing Tool for DAFO Analytics Agent

This module implements the data processing tool with validation for JSON, CSV, and text formats.
"""

import json
import csv
import io
import logging
from typing import Any, List, Dict, Union
from strands_agents.tools import tool

from ..models import ProcessedData, DataFormat
from ..config import get_config

# Configure logging
logger = logging.getLogger(__name__)

# Get configuration
DATA_CONFIG = get_config("data_processing")
ANALYSIS_CONFIG = get_config("analysis")


class DataValidationError(Exception):
    """Custom exception for data validation errors"""
    pass


class DataProcessor:
    """Data processing and validation class"""
    
    def __init__(self):
        """Initialize data processor with configuration"""
        self.max_data_size = ANALYSIS_CONFIG.get("max_data_size", 10 * 1024 * 1024)
        self.supported_formats = ANALYSIS_CONFIG.get("supported_formats", ["json", "csv", "text"])
        self.max_records = ANALYSIS_CONFIG.get("max_records", 100000)
        self.validation_rules = DATA_CONFIG.get("validation_rules", {})
    
    def validate_data(self, data: Any, format_type: str) -> List[str]:
        """
        Validate input data structure and content
        
        Args:
            data: Raw input data
            format_type: Data format identifier
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        try:
            # Check format type
            if format_type not in self.supported_formats:
                errors.append(f"Unsupported format type: {format_type}. Supported formats: {self.supported_formats}")
                return errors
            
            # Check data size
            data_str = str(data) if not isinstance(data, str) else data
            if len(data_str.encode('utf-8')) > self.max_data_size:
                errors.append(f"Data size exceeds maximum limit of {self.max_data_size} bytes")
            
            # Check if data is empty
            if not data or (isinstance(data, str) and not data.strip()):
                errors.append("Data cannot be empty")
                return errors
            
            # Format-specific validation
            if format_type == "json":
                errors.extend(self._validate_json(data))
            elif format_type == "csv":
                errors.extend(self._validate_csv(data))
            elif format_type == "text":
                errors.extend(self._validate_text(data))
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            errors.append(f"Validation failed: {str(e)}")
        
        return errors
    
    def _validate_json(self, data: Any) -> List[str]:
        """Validate JSON data format"""
        errors = []
        
        try:
            # Parse JSON if it's a string
            if isinstance(data, str):
                parsed_data = json.loads(data)
            else:
                parsed_data = data
            
            # Check if it's a valid structure (dict or list)
            if not isinstance(parsed_data, (dict, list)):
                errors.append("JSON data must be an object or array")
                return errors
            
            # If it's a list, check record count
            if isinstance(parsed_data, list):
                if len(parsed_data) > self.max_records:
                    errors.append(f"Number of records ({len(parsed_data)}) exceeds maximum limit of {self.max_records}")
                
                # Check if list is not empty and contains valid objects
                if len(parsed_data) == 0:
                    errors.append("JSON array cannot be empty")
                elif not all(isinstance(item, dict) for item in parsed_data):
                    errors.append("All items in JSON array must be objects")
            
            # If it's a dict, check for required structure
            elif isinstance(parsed_data, dict):
                if len(parsed_data) == 0:
                    errors.append("JSON object cannot be empty")
        
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            errors.append(f"JSON validation error: {str(e)}")
        
        return errors
    
    def _validate_csv(self, data: str) -> List[str]:
        """Validate CSV data format"""
        errors = []
        
        try:
            if not isinstance(data, str):
                errors.append("CSV data must be provided as a string")
                return errors
            
            # Parse CSV
            csv_reader = csv.reader(io.StringIO(data.strip()))
            rows = list(csv_reader)
            
            # Check if CSV has data
            if len(rows) == 0:
                errors.append("CSV data cannot be empty")
                return errors
            
            # Check row count
            if len(rows) > self.max_records:
                errors.append(f"Number of rows ({len(rows)}) exceeds maximum limit of {self.max_records}")
            
            # Validate minimum rows
            min_rows = self.validation_rules.get("min_rows", 1)
            if len(rows) < min_rows:
                errors.append(f"CSV must have at least {min_rows} row(s)")
            
            # Check header row (first row)
            header = rows[0] if rows else []
            if not header or all(not cell.strip() for cell in header):
                errors.append("CSV must have a valid header row")
                return errors
            
            # Check column count
            num_columns = len(header)
            min_columns = self.validation_rules.get("min_columns", 1)
            max_columns = self.validation_rules.get("max_columns", 100)
            
            if num_columns < min_columns:
                errors.append(f"CSV must have at least {min_columns} column(s)")
            if num_columns > max_columns:
                errors.append(f"CSV cannot have more than {max_columns} columns")
            
            # Check for consistent column count across rows
            for i, row in enumerate(rows[1:], start=2):
                if len(row) != num_columns:
                    errors.append(f"Row {i} has {len(row)} columns, expected {num_columns}")
                    break  # Only report first inconsistency
        
        except Exception as e:
            errors.append(f"CSV validation error: {str(e)}")
        
        return errors
    
    def _validate_text(self, data: str) -> List[str]:
        """Validate text data format"""
        errors = []
        
        try:
            if not isinstance(data, str):
                errors.append("Text data must be provided as a string")
                return errors
            
            # Check text length
            max_text_length = DATA_CONFIG.get("max_text_length", 50000)
            if len(data) > max_text_length:
                errors.append(f"Text length ({len(data)}) exceeds maximum limit of {max_text_length} characters")
            
            # Check for minimum content
            if len(data.strip()) < 10:
                errors.append("Text must contain at least 10 characters of meaningful content")
            
            # Check encoding (ensure it's valid UTF-8)
            try:
                data.encode('utf-8')
            except UnicodeEncodeError:
                errors.append("Text contains invalid UTF-8 characters")
        
        except Exception as e:
            errors.append(f"Text validation error: {str(e)}")
        
        return errors
    
    def process_data(self, data: Any, format_type: str) -> ProcessedData:
        """
        Process and structure input data for analysis
        
        Args:
            data: Raw input data
            format_type: Data format identifier
            
        Returns:
            ProcessedData object with structured data
        """
        try:
            # Validate data first
            validation_errors = self.validate_data(data, format_type)
            if validation_errors:
                raise DataValidationError(f"Data validation failed: {'; '.join(validation_errors)}")
            
            # Process based on format type
            if format_type == "json":
                return self._process_json(data)
            elif format_type == "csv":
                return self._process_csv(data)
            elif format_type == "text":
                return self._process_text(data)
            else:
                raise ValueError(f"Unsupported format type: {format_type}")
        
        except Exception as e:
            logger.error(f"Data processing error: {str(e)}")
            raise
    
    def _process_json(self, data: Any) -> ProcessedData:
        """Process JSON data"""
        # Parse JSON if it's a string
        if isinstance(data, str):
            parsed_data = json.loads(data)
        else:
            parsed_data = data
        
        # Extract metadata
        if isinstance(parsed_data, list):
            record_count = len(parsed_data)
            columns = list(parsed_data[0].keys()) if parsed_data and isinstance(parsed_data[0], dict) else []
            structured_data = {"records": parsed_data}
        else:
            record_count = 1
            columns = list(parsed_data.keys()) if isinstance(parsed_data, dict) else []
            structured_data = {"record": parsed_data}
        
        metadata = {
            "original_format": "json",
            "processing_timestamp": str(logger.handlers[0].formatter.formatTime(logger.makeRecord("", 0, "", 0, "", (), None)) if logger.handlers else ""),
            "data_structure": "array" if isinstance(parsed_data, list) else "object"
        }
        
        return ProcessedData(
            structured_data=structured_data,
            data_type="json",
            record_count=record_count,
            columns=columns,
            validation_errors=[],
            metadata=metadata
        )
    
    def _process_csv(self, data: str) -> ProcessedData:
        """Process CSV data"""
        csv_reader = csv.DictReader(io.StringIO(data.strip()))
        records = list(csv_reader)
        
        columns = csv_reader.fieldnames or []
        record_count = len(records)
        
        structured_data = {
            "records": records,
            "headers": columns
        }
        
        metadata = {
            "original_format": "csv",
            "processing_timestamp": str(logger.handlers[0].formatter.formatTime(logger.makeRecord("", 0, "", 0, "", (), None)) if logger.handlers else ""),
            "delimiter": ",",
            "encoding": "utf-8"
        }
        
        return ProcessedData(
            structured_data=structured_data,
            data_type="csv",
            record_count=record_count,
            columns=columns,
            validation_errors=[],
            metadata=metadata
        )
    
    def _process_text(self, data: str) -> ProcessedData:
        """Process text data"""
        # Split text into chunks for analysis
        chunk_size = DATA_CONFIG.get("text_chunk_size", 1000)
        chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
        
        # Extract basic text statistics
        word_count = len(data.split())
        line_count = len(data.split('\n'))
        char_count = len(data)
        
        structured_data = {
            "full_text": data,
            "chunks": chunks,
            "statistics": {
                "word_count": word_count,
                "line_count": line_count,
                "character_count": char_count
            }
        }
        
        metadata = {
            "original_format": "text",
            "processing_timestamp": str(logger.handlers[0].formatter.formatTime(logger.makeRecord("", 0, "", 0, "", (), None)) if logger.handlers else ""),
            "chunk_count": len(chunks),
            "chunk_size": chunk_size
        }
        
        return ProcessedData(
            structured_data=structured_data,
            data_type="text",
            record_count=len(chunks),
            columns=["text_chunk"],
            validation_errors=[],
            metadata=metadata
        )


# Create global instance
_data_processor = DataProcessor()


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
    try:
        # Validate data first
        validation_errors = _data_processor.validate_data(data, format_type)
        if validation_errors:
            return {
                "success": False,
                "validation_errors": validation_errors,
                "error": "Data validation failed"
            }
        
        # Process data if validation passes
        processed_data = _data_processor.process_data(data, format_type)
        return {
            "success": True,
            "processed_data": processed_data.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Data processing tool error: {str(e)}")
        return {
            "success": False,
            "error": f"Data processing failed: {str(e)}"
        }