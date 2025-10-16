import json
import demjson3
import requests


def generate_config_with_llm(llm_params: str):
    json_schema = {'schema': {'type': 'object', 'properties': {'mode': {
        'type': 'string', 'enum': ['static', 'dynamic']}, 'phases': {'type':
        'array', 'items': {'type': 'object', 'properties': {'duration': {
        'type': 'number', 'minimum': 1, 'maximum': 355}, 'west': {'type':
        'string', 'enum': ['green', 'yellow', 'red']}, 'east': {'type':
        'string', 'enum': ['green', 'yellow', 'red']}, 'north': {'type':
        'string', 'enum': ['green', 'yellow', 'red']}, 'south': {'type':
        'string', 'enum': ['green', 'yellow', 'red']}}, 'required': [
        'duration', 'west', 'east', 'north', 'south']}, 'minItems': 2},
        'min_phase_time': {'type': 'number', 'minimum': 1},
        'max_phase_time': {'type': 'number', 'minimum': 1},
        'dynamic_logic_factor': {'type': 'number', 'minimum': 0.9,
        'maximum': 0.999}, 'traffic_density': {'type': 'object',
        'description':
        'Average number of cars to spawn per 10 seconds from each direction. Can be a float.'
        , 'properties': {'from_west': {'type': 'number', 'minimum': 0,
        'maximum': 5}, 'from_east': {'type': 'number', 'minimum': 0,
        'maximum': 5}, 'from_north': {'type': 'number', 'minimum': 0,
        'maximum': 5}, 'from_south': {'type': 'number', 'minimum': 0,
        'maximum': 5}}, 'required': ['from_west', 'from_east', 'from_north',
        'from_south']}}, 'required': ['mode', 'phases', 'min_phase_time',
        'max_phase_time', 'dynamic_logic_factor', 'traffic_density']}}
    json_request = {'model': 'qwen/qwen3-4b-thinking-2507', 'messages': [{
        'role': 'user', 'content':
        f"""You are an expert traffic engineer. Your task is to generate a JSON configuration object for a traffic simulator.
This configuration must strictly adhere to the provided JSON Schema.
The scenario to model is: "{llm_params}"."""
        }], 'temperature': 0, 'max_tokens': 2048, 'response_format': {
        'type': 'json_schema', 'json_schema': json_schema}}
    headers = {'content-type': 'application/json'}
    lm_message = json.loads(requests.post(headers=headers, url=
        'http://127.0.0.1:1234/v1/chat/completions', data=json.dumps(
        json_request)).content.decode('utf-8'))['choices'][0]['message'][
        'content']
    json_config = None
    try:
        json_config = json.loads(lm_message)
    except:
        print(lm_message)
        json_config = demjson3.decode(lm_message, strict=False)
        print(json_config)
    return json_config
