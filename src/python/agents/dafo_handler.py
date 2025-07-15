"""
DAFO Analytics Agent Lambda Handler

AWS Lambda entry point for the DAFO analytics agent.
"""

import json
import logging
from typing import Dict, Any
import asyncio

from .dafo import DAFOAgent
from .dafo.models import AnalysisRequest, DataFormat, AnalysisDepth

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point for DAFO agent
    
    Args:
        event: Lambda event object
        context: Lambda context object
        
    Returns:
        Dictionary containing response data
    """
    try:
        logger.info(f"Received event: {json.dumps(event, default=str)}")
        
        # Determine event type and route accordingly
        if 'httpMethod' in event:
            # REST API request
            return handle_rest_request(event, context)
        elif 'requestContext' in event and 'routeKey' in event['requestContext']:
            # WebSocket API request
            return handle_websocket_request(event, context)
        else:
            # Unknown event type
            logger.warning(f"Unknown event type: {event}")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Unknown event type',
                    'event_keys': list(event.keys())
                })
            }
            
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }


def handle_rest_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle REST API requests
    
    Args:
        event: Lambda event object
        context: Lambda context object
        
    Returns:
        HTTP response dictionary
    """
    try:
        method = event['httpMethod']
        path = event['path']
        
        logger.info(f"Handling REST request: {method} {path}")
        
        # Route based on method and path
        if method == 'POST' and path.startswith('/dafo/analyze'):
            return asyncio.run(handle_analyze_request(event))
        elif method == 'GET' and path.startswith('/dafo/history/'):
            return asyncio.run(handle_history_request(event))
        elif method == 'GET' and path.startswith('/dafo/report/'):
            return asyncio.run(handle_report_request(event))
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'Endpoint not found',
                    'method': method,
                    'path': path
                })
            }
            
    except Exception as e:
        logger.error(f"REST request handling error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Request processing failed',
                'message': str(e)
            })
        }


def handle_websocket_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle WebSocket API requests
    
    Args:
        event: Lambda event object
        context: Lambda context object
        
    Returns:
        WebSocket response dictionary
    """
    try:
        route_key = event['requestContext']['routeKey']
        connection_id = event['requestContext']['connectionId']
        
        logger.info(f"Handling WebSocket request: {route_key} for connection {connection_id}")
        
        # Handle different WebSocket routes
        if route_key == '$connect':
            return handle_websocket_connect(event)
        elif route_key == '$disconnect':
            return handle_websocket_disconnect(event)
        elif route_key == '$default':
            return handle_websocket_message(event)
        else:
            logger.warning(f"Unknown WebSocket route: {route_key}")
            return {'statusCode': 400}
            
    except Exception as e:
        logger.error(f"WebSocket request handling error: {str(e)}")
        return {'statusCode': 500}


async def handle_analyze_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle POST /dafo/analyze requests
    
    Args:
        event: Lambda event object
        
    Returns:
        HTTP response dictionary
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Extract required parameters
        data = body.get('data')
        format_type = body.get('format_type', 'json')
        user_id = body.get('user_id')
        
        if not data or not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameters',
                    'required': ['data', 'user_id']
                })
            }
        
        # Create analysis request
        import uuid
        request = AnalysisRequest(
            data=data,
            format_type=DataFormat(format_type),
            user_id=user_id,
            session_id=body.get('session_id', f"session_{user_id}_{str(uuid.uuid4())[:8]}"),
            industry_context=body.get('industry_context'),
            custom_keywords=body.get('custom_keywords'),
            analysis_depth=AnalysisDepth(body.get('analysis_depth', 'basic'))
        )
        
        # Initialize DAFO agent (components will be injected in later tasks)
        agent = DAFOAgent()
        
        # Perform analysis
        result = await agent.analyze_data(request)
        
        if result['success']:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'session_id': result['session_id'],
                    'message': 'Analysis completed successfully',
                    'result': result['result']
                })
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'error': result['error'],
                    'session_id': result.get('session_id')
                })
            }
            
    except Exception as e:
        logger.error(f"Analyze request error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Analysis request failed',
                'message': str(e)
            })
        }


async def handle_history_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle GET /dafo/history/{user_id} requests
    
    Args:
        event: Lambda event object
        
    Returns:
        HTTP response dictionary
    """
    try:
        # Extract user_id from path parameters
        path_params = event.get('pathParameters', {})
        user_id = path_params.get('user_id')
        
        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing user_id parameter'
                })
            }
        
        # Initialize DAFO agent
        agent = DAFOAgent()
        
        # Get analysis history
        history = await agent.get_analysis_history(user_id)
        
        return {
            'statusCode': 200,
            'body': json.dumps(history)
        }
        
    except Exception as e:
        logger.error(f"History request error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'History request failed',
                'message': str(e)
            })
        }


async def handle_report_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle GET /dafo/report/{analysis_id} requests
    
    Args:
        event: Lambda event object
        
    Returns:
        HTTP response dictionary
    """
    try:
        # Extract analysis_id from path parameters
        path_params = event.get('pathParameters', {})
        analysis_id = path_params.get('analysis_id')
        
        if not analysis_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing analysis_id parameter'
                })
            }
        
        # Initialize DAFO agent
        agent = DAFOAgent()
        
        # Get analysis report
        report = await agent.get_analysis_report(analysis_id)
        
        if report:
            return {
                'statusCode': 200,
                'body': json.dumps(report.to_dict())
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'Analysis report not found',
                    'analysis_id': analysis_id
                })
            }
            
    except Exception as e:
        logger.error(f"Report request error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Report request failed',
                'message': str(e)
            })
        }


def handle_websocket_connect(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle WebSocket connection events
    
    Args:
        event: Lambda event object
        
    Returns:
        WebSocket response dictionary
    """
    connection_id = event['requestContext']['connectionId']
    logger.info(f"WebSocket connection established: {connection_id}")
    
    # Store connection information (will be implemented in later tasks)
    
    return {'statusCode': 200}


def handle_websocket_disconnect(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle WebSocket disconnection events
    
    Args:
        event: Lambda event object
        
    Returns:
        WebSocket response dictionary
    """
    connection_id = event['requestContext']['connectionId']
    logger.info(f"WebSocket connection closed: {connection_id}")
    
    # Clean up connection information (will be implemented in later tasks)
    
    return {'statusCode': 200}


def handle_websocket_message(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle WebSocket message events
    
    Args:
        event: Lambda event object
        
    Returns:
        WebSocket response dictionary
    """
    connection_id = event['requestContext']['connectionId']
    body = event.get('body', '{}')
    
    logger.info(f"WebSocket message from {connection_id}: {body}")
    
    # Process WebSocket messages (will be implemented in later tasks)
    
    return {'statusCode': 200}