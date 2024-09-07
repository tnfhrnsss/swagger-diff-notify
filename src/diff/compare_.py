from slack import templates
from deepdiff import DeepDiff
from utils import file_util

def compareto(newjson):
    swagger_old = file_util.find_latest_snapshot()
    diff = DeepDiff(swagger_old, newjson, ignore_order=True)

    diff_messages = []
    if diff:
        file_util.save_diff(diff.to_json())
        added = diff.get('dictionary_item_added', [])

        if added:
            diff_messages = item_added(added, newjson)

        changed = diff.get('values_changed')
        if changed:
            change_format_m = item_changed(changed)
            if change_format_m:
                if len(diff_messages) > 0 :
                    diff_messages = templates.divider_block()

                diff_messages.append(templates.change_title_block())
                diff_messages.append(templates.markdown_block(change_format_m))

        removed = diff.get('dictionary_item_removed')
        if removed:
            print(removed)

        iterable_added = diff.get('iterable_item_added')
        if iterable_added:
            print(iterable_added)

    if diff_messages:
        diff_messages.insert(0, templates.header_block())

    return diff_messages



def item_added(added, newjson):
    message = []
    paths_values = [item.split("root['paths']")[1].strip("[]'") for item in added if "root['paths']" in item]
    message.append(templates.welcome_block())
    for aaa in paths_values:
        swagger_data = newjson.get('paths').get(aaa)
        message.append(templates.divider_block())
        message.append(templates.api_path_block(aaa))
        for endpoint, methods in swagger_data.items():
            message.append(templates.api_method_block(endpoint))
            message.append(create_slack_message(methods, newjson))
    return message


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


    return templates.markdown_block(table)


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