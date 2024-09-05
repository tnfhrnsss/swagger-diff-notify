import requests

import http.client
import sys
import json
from deepdiff import DeepDiff

from slack_api import send

from datetime_util import get_current_datetime

print(sys.argv[1])
api_url = sys.argv[1]
current_time = get_current_datetime()


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
    with open('../output/lastest_snapshot.json') as file:
        swagger_old = json.load(file)

    diff = DeepDiff(swagger_old, newjson, ignore_order=True)

    slack_message_blocks = []
    if diff:
        save_diff(diff.to_json())

        added = diff.get('dictionary_item_added', [])
        if added:
            slack_message_blocks = item_added(added, newjson)

        changed = diff.get('values_changed')
        if changed:
            print(changed)
            #slack_message_blocks.append(item_changed(changed))

        send(slack_message_blocks)
        success(newjson)




def item_added(added, newjson):
    paths_values = [item.split("root['paths']")[1].strip("[]'") for item in added if "root['paths']" in item]
    # print(paths_values)

    slack_message_blocks = []
    for aaa in paths_values:
        swagger_data = newjson.get('paths').get(aaa)
        #print(swagger_data)


        slack_message_blocks.append(create_divider())
        slack_message_blocks.append(creamte_path_message(aaa))
        for endpoint, methods in swagger_data.items():
            slack_message_blocks.append(create_header_endpoint(endpoint))
            slack_message_blocks.append(create_slack_message(methods, newjson))

        #print(slack_message_blocks)

    return slack_message_blocks


def item_changed(changed):
    messages = []

    for key, changes in changed.items():
        new_value = changes.get('new_value')
        old_value = changes.get('old_value')

        message = f"\n변경된 경로: {key}"

        if isinstance(new_value, dict) and isinstance(old_value, dict):
            for sub_key in new_value.keys() | old_value.keys():
                nv = new_value.get(sub_key)
                ov = old_value.get(sub_key)
                if nv != ov:
                    message += f"\n  - {sub_key} 변경 전: {ov}, 변경 후: {nv}"
        else:
            message += f"\n  - 변경 전: {old_value}, 변경 후: {new_value}"

        messages.append(message)

    return "\n".join(messages)


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
    link_url = ""

    for method, details in methods.items():
        if method == 'operationId':
            continue

        print(method)
        print(details)

        if method == 'tags':
            link_url = api_url + "swagger-ui/index.html#/" + details[0]


        if method == 'parameters':
            header_params = []
            path_params = []
            query_params = []

            for param in details:
                param_string = f"* {param['name']} {check_required(param['required'])}"
                if param['in'] == "header":
                    header_params.append(param_string)
                elif param['in'] == "path":
                    path_params.append(param_string)
                elif param['in'] == "query":
                    query_params.append(param_string)

            if header_params:
                header_param_list = '\n'.join(header_params)
                table += f"• Header Parameters \n ```{header_param_list}``` \n"

            if path_params:
                path_param_list = '\n'.join(path_params)
                table += f"• Path Parameters \n ```{path_param_list}``` \n"

            if query_params:
                query_param_list = '\n'.join(query_params)
                table += f"• Query Parameters \n ```{query_param_list}``` \n"


        scheme_message = ''
        if method == 'requestBody':
            ref_path = details['content']['application/json']['schema']['$ref']

            path = ref_path.lstrip('#').split('/')
            sms_push_template_cdo = get_value_from_path(newjson, path)
            scheme_message = format_schema(sms_push_template_cdo)
            table += scheme_message

        if method == 'responses':
            try:
                ref_path = details['200']['content']['*/*']['schema']['$ref']
                path = ref_path.lstrip('#').split('/')


                sms_push_template_cdo = get_value_from_path(newjson, path)
                scheme_message = response_format_schema(sms_push_template_cdo)
                table += scheme_message
            except KeyError as e:
                print(e)
                #return None


    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": table
        }
    }


def get_value_from_path(data, path):
    for key in path:
        if key == '':
            continue
        data = data[key]
    return data


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
        "• Request Body\n"
        f"```Required Fields: {required_fields}\n"
        f"Properties:\n{properties_str}```"
    )

    return message


def response_format_schema(data):
    properties = []
    for key, value in data.get("properties", {}).items():
        prop_type = value.get("type", "")
        enums = value.get("enum", "")
        message = f"- {key} (type: {prop_type}"
        if enums:
            message += f", enum: {enums}"
        message += ")"
        properties.append(message)

    properties_str = "\n".join(properties)

    message = (
        "• Response Body\n"
        f"```Properties:\n{properties_str}```"
    )

    return message


def save_diff(diff):
    with open(f'../output/{current_time}_diff_result.json', 'w') as file:
        json.dump(diff, file, indent=4)


def success(newjson):
    with open('../output/lastest_snapshot.json', 'w') as file:
        json.dump(newjson, file, indent=4)


if __name__ == "__main__":
    main()
