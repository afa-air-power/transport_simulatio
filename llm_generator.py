from openai import OpenAI
import json

# JSON-схема для валидации конфигурации, полученной от LLM
config_schema = {
    "type": "object",
    "properties": {
        "mode": {"type": "string", "enum": ["static", "dynamic"]},
        "phases": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "duration": {"type": "number", "minimum": 1, "maximum": 355},
                    "west": {"type": "string", "enum": ["green", "yellow", "red"]},
                    "east": {"type": "string", "enum": ["green", "yellow", "red"]},
                    "north": {"type": "string", "enum": ["green", "yellow", "red"]},
                    "south": {"type": "string", "enum": ["green", "yellow", "red"]}
                },
                "required": ["duration", "west", "east", "north", "south"]
            },
            "minItems": 2
        },
        "min_phase_time": {"type": "number", "minimum": 1},
        "max_phase_time": {"type": "number", "minimum": 1},
        "dynamic_logic_factor": {"type": "number", "minimum": 0.9, "maximum": 0.999},
        "traffic_density": {
            "type": "object",
            "description": "Average number of cars to spawn per 10 seconds from each direction. Can be a float.",
            "properties": {
                "from_west": {"type": "number", "minimum": 0, "maximum": 4.999},
                "from_east": {"type": "number", "minimum": 0, "maximum": 4.999},
                "from_north": {"type": "number", "minimum": 0, "maximum": 4.999},
                "from_south": {"type": "number", "minimum": 0, "maximum": 4.999}
            },
            "required": ["from_west", "from_east", "from_north", "from_south"]
        }
    },
    "required": ["mode", "phases", "min_phase_time", "max_phase_time", "dynamic_logic_factor", "traffic_density"]
}
# Initialize OpenAI client that points to the local LM Studio server
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)


def generate_config_with_llm(scenario_description: str):
    """
    Отправляет запрос к локальной LLM для генерации конфигурации трафика.
    """
    prompt = f"""
You are an expert traffic engineer. Your task is to generate a JSON configuration object for a traffic simulator.
This configuration must strictly adhere to the provided JSON Schema.
The scenario to model is: "{scenario_description}".

"""
    messages = [
        {"role": "system", "content": "You are an expert traffic engineer. Your task is to generate a JSON configuration object for a traffic simulator."},
        {"role": "user", "content": prompt}
    ]
    character_schema = {
        "type": "json_schema",
        "json_schema": {
            "schema": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "enum": ["static", "dynamic"]},
                    "phases": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "duration": {"type": "number", "minimum": 1, "maximum": 355},
                                "west": {"type": "string", "enum": ["green", "yellow", "red"]},
                                "east": {"type": "string", "enum": ["green", "yellow", "red"]},
                                "north": {"type": "string", "enum": ["green", "yellow", "red"]},
                                "south": {"type": "string", "enum": ["green", "yellow", "red"]}
                            },
                            "required": ["duration", "west", "east", "north", "south"]
                        },
                        "minItems": 2
                    },
                    "min_phase_time": {"type": "number", "minimum": 1},
                    "max_phase_time": {"type": "number", "minimum": 1},
                    "dynamic_logic_factor": {"type": "number", "minimum": 0.9, "maximum": 0.999},
                    "traffic_density": {
                        "type": "object",
                        "description": "Average number of cars to spawn per 10 seconds from each direction. Can be a float.",
                        "properties": {
                            "from_west": {"type": "number", "minimum": 0, "maximum": 4.999},
                            "from_east": {"type": "number", "minimum": 0, "maximum": 4.999},
                            "from_north": {"type": "number", "minimum": 0, "maximum": 4.999},
                            "from_south": {"type": "number", "minimum": 0, "maximum": 4.999}
                        },
                        "required": ["from_west", "from_east", "from_north", "from_south"]
                    }
                },
                "required": ["mode", "phases", "min_phase_time", "max_phase_time", "dynamic_logic_factor",
                             "traffic_density"]
            }
        }
    }

    # Get response from AI
    response = client.chat.completions.create(
        model="qwen/qwen3-4b-thinking-2507",
        messages=messages,
        response_format=character_schema,
    )

    # Parse and display the results
    return json.loads(response.choices[0].message.content)
