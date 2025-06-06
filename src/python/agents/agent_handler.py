import json
import datetime

def handler(event, context):
    """
    Simple Lambda function that returns the current time and any input data
        
    Parameters:
        event (dict): Input event data
        context (LambdaContext): Lambda runtime information
            
        Returns:
            dict: Response containing timestamp and echo of input data
        """
    current_time = datetime.datetime.now().isoformat()
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Hello from Lambda!',
            'timestamp': current_time,
            'input': event
        })
    }
