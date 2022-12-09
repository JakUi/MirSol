import requests
import subprocess
import json
import time
from jsonpath_ng.ext import parse
from Config import board_id, bearer_token, output_test


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
    # print(json_data)
    if field_type == "Input field":
        jsonpath_expression = parse(f'$.data[?(@.type == "text")]|$.data[?(@.style.fillColor == "{element_color}")]..content')
    elif field_type == "Output field":
        jsonpath_expression = parse(f'$.data[?(@.type == "text")]|$.data[?(@.style.fillColor == "{element_color}")].id')
    match = [match.value for match in jsonpath_expression.find(json_data)]
    # print(match)
    if match != []:
        result = match[0].replace('<p>', '').replace('</p>', '\n').replace('<br />', '')
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
        if result == '':
            result = 'Done! Enter next command'
    except Exception as e:
        result = str(e)
    with open('temp.txt', 'w') as file:
        file.write(result)


def prepare_output_results():
    with open('temp.txt', 'r') as file:
        output = ''
        for l in file:
            output = output + '<p>' + l
    return output

def push_output_result(output_field_color, command):
    run_command_in_cmd(command)
    cli_output = prepare_output_results()
    output_field_id = find_element_on_board(element_color=output_field_color, field_type="Output field")
    position = return_element_position(board_id, element_id=output_field_id)
    position_x, position_y = position['x'], position['y']
    url = f"https://api.miro.com/v2/boards/{board_id}/texts/{output_field_id}"
    payload = {
              "data":{"content": f"{cli_output}"}, "position":{"origin":"center","x":f"{position_x}","y":f"{position_y}"}
              }

    headers = {"accept": "application/json", "content-type": "application/json", "authorization": f"{bearer_token}"}
    response = requests.patch(url, json=payload, headers=headers)
    if response.status_code != requests.codes.ok:
        print(response.status_code)
        print(response.text)
    return command


last_command = None
while True:
    command = get_command(input_field_color)
    if last_command != command:
        last_command = push_output_result(output_field_color, command)
    time.sleep(1)
