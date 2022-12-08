import requests
import subprocess
from jsonpath_ng.ext import parse
import json
from Config import board_id, bearer_token


input_field_color = "#e6e6e6"
output_field_color = "#ffffff"

def get_all_elements_from_board(board_id):
    url = f"https://api.miro.com/v2/boards/{board_id}/items?limit=10"    
    headers = {"accept": "application/json", "authorization": f"{bearer_token}"}
    response = requests.get(url, headers=headers)
    # print(response.text)
    return response.text

def find_element_on_board(element_color, field_type):
    all_elemnents_on_board = get_all_elements_from_board(board_id)
    json_data = json.loads(all_elemnents_on_board)
    if field_type == "Input field":
        jsonpath_expression = parse(f'$.data[?(@.type == "text")]|$.data[?(@.style.fillColor == "{element_color}")]..content')
    elif field_type == "Output field":
        jsonpath_expression = parse(f'$.data[?(@.type == "text")]|$.data[?(@.style.fillColor == "{element_color}")].id')
    match = [match.value for match in jsonpath_expression.find(json_data)]
    # print(match)
    if match != []:
        result = match[0].replace('<p>', '').replace('</p>', '')
    else:
        result = f"{field_type} not found!"
    return result

def return_element_position(board_id, element_id):
    url = f"https://api.miro.com/v2/boards/{board_id}/items/{element_id}"
    headers = {"accept": "application/json", "authorization": f"{bearer_token}"}
    response = requests.get(url, headers=headers)
    json_data = json.loads(response.text)
    jsonpath_expression = parse(f'$.position')
    match = [match.value for match in jsonpath_expression.find(json_data)]
    return match[0]

def get_command(input_field_color):
    command = find_element_on_board(element_color=input_field_color, field_type="Input field")
    return command

def run_command_in_cmd(command):
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, text=True)
        print(result)
    except Exception as e:
        result = print(str(e))
    return result

def push_output_result(output_field_color):
    cli_output = run_command_in_cmd(get_command(input_field_color))
    output_field_id = find_element_on_board(element_color=output_field_color, field_type="Output field")
    position = return_element_position(board_id, element_id=output_field_id)
    position_x, position_y = position['x'], position['y']
    url = f"https://api.miro.com/v2/boards/{board_id}/texts/{output_field_id}"
    payload = {
              "data":{"content": f"{cli_output}"}, "position":{"origin":"center","x":f"{position_x}","y":f"{position_y}"}
              }

    headers = {"accept": "application/json", "content-type": "application/json", "authorization": f"{bearer_token}"}
    response = requests.patch(url, json=payload, headers=headers)
    print(response.status_code)


push_output_result(output_field_color)
