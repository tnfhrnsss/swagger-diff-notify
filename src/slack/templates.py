from utils.message_util import get_message


def header_block():
    return {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": get_message("header")
        }
    }


def welcome_block():
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": get_message("welcome")
        }
    }


def change_title_block():
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ":mechanic: *What's changed?*"
        }
    }


def remove_title_block():
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ":no_good::skin-tone-3: *What's removed?*"
        }
    }


def markdown_block(messages):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": messages
        }
    }


def api_path_block(path):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*API:* `{}`".format(path)
        }
    }


def api_method_block(method):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Method:* `{}`".format(method)
        }
    }


def divider_block():
    return {
        "type": "divider"
    }