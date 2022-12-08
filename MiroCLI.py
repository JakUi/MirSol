import requests
import os
import subprocess
from jsonpath_ng.ext import parse
import json
from Config import board_id, bearer_token


def run_command_in_cmd(command):
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, text=True)
        print(result)
    except Exception as e:
        print(str(e))

# def get_element_info(board_id, element_id):
#     url = f"https://api.miro.com/v2/boards/{board_id}/items/{element_id}"
#     headers = {"accept": "application/json", "authorization": f"{bearer_token}"}
#     response = requests.get(url, headers=headers)
#     print(response.text)

def get_all_elements_from_board(board_id):
    url = f"https://api.miro.com/v2/boards/{board_id}/items?limit=10"    
    headers = {"accept": "application/json", "authorization": f"{bearer_token}"}
    response = requests.get(url, headers=headers)    
    return response.text

element_color = "#e6e6e6"

def get_command(element_color):
    all_elemnents_on_board = get_all_elements_from_board(board_id)
    json_data = json.loads(all_elemnents_on_board)
    jsonpath_expression = parse(f'$.data[?(@.type == "text")]|$.data[?(@.style.fillColor == "{element_color}")]..content')
    result = [match.value for match in jsonpath_expression.find(json_data)]
    if result != []:
        command = result[0].replace('<p>', '').replace('</p>', '')
    else:
        command = "Console not found!"
    
    print(command)
    return command

run_command_in_cmd(get_command(element_color))
