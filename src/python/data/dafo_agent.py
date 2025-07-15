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
DAFO_PROMPT = """Eres un especialista en Business Analytics y necesitas generar un informe estratégico en el que se identifique 
    oportunidades de mejora basadas en Big Data y proponga soluciones concretas para un problema especifico.

Habilidades:
- Pensamiento critico
- Toma de decisiones basadas en datos
- Comunicación efectiva.

Concepto de análisis de oportunidades.

Mentalidad proactiva, curiosa y creativa.

Metodología clara y organizada:

- Analiza el problema en profundidad siguiendo los pasos de diagnosis.
- Piensa en la solución basada en datos.
- Utiliza herramientas como el análisis DAFO y el marco SMART
- La comunicación es clave, redacta de forma clara, concisa y persuasiva.
"""

def handler(event: Dict[str, Any], _context) -> str:
    dafo_agent = Agent(
        model=model,
        system_prompt=WEATHER_SYSTEM_PROMPT,
        tools=[http_request]
    )

    

    response = dafo_agent(event.get('prompt'))
    print(response)
    return str(response)