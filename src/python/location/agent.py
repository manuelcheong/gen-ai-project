import os
from strands import Agent
from strands_tools import http_request
from strands.models import BedrockModel
from typing import Dict, Any

model = BedrockModel(
    model_id="eu.anthropic.claude-sonnet-4-20250514-v1:0",
    additional_request_fields={
        "anthropic_beta": ["interleaved-thinking-2025-05-14"],
        "thinking": {"type": "enabled", "budget_tokens": 8000},
    },
)

os.environ["STRANDS_TOOL_CONSOLE_MODE"] = "enabled"

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
        model=model,
        system_prompt=WEATHER_SYSTEM_PROMPT,
        tools=[http_request]
    )

    

    response = weather_agent(event.get('prompt'))
    print(response)
    return str(response)