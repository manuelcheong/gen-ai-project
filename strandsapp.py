import json
import os
import logging
from strandsapp import Agent, tool

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define a custom tool for the agent
@tool
def weather_lookup(city: str) -> str:
    """
    Look up the current weather for a city.
    
    Args:
        city (str): The name of the city to check weather for
        
    Returns:
        str: The current weather information
    """
    # In a real implementation, this would call a weather API
    # This is a mock implementation for demonstration
    weather_data = {
        "seattle": "Rainy, 52°F",
        "san francisco": "Foggy, 58°F",
        "new york": "Sunny, 72°F",
        "chicago": "Windy, 45°F",
        "miami": "Sunny, 85°F"
    }
    
    city_lower = city.lower()
    if city_lower in weather_data:
        return f"Current weather in {city}: {weather_data[city_lower]}"
    else:
        return f"Weather data for {city} is not available."

# Initialize the Strands Agent
def create_agent():
    # Get the Bedrock region from environment variables
    bedrock_region = os.environ.get('BEDROCK_REGION', 'us-west-2')
    
    # Create the agent with the Claude 3.7 Sonnet model
    agent = Agent(
        model=f"us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        model_kwargs={
            "region_name": bedrock_region,
            "temperature": 0.7,
            "max_tokens": 1000
        },
        tools=[weather_lookup],
        system_prompt="You are a helpful assistant that provides concise and accurate information. When asked about weather, use the weather_lookup tool."
    )
    
    return agent

# Lambda handler function
def lambda_handler(event, context):
    try:
        logger.info("Received event: %s", json.dumps(event))
        
        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', '')
        
        if not user_message:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'No message provided'})
            }
        
        # Create the agent
        agent = create_agent()
        
        # Process the user message
        response = agent(user_message)
        
        # Return the agent's response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': response.message,
                'tool_uses': [
                    {
                        'name': tool_use.name,
                        'input': tool_use.input,
                        'output': tool_use.output
                    } for tool_use in response.tool_uses
                ]
            })
        }
    
    except Exception as e:
        logger.error("Error processing request: %s", str(e))
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }