

import requests

import http.client
import sys
import json
from deepdiff import DeepDiff
import re

from slack_api import send
from slack import formatter
from utils.datetime_util import get_current_datetime

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

        slack_message_blocks.append(header_block_message())

        if added:
            slack_message_blocks = item_added(added, newjson, slack_message_blocks)

        changed = diff.get('values_changed')
        if changed:
            change_format_m = item_changed(changed)
            if change_format_m:
                slack_message_blocks.append(create_divider())
                slack_message_blocks.append(change_block_message())
                slack_message_blocks.append(formatter.markdown_block(change_format_m))

        removed = diff.get('dictionary_item_removed')
        if removed:
            print(removed)

        iterable_added = diff.get('iterable_item_added')
        if iterable_added:
            print(iterable_added)

        print(slack_message_blocks)
        send(slack_message_blocks)
        success(newjson)




def item_added(added, newjson, root_block):
    paths_values = [item.split("root['paths']")[1].strip("[]'") for item in added if "root['paths']" in item]
    root_block.append(add_block_message())
    for aaa in paths_values:
        swagger_data = newjson.get('paths').get(aaa)
        root_block.append(create_divider())
        root_block.append(creamte_path_message(aaa))
        for endpoint, methods in swagger_data.items():
            root_block.append(create_header_endpoint(endpoint))
            root_block.append(create_slack_message(methods, newjson))
    return root_block


def item_changed(values_changed):
    messages = []

    for path, changes in values_changed.items():
        if "root['servers']" in path or "root['paths']" in path:
            continue

        matched = re.search(r"\['schemas'\]\['(.*?)'\]", path)
        changed_key = path
        if matched:
            changed_key = matched.group(1)

        old_value = changes.get("old_value", {})
        new_value = changes.get("new_value", {})

        message = ">*{}*\n".format(changed_key)

        for key in old_value.keys() | new_value.keys():
            message += "* {} \n\n".format(key)

        messages.append(message)

    return "\n\n".join(messages)


def header_block_message():
    return {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": ":rocket: API Update Alert! \n"
        }
    }


def add_block_message():
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Hi! :wave: \nAPI specs just got an upgrade! :star2::hammer_and_wrench: \n\n\n :arrows_counterclockwise: *What's new?*"
        }
    }

def change_block_message():
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ":mechanic: *What's changed?*"
        }
    }


def creamte_path_message(path):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*API:* `{}`".format(path)
        }
    }



def create_header_endpoint(endpoint):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Method:* `{}`".format(endpoint)
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

    for method, details in methods.items():
        if method == 'operationId' or method == 'tags':
            continue

        if method == 'parameters':
            header_params = []
            path_params = []
            query_params = []

            for param in details:
                param_string = "- {} {}".format(param['name'], check_required(param['required']))
                if param['in'] == "header":
                    header_params.append(param_string)
                elif param['in'] == "path":
                    path_params.append(param_string)
                elif param['in'] == "query":
                    query_params.append(param_string)

            if header_params:
                header_param_list = '\n'.join(header_params)
                table += ">Header Parameters \n ```{}``` \n\n".format(header_param_list)

            if path_params:
                path_param_list = '\n'.join(path_params)
                table += ">Path Parameters \n ```{}``` \n\n".format(path_param_list)

            if query_params:
                query_param_list = '\n'.join(query_params)
                table += ">Query Parameters \n ```{}``` \n\n".format(query_param_list)


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
        message = "- {} ({})".format(key, prop_type)
        if min_length:
            message += ", (min/max: {}/{}".format(min_length, max_length)
        message += ")"
        properties.append(message)

    properties_str = "\n".join(properties)

    message = (
        ">Request Body\n"
        "```Required Fields: {}\n"
        "{}```\n\n"
    ).format(required_fields, properties_str)

    return message


def response_format_schema(data):
    properties = []
    for key, value in data.get("properties", {}).items():
        prop_type = value.get("type", "")
        enums = value.get("enum", "")
        message = "- {} ({}".format(key, prop_type)
        if enums:
            message += ", enum: {}".format(enums)
        message += ")"
        properties.append(message)

    properties_str = "\n".join(properties)

    message = (
        ">Response Body\n"
        "```{}```\n\n"
    ).format(properties_str)

    return message


def save_diff(diff):
    diff_file_name = "../output/{}_diff_result.json".format(current_time)
    with open(diff_file_name, 'w') as file:
        json.dump(diff, file, indent=4)


def success(newjson):
    with open('../output/lastest_snapshot.json', 'w') as file:
        json.dump(newjson, file, indent=4)


if __name__ == "__main__":
    main()
