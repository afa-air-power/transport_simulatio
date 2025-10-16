import json
import requests
from jsonschema import validate, ValidationError

# URL вашего локального сервера LM Studio
LLM_URL = "http://localhost:1234/v1/chat/completions"

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


def generate_config_with_llm(scenario_description: str):
    """
    Отправляет запрос к локальной LLM для генерации конфигурации трафика.
    """
    prompt = f"""
You are an expert traffic engineer. Your task is to generate a JSON configuration object for a traffic simulator.
This configuration must strictly adhere to the provided JSON Schema.
The scenario to model is: "{scenario_description}".
Your output must be ONLY the raw JSON object. Do not include any explanations, comments, or markdown code fences (like ```json).

JSON Schema to follow:
{json.dumps(config_schema, indent=2)}
"""

    headers = {"Content-Type": "application/json"}
    # Параметр 'response_format' не всегда поддерживается локальными LLM-серверами.
    # Мы его убираем и полагаемся на подробный промпт и валидацию ответа.
    data = {
        "model": "qwen/qwen3-4b-thinking-2507",  # Убедитесь, что эта модель загружена в LM Studio
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 2048,  # Увеличено, чтобы вместить полный JSON
    }

    try:
        response = requests.post(LLM_URL, headers=headers, json=data, timeout=12000)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Не удалось подключиться к LM Studio. Ошибка: {e}")

    try:
        llm_output = response.json()['choices'][0]['message']['content']
        print(llm_output)

        # Более надежный способ извлечь JSON из ответа
        start_index = llm_output.find('{')
        end_index = llm_output.rfind('}')
        if start_index == -1 or end_index == -1:
            raise ValueError("В ответе LLM не найден JSON-объект.")

        cleaned_output = llm_output[start_index:end_index + 1]
        config_data = json.loads(cleaned_output)

    except (json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
        raise ValueError(f"Некорректный формат ответа от LLM: {e}\nОтвет: {llm_output}")

    try:
        validate(instance=config_data, schema=config_schema)
        return config_data
    except ValidationError as e:
        # Попытка исправить распространенную ошибку модели (возврат старого ключа)
        if "'traffic_density' is a required property" in e.message and 'traffic_spawn_rates' in config_data:
            print("Обнаружена распространенная ошибка LLM, попытка исправления...")
            config_data['traffic_density'] = config_data.pop('traffic_spawn_rates')
            try:
                # Повторная валидация после исправления
                validate(instance=config_data, schema=config_schema)
                print("Исправление успешно, валидация пройдена.")
                return config_data
            except ValidationError as e2:
                # Если даже после исправления не работает, то проблема серьезнее
                raise ValueError(f"JSON не прошел валидацию даже после исправления: {e2}")
        else:
            # Если ошибка в чем-то другом, просто пробрасываем ее
            raise ValueError(f"Сгенерированный JSON не прошел валидацию: {e}")
