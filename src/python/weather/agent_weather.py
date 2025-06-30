from strands import Agent
from strands_tools import http_request
from typing import Dict, Any
from strands.models import BedrockModel

bedrock_model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region_name='us-west-2',  # Change to your preferred region
    temperature=0.3,
)

# Define a weather-focused system prompt
WEATHER_SYSTEM_PROMPT = """You are a weather assistant with HTTP capabilities. You can:

1. Make HTTP requests to the National Weather Service API
2. Process and display weather forecast data
3. Provide weather information for locations in the United States

When retrieving weather information:
1. First get the coordinates or grid information using https://api.weather.gov/points/{latitude},{longitude} or https://api.weather.gov/points/{zipcode}
2. Then use the returned forecast URL to get the actual forecast

When displaying responses:
- Format weather data in a human-readable way
- Highlight important information like temperature, precipitation, and alerts
- Handle errors appropriately
- Convert technical terms to user-friendly language

Always explain the weather conditions clearly and provide context for the forecast.
"""

def handler(event: Dict[str, Any], _context) -> str:
    weather_agent = Agent(
        model=bedrock_model,
        system_prompt=WEATHER_SYSTEM_PROMPT,
        tools=[http_request],
    )

    response = weather_agent(event.get('prompt'))
    return str(response)