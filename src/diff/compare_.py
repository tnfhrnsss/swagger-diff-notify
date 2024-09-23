from slack import templates
from deepdiff import DeepDiff
from utils import file_util
import re
from constants import PATHS_CONSTANTS

def compareto(api_url, newjson):
    swagger_old = file_util.find_latest_snapshot(api_url)
    diff = DeepDiff(swagger_old, newjson, ignore_order=True)

    diff_messages = []
    if diff:
        file_util.save_diff(diff.to_json())
        added = diff.get('dictionary_item_added', [])

        if added:
            item_added_result = item_added(added, newjson)
            if len(item_added_result) > 0:
                item_added_result.insert(0, templates.new_title_block())
                diff_messages = item_added_result

        changed = diff.get('values_changed')
        if changed:
            change_format_m = item_changed(changed)
            if change_format_m:
                if len(diff_messages) > 0 :
                    diff_messages.append(templates.divider_block())

                diff_messages.append(templates.change_title_block())
                diff_messages.append(templates.markdown_block(change_format_m))

        removed = diff.get('dictionary_item_removed')
        if removed:
            removed_messages = item_removed(removed)
            if removed_messages:
                if len(diff_messages) > 0 :
                    diff_messages.append(templates.divider_block())

                diff_messages.append(templates.remove_title_block())
                diff_messages.append(templates.markdown_block(removed_messages))

    if diff_messages:
        diff_messages.insert(0, templates.header_block(api_url))
        diff_messages.insert(1, templates.welcome_block())

    return diff_messages



def item_added(added, raw_data):
    messages = []
    paths_values = [item.split("root['paths']")[1].strip("[]'") for item in added if "root['paths']" in item]
    for value in paths_values:
        swagger_data = raw_data.get('paths').get(value)
        messages.append(templates.divider_block())
        messages.append(templates.api_path_block(value))
        for endpoint, method in swagger_data.items():
            messages.append(templates.api_method_block(endpoint))
            wrapped_detils = item_added_details(method, raw_data)
            if len(wrapped_detils) > 0:
                messages.append(templates.markdown_block(wrapped_detils))
    return messages


def item_changed(values_changed):
    messages = []

    for path, changes in values_changed.items():
        if "root['paths']" in path:
            extract_path = extract_first_two_brackets(path)
            message = ">{}\n".format(extract_path)
        else:
            continue

        messages.append(message)

    return "\n\n".join(messages)


def item_removed(items):
    messages = []

    for item in items:
        result = remove_constant_from_str(item)
        messages.append("{}".format(result))

    return "\n\n".join(messages)


def extract_first_two_brackets(input_str):
    matches = re.findall(r"\['(.*?)'\]", input_str)

    if len(matches) >= 3:
        return "*({})* {}".format(matches[2], matches[1])
    else:
        return None



def remove_constant_from_str(input_str):
    for constant in PATHS_CONSTANTS:
        if constant in input_str:
            input_str = input_str.replace(constant, "")
    return input_str


def check_required(is_required):
    return "(Required)" if is_required else ""


def item_added_details(method, raw_data):
    table = ""
    for key, details in method.items():
        if key == 'operationId' or key == 'tags':
            continue

        if key == 'parameters':
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
        if key == 'requestBody':
            ref_path = details['content']['application/json']['schema']['$ref']

            path = ref_path.lstrip('#').split('/')
            sms_push_template_cdo = get_value_from_path(raw_data, path)
            scheme_message = format_schema(sms_push_template_cdo)
            table += scheme_message

        if key == 'responses':
            try:
                ref_path = details['200']['content']['*/*']['schema']['$ref']
                path = ref_path.lstrip('#').split('/')


                sms_push_template_cdo = get_value_from_path(raw_data, path)
                scheme_message = response_format_schema(sms_push_template_cdo)
                table += scheme_message
            except KeyError as e:
                print(e)


    return table


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