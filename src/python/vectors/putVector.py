import boto3 
import json 
from typing import Dict, Any

s3vectors = boto3.client('s3vectors', region_name='eu-central-1')

def handler(event: Dict[str, Any], _context) -> str:

    s3vectors.put_vectors( vectorBucketName="channy-vector-bucket",
    indexName="channy-vector-index", 
    vectors=[
    {"key": "v1", "data": {"float32": event.get('embedding')}, "metadata": {"id": event.get('key'), "source_text": event.get('key'), "genre":"documents"}}
    ],
    )
    return { "statusCode": 200, "body": json.dumps({"message": "Vector added successfully"})}