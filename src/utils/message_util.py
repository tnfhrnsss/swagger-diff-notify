import json
import os


def load_messages(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(("Failed to find file. {}").format(file_path))

    with open(file_path, 'r', encoding='utf-8') as file:
        messages = json.load(file)
    return messages


def get_message(key, file_path='./resources/messages.json'):
    messages = load_messages(file_path)
    return messages.get(key, ("'{}'에 해당하는 메시지가 없습니다.").format(key))


def get_formatted_message(key, file_path='messages.json', **kwargs):
    messages = load_messages(file_path)
    message = messages.get(key, ("'{}'에 해당하는 메시지가 없습니다.").format(key))

    try:
        return message.format(**kwargs)
    except KeyError as e:
        return message

