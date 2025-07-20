#!/usr/bin/env python3
"""
Basic test script to verify data processor functionality
"""

import sys
import os
import json

# Add the parent directories to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

try:
    from src.python.agents.dafo.tools.data_processor import DataProcessor, data_processor
    from src.python.agents.dafo.models import ProcessedData
    
    print("✓ Successfully imported modules")
    
    # Test 1: JSON processing
    print("\n--- Testing JSON Processing ---")
    json_data = '{"name": "test", "value": 123, "active": true}'
    result = data_processor(json_data, "json")
    
    if result["success"]:
        print("✓ JSON processing successful")
        processed = result["processed_data"]
        print(f"  - Data type: {processed['data_type']}")
        print(f"  - Record count: {processed['record_count']}")
        print(f"  - Columns: {processed['columns']}")
    else:
        print("✗ JSON processing failed:", result.get("error"))
    
    # Test 2: CSV processing
    print("\n--- Testing CSV Processing ---")
    csv_data = "name,age,city\nJohn,25,NYC\nJane,30,LA\nBob,35,Chicago"
    result = data_processor(csv_data, "csv")
    
    if result["success"]:
        print("✓ CSV processing successful")
        processed = result["processed_data"]
        print(f"  - Data type: {processed['data_type']}")
        print(f"  - Record count: {processed['record_count']}")
        print(f"  - Columns: {processed['columns']}")
    else:
        print("✗ CSV processing failed:", result.get("error"))
    
    # Test 3: Text processing
    print("\n--- Testing Text Processing ---")
    text_data = "This is a sample business report with important information about our company's performance and strategic position in the market."
    result = data_processor(text_data, "text")
    
    if result["success"]:
        print("✓ Text processing successful")
        processed = result["processed_data"]
        print(f"  - Data type: {processed['data_type']}")
        print(f"  - Record count: {processed['record_count']}")
        print(f"  - Columns: {processed['columns']}")
        stats = processed['structured_data']['statistics']
        print(f"  - Word count: {stats['word_count']}")
        print(f"  - Character count: {stats['character_count']}")
    else:
        print("✗ Text processing failed:", result.get("error"))
    
    # Test 4: Validation errors
    print("\n--- Testing Validation Errors ---")
    invalid_json = '{"name": "test", "value": 123'  # Missing closing brace
    result = data_processor(invalid_json, "json")
    
    if not result["success"]:
        print("✓ Validation correctly caught invalid JSON")
        print(f"  - Errors: {result['validation_errors']}")
    else:
        print("✗ Validation should have failed for invalid JSON")
    
    # Test 5: Unsupported format
    print("\n--- Testing Unsupported Format ---")
    result = data_processor("test data", "xml")
    
    if not result["success"]:
        print("✓ Correctly rejected unsupported format")
        print(f"  - Errors: {result['validation_errors']}")
    else:
        print("✗ Should have rejected unsupported format")
    
    print("\n=== All basic tests completed ===")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure all required modules are available")
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()