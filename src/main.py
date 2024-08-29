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

            slack_message_blocks = []
            for endpoint, methods in swagger_data.items():
                slack_message_blocks.extend(create_slack_message(endpoint, methods))

            print(slack_message_blocks)
            #send(slack_message_blocks)

    #message = format_diff_to_slack(diff)

        #send(message)
        #success(newjson)


def create_slack_message(endpoint, methods):
    blocks = []

    # 엔드포인트 헤더
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*Endpoint:* `{endpoint}`"
        }
    })

    # 각 메소드에 대한 테이블 생성
    for method, details in methods.items():
        print(method)
        print(details)
        if method == 'tags' or method == 'operationId':
            continue

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Method:* `{method.upper()}`"
            }
        })

        table = "*Details:*\n"
        table += "| Key | Value |\n"
        table += "| --- | ----- |\n"
     #   table += f"| *OperationId* | `{details['operationId']}` |\n"
     #   table += f"| *Tags* | `{', '.join(details['tags'])}` |\n"

        if method == 'parameters':
            table = ""
            param_list = ', '.join([f"`{param['name']}` 필수여부: ({param['required']})" for param in details])
            table += f"| *Parameters* | {param_list} |\n"
            print(table)

        #if method == 'requestBody':
            #request_body = details.get('requestBody', {})
            #if request_body:
                #table += "| *Request Body* | JSON |\n"

        #if method == 'responses':
            #responses = details.get('responses', {})
            #response_codes = ', '.join(responses.keys())
            #table += f"| *Responses* | {response_codes} |\n"

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": table
            }
        })

    return blocks


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


def success(newjson):
    with open('../output/lastest_snapshot.json', 'w') as file:
        json.dump(newjson, file, indent=4)


if __name__ == "__main__":
    main()
