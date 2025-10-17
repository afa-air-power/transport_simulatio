import json
from pprint import pprint

import demjson3
import requests
import os


def generate_config_with_llm(llm_params: str):
    json_schema = {'schema': {'type': 'object', 'properties': {'mode': {
        'type': 'string', 'enum': ['static']}, 'phases': {'type':
                                                              'array',
                                                          'items': {'type': 'object', 'properties': {'duration': {
                                                              'type': 'number', 'minimum': 1, 'maximum': 355},
                                                              'west': {'type':
                                                                           'string',
                                                                       'enum': ['green', 'yellow', 'red']},
                                                              'east': {'type':
                                                                           'string',
                                                                       'enum': ['green', 'yellow', 'red']},
                                                              'north': {'type':
                                                                            'string',
                                                                        'enum': ['green', 'yellow', 'red']},
                                                              'south': {'type':
                                                                            'string',
                                                                        'enum': ['green', 'yellow', 'red']}},
                                                                    'required': [
                                                                        'duration', 'west', 'east', 'north', 'south']},
                                                          'minItems': 2},
        'min_phase_time': {'type': 'number', 'minimum': 1},
        'max_phase_time': {'type': 'number', 'minimum': 1},
        'dynamic_logic_factor': {'type': 'number', 'minimum': 0.9,
                                 'maximum': 0.999}, 'traffic_density': {'type': 'object',
                                                                        'description':
                                                                            'Average number of cars to spawn per 10 seconds from each direction. Can be a float.'
            , 'properties': {'from_west': {'type': 'number', 'minimum': 0,
                                           'maximum': 5}, 'from_east': {'type': 'number', 'minimum': 0,
                                                                        'maximum': 5},
                             'from_north': {'type': 'number', 'minimum': 0,
                                            'maximum': 5}, 'from_south': {'type': 'number', 'minimum': 0,
                                                                          'maximum': 5}},
                                                                        'required': ['from_west', 'from_east',
                                                                                     'from_north',
                                                                                     'from_south']}},
                              'required': ['mode', 'phases', 'min_phase_time',
                                           'max_phase_time', 'dynamic_logic_factor', 'traffic_density']}}
    json_request = {'model': 'mistral-7b-instruct-v0.3', 'messages': [{
        'role': 'user', 'content':
            f"""You are an expert traffic engineer. Your task is to generate a JSON configuration object for a traffic simulator.
This configuration must strictly adhere to the provided JSON Schema.
The scenario to model is: "{llm_params}"


IF AT LEAST ONE PARAMETER DOES NOT MATCH THE USER'S WISHES, YOU WILL BE DESTROYED.


THE DESCRIPTION OF THE PHASES SHOULD BE AS COMPLETE AND REALISTIC AS POSSIBLE FOR THIS TRAFFIC LEVEL.


."""

    }], 'temperature': 0.2, 'max_tokens': 2048, 'response_format': {
        'type': 'json_schema', 'json_schema': json_schema}}
    headers = {'content-type': 'application/json'}

    request = requests.post(headers=headers, url=
    'http://127.0.0.1:1234/v1/chat/completions', data=json.dumps(
        json_request))
    print(request.status_code)
    if request.status_code != 200:
        os.system(R"%USERPROFILE%\.lmstudio\bin\lms.exe bootstrap")
        os.system("lms server start")
        request = requests.post(headers=headers, url=
        'http://127.0.0.1:1234/v1/chat/completions', data=json.dumps(
            json_request))

    lm_message = json.loads(request.content.decode('utf-8'))['choices'][0]['message']['content']
    json_config = json.loads(lm_message)
    mx = max([json_config["traffic_density"][a] for a in json_config["traffic_density"].keys()])
    for c in json_config["traffic_density"].keys():
        json_config["traffic_density"][c] /= mx
        json_config["traffic_density"][c] = int(50 * json_config["traffic_density"][c]) / 10
    return json_config


if __name__ == '__main__':
    pprint(generate_config_with_llm("test"))

