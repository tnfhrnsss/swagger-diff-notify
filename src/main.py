import requests

import http.client
import sys
import json
from deepdiff import DeepDiff

from slack_api import send

print(sys.argv[1])
api_url = sys.argv[1]


def main():
    if len(api_url) == 0:
        print("api path is null.")
    else:
        try:
            swagger_url = api_url + '/v3/api-docs'
            response = requests.get(swagger_url)
            swagger_json = response.json()
            compareto(swagger_json)
            #print(swagger_json)
        except http.client.IncompleteRead as e:
            print("IncompleteRead error occurred exception.!!", e)

        except Exception as e:
            print("occur exception.!!", e)


def compareto(newjson):
    # 이전 및 새로운 Swagger 파일 로드
    with open('../output/lastest_snapshot.json') as file:
        swagger_old = json.load(file)


    # Swagger 파일 비교
    diff = DeepDiff(swagger_old, newjson, ignore_order=True)

    # 변경 사항이 있는 경우 슬랙으로 알림 전송
    if diff:
        #print(diff)

        added = diff.get('dictionary_item_added', [])
        #print(added)
        added_items = [item for item in diff['dictionary_item_added'] if "root['paths']" in item]

        paths_values = [item.split("root['paths']")[1].strip("[]'") for item in diff['dictionary_item_added'] if "root['paths']" in item]
       # print(paths_values)

        for aaa in paths_values:
            swagger_data = newjson.get('paths').get(aaa)
            #print(swagger_data)
            #print(aaa)

            slack_message_blocks = []
            slack_message_blocks.append(create_header())
            slack_message_blocks.append(create_divider())
            slack_message_blocks.append(creamte_path_message(aaa))
            for endpoint, methods in swagger_data.items():
                slack_message_blocks.append(create_header_endpoint(endpoint))
                slack_message_blocks.append(create_slack_message(methods, newjson))

            #print(slack_message_blocks)
            #send(slack_message_blocks)

    #message = format_diff_to_slack(diff)

        #send(message)
        #success(newjson)

def create_header():
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ":mag: *Api Change*"
        }
    }


def creamte_path_message(path):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*API:* `{path}`"
        }
    }



def create_header_endpoint(endpoint):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*Method:* `{endpoint}`"
        }
    }


def create_divider():
    return {
        "type": "divider"
    }


def check_required(is_required):
    return "(Required)" if is_required else ""



def create_slack_message(methods, newjson):
    table = ""


    # 각 메소드에 대한 테이블 생성
    for method, details in methods.items():
        if method == 'tags' or method == 'operationId':
            continue

        if method == 'responses':
            continue

        print(method)
        print(details)

     #   table += f"| *OperationId* | `{details['operationId']}` |\n"
     #   table += f"| *Tags* | `{', '.join(details['tags'])}` |\n"

        if method == 'parameters':
            header_params = []
            path_params = []

            for param in details:
                param_string = f"• {param['name']} {check_required(param['required'])} \n"
                if param['in'] == "header":
                    header_params.append(param_string)
                elif param['in'] == "path":
                    path_params.append(param_string)

            if header_params:
                header_param_list = '\n '.join(header_params)
                table += f"* Header Parameters* \n {header_param_list} \n"

            if path_params:
                path_param_list = '\n '.join(path_params)
                table += f"* Path Parameters* \n {path_param_list} \n"


        scheme_message = ''
        if method == 'requestBody':
            ref_path = details['content']['application/json']['schema']['$ref']

            path = ref_path.lstrip('#').split('/')
            def get_value_from_path(data, path):
                for key in path:
                    if key == '':
                        continue
                    data = data[key]
                return data

            sms_push_template_cdo = get_value_from_path(newjson, path)

            print(json.dumps(sms_push_template_cdo, indent=2))
            scheme_message = format_schema(sms_push_template_cdo)
            table += scheme_message

        #if method == 'responses':
            #responses = details.get('responses', {})
            #response_codes = ', '.join(responses.keys())
            #table += f"| *Responses* | {response_codes} |\n"

    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
         #   "text": table,
            "text": f"``` {table}```"
        }
    }




def format_diff_to_slack(diff):
    added = diff.get('dictionary_item_added', [])
    removed = diff.get('dictionary_item_removed', [])
    changed = diff.get('values_changed', {})

    # 테이블 헤더
    message = "*API 변경 사항 감지됨:*\n\n"

    if added:
        message += "*추가된 항목:*\n"
        for item in added:
            message += f"- {item}\n"

    if removed:
        message += "\n*제거된 항목:*\n"
        for item in removed:
            message += f"- {item}\n"

    if changed:
        message += "\n*변경된 항목:*\n"
        for key, value in changed.items():
            message += f"- {key}: {value['old_value']} -> {value['new_value']}\n"

    return message


def format_schema(data):
    required_fields = ', '.join(data.get("required", []))

    properties = []
    for key, value in data.get("properties", {}).items():
        prop_type = value.get("type", "")
        min_length = value.get("minLength", "")
        max_length = value.get("maxLength", "")
        properties.append(f"- {key} (type: {prop_type}, minLength: {min_length}, maxLength: {max_length})")

    properties_str = "\n".join(properties)

    message = (
        "Request Body\n"
        f"Required Fields: {required_fields}\n"
        f"Properties:\n{properties_str}"
    )

    return message


def success(newjson):
    with open('../output/lastest_snapshot.json', 'w') as file:
        json.dump(newjson, file, indent=4)


if __name__ == "__main__":
    main()
