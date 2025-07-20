"""
Unit tests for DAFO Data Processing Tool

This module contains comprehensive tests for data processing with various input formats.
"""

import json
import pytest
import unittest
from unittest.mock import patch, MagicMock

from .data_processor import DataProcessor, data_processor, DataValidationError
from ..models import ProcessedData


class TestDataProcessor(unittest.TestCase):
    """Test cases for DataProcessor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = DataProcessor()
    
    def test_init(self):
        """Test DataProcessor initialization"""
        self.assertIsInstance(self.processor.max_data_size, int)
        self.assertIsInstance(self.processor.supported_formats, list)
        self.assertIn("json", self.processor.supported_formats)
        self.assertIn("csv", self.processor.supported_formats)
        self.assertIn("text", self.processor.supported_formats)
    
    # JSON Validation Tests
    def test_validate_json_valid_object(self):
        """Test validation of valid JSON object"""
        data = '{"name": "test", "value": 123}'
        errors = self.processor.validate_data(data, "json")
        self.assertEqual(errors, [])
    
    def test_validate_json_valid_array(self):
        """Test validation of valid JSON array"""
        data = '[{"name": "test1", "value": 123}, {"name": "test2", "value": 456}]'
        errors = self.processor.validate_data(data, "json")
        self.assertEqual(errors, [])
    
    def test_validate_json_invalid_format(self):
        """Test validation of invalid JSON format"""
        data = '{"name": "test", "value": 123'  # Missing closing brace
        errors = self.processor.validate_data(data, "json")
        self.assertTrue(any("Invalid JSON format" in error for error in errors))
    
    def test_validate_json_empty_object(self):
        """Test validation of empty JSON object"""
        data = '{}'
        errors = self.processor.validate_data(data, "json")
        self.assertTrue(any("cannot be empty" in error for error in errors))
    
    def test_validate_json_empty_array(self):
        """Test validation of empty JSON array"""
        data = '[]'
        errors = self.processor.validate_data(data, "json")
        self.assertTrue(any("cannot be empty" in error for error in errors))
    
    def test_validate_json_invalid_array_items(self):
        """Test validation of JSON array with invalid items"""
        data = '[{"name": "test"}, "invalid_item", 123]'
        errors = self.processor.validate_data(data, "json")
        self.assertTrue(any("must be objects" in error for error in errors))
    
    def test_validate_json_too_many_records(self):
        """Test validation of JSON array with too many records"""
        # Create array with more than max_records
        large_array = [{"id": i} for i in range(self.processor.max_records + 1)]
        data = json.dumps(large_array)
        errors = self.processor.validate_data(data, "json")
        self.assertTrue(any("exceeds maximum limit" in error for error in errors))
    
    # CSV Validation Tests
    def test_validate_csv_valid_data(self):
        """Test validation of valid CSV data"""
        data = "name,age,city\nJohn,25,NYC\nJane,30,LA"
        errors = self.processor.validate_data(data, "csv")
        self.assertEqual(errors, [])
    
    def test_validate_csv_empty_data(self):
        """Test validation of empty CSV data"""
        data = ""
        errors = self.processor.validate_data(data, "csv")
        self.assertTrue(any("cannot be empty" in error for error in errors))
    
    def test_validate_csv_no_header(self):
        """Test validation of CSV without header"""
        data = ",,\nJohn,25,NYC"
        errors = self.processor.validate_data(data, "csv")
        self.assertTrue(any("valid header row" in error for error in errors))
    
    def test_validate_csv_inconsistent_columns(self):
        """Test validation of CSV with inconsistent column count"""
        data = "name,age,city\nJohn,25,NYC\nJane,30"  # Missing city in second row
        errors = self.processor.validate_data(data, "csv")
        self.assertTrue(any("columns, expected" in error for error in errors))
    
    def test_validate_csv_too_many_rows(self):
        """Test validation of CSV with too many rows"""
        # Create CSV with more than max_records
        header = "id,value"
        rows = [f"{i},value{i}" for i in range(self.processor.max_records + 1)]
        data = header + "\n" + "\n".join(rows)
        errors = self.processor.validate_data(data, "csv")
        self.assertTrue(any("exceeds maximum limit" in error for error in errors))
    
    def test_validate_csv_non_string_input(self):
        """Test validation of non-string CSV input"""
        data = 123
        errors = self.processor.validate_data(data, "csv")
        self.assertTrue(any("must be provided as a string" in error for error in errors))
    
    # Text Validation Tests
    def test_validate_text_valid_data(self):
        """Test validation of valid text data"""
        data = "This is a sample text for analysis with sufficient content."
        errors = self.processor.validate_data(data, "text")
        self.assertEqual(errors, [])
    
    def test_validate_text_too_short(self):
        """Test validation of text that's too short"""
        data = "Short"
        errors = self.processor.validate_data(data, "text")
        self.assertTrue(any("at least 10 characters" in error for error in errors))
    
    def test_validate_text_too_long(self):
        """Test validation of text that's too long"""
        # Create text longer than max_text_length
        data = "x" * (self.processor.max_data_size + 1)
        errors = self.processor.validate_data(data, "text")
        self.assertTrue(any("exceeds maximum limit" in error for error in errors))
    
    def test_validate_text_non_string_input(self):
        """Test validation of non-string text input"""
        data = 123
        errors = self.processor.validate_data(data, "text")
        self.assertTrue(any("must be provided as a string" in error for error in errors))
    
    # General Validation Tests
    def test_validate_unsupported_format(self):
        """Test validation with unsupported format"""
        data = "test data"
        errors = self.processor.validate_data(data, "xml")
        self.assertTrue(any("Unsupported format type" in error for error in errors))
    
    def test_validate_empty_data(self):
        """Test validation of empty data"""
        errors = self.processor.validate_data("", "json")
        self.assertTrue(any("cannot be empty" in error for error in errors))
    
    def test_validate_none_data(self):
        """Test validation of None data"""
        errors = self.processor.validate_data(None, "json")
        self.assertTrue(any("cannot be empty" in error for error in errors))
    
    # Data Processing Tests
    def test_process_json_object(self):
        """Test processing of JSON object"""
        data = '{"name": "test", "value": 123}'
        result = self.processor.process_data(data, "json")
        
        self.assertIsInstance(result, ProcessedData)
        self.assertEqual(result.data_type, "json")
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.columns, ["name", "value"])
        self.assertIn("record", result.structured_data)
    
    def test_process_json_array(self):
        """Test processing of JSON array"""
        data = '[{"name": "test1", "value": 123}, {"name": "test2", "value": 456}]'
        result = self.processor.process_data(data, "json")
        
        self.assertIsInstance(result, ProcessedData)
        self.assertEqual(result.data_type, "json")
        self.assertEqual(result.record_count, 2)
        self.assertEqual(result.columns, ["name", "value"])
        self.assertIn("records", result.structured_data)
    
    def test_process_csv_data(self):
        """Test processing of CSV data"""
        data = "name,age,city\nJohn,25,NYC\nJane,30,LA"
        result = self.processor.process_data(data, "csv")
        
        self.assertIsInstance(result, ProcessedData)
        self.assertEqual(result.data_type, "csv")
        self.assertEqual(result.record_count, 2)
        self.assertEqual(result.columns, ["name", "age", "city"])
        self.assertIn("records", result.structured_data)
        self.assertIn("headers", result.structured_data)
    
    def test_process_text_data(self):
        """Test processing of text data"""
        data = "This is a sample text for analysis with sufficient content to test processing."
        result = self.processor.process_data(data, "text")
        
        self.assertIsInstance(result, ProcessedData)
        self.assertEqual(result.data_type, "text")
        self.assertGreater(result.record_count, 0)  # Should have chunks
        self.assertEqual(result.columns, ["text_chunk"])
        self.assertIn("full_text", result.structured_data)
        self.assertIn("chunks", result.structured_data)
        self.assertIn("statistics", result.structured_data)
    
    def test_process_data_with_validation_errors(self):
        """Test processing data that fails validation"""
        data = ""  # Empty data
        with self.assertRaises(DataValidationError):
            self.processor.process_data(data, "json")
    
    def test_process_unsupported_format(self):
        """Test processing with unsupported format"""
        data = "test data"
        with self.assertRaises(ValueError):
            self.processor.process_data(data, "xml")


