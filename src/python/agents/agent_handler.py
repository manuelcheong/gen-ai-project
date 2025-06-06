import json
import requests

def handler(event, context):
    """
    Simple Lambda function that returns the current time and any input data
        
    Parameters:
        event (dict): Input event data
        context (LambdaContext): Lambda runtime information
            
        Returns:
            dict: Response containing timestamp and echo of input data
        """
    response = requests.get('https://httpbin.org/get')
            
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Successfully made HTTP request',
            'status_code': response.status_code,
            'response_data': response.json()
        })
    }
    