class TestDataProcessorTool(unittest.TestCase):
    """Test cases for the data_processor tool function"""
    
    def test_tool_success_json(self):
        """Test tool with valid JSON data"""
        data = '{"name": "test", "value": 123}'
        result = data_processor(data, "json")
        
        self.assertTrue(result["success"])
        self.assertIn("processed_data", result)
        self.assertNotIn("error", result)
    
    def test_tool_success_csv(self):
        """Test tool with valid CSV data"""
        data = "name,age\nJohn,25\nJane,30"
        result = data_processor(data, "csv")
        
        self.assertTrue(result["success"])
        self.assertIn("processed_data", result)
        self.assertNotIn("error", result)
    
    def test_tool_success_text(self):
        """Test tool with valid text data"""
        data = "This is a sample text for analysis with sufficient content."
        result = data_processor(data, "text")
        
        self.assertTrue(result["success"])
        self.assertIn("processed_data", result)
        self.assertNotIn("error", result)
    
    def test_tool_validation_failure(self):
        """Test tool with invalid data"""
        data = ""  # Empty data
        result = data_processor(data, "json")
        
        self.assertFalse(result["success"])
        self.assertIn("validation_errors", result)
        self.assertIn("error", result)
    
    def test_tool_processing_failure(self):
        """Test tool with processing error"""
        data = '{"name": "test", "value": 123'  # Invalid JSON
        result = data_processor(data, "json")
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_tool_unsupported_format(self):
        """Test tool with unsupported format"""
        data = "test data"
        result = data_processor(data, "xml")
        
        self.assertFalse(result["success"])
        self.assertIn("validation_errors", result)
        self.assertTrue(any("Unsupported format type" in error for error in result["validation_errors"]))


class TestDataProcessorEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = DataProcessor()
    
    def test_large_json_data(self):
        """Test processing of large JSON data"""
        # Create large but valid JSON
        large_data = {"items": [{"id": i, "value": f"item_{i}"} for i in range(1000)]}
        data = json.dumps(large_data)
        
        result = self.processor.process_data(data, "json")
        self.assertIsInstance(result, ProcessedData)
        self.assertEqual(result.data_type, "json")
    
    def test_csv_with_special_characters(self):
        """Test CSV processing with special characters"""
        data = 'name,description\n"John, Jr.","Has, comma"\n"Jane","Normal text"'
        result = self.processor.process_data(data, "csv")
        
        self.assertIsInstance(result, ProcessedData)
        self.assertEqual(result.record_count, 2)
    
    def test_text_with_unicode(self):
        """Test text processing with Unicode characters"""
        data = "This is a test with Unicode: café, naïve, résumé, and emoji 🚀"
        result = self.processor.process_data(data, "text")
        
        self.assertIsInstance(result, ProcessedData)
        self.assertIn("full_text", result.structured_data)
    
    def test_json_with_nested_objects(self):
        """Test JSON processing with nested objects"""
        data = {
            "company": "Test Corp",
            "employees": [
                {"name": "John", "department": {"name": "IT", "budget": 100000}},
                {"name": "Jane", "department": {"name": "HR", "budget": 50000}}
            ]
        }
        json_data = json.dumps(data)
        
        result = self.processor.process_data(json_data, "json")
        self.assertIsInstance(result, ProcessedData)
        self.assertEqual(result.data_type, "json")
    
    def test_csv_single_column(self):
        """Test CSV processing with single column"""
        data = "value\n123\n456\n789"
        result = self.processor.process_data(data, "csv")
        
        self.assertIsInstance(result, ProcessedData)
        self.assertEqual(result.columns, ["value"])
        self.assertEqual(result.record_count, 3)
    
    def test_text_chunking(self):
        """Test text chunking functionality"""
        # Create text longer than chunk size
        long_text = "This is a test. " * 100  # Should create multiple chunks
        result = self.processor.process_data(long_text, "text")
        
        self.assertIsInstance(result, ProcessedData)
        self.assertGreater(len(result.structured_data["chunks"]), 1)
        self.assertIn("chunk_count", result.metadata)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)