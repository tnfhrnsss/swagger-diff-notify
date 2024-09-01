from slack_sdk import WebClient
from config_loader import config


def send(message):
    print(message)
    slack_token = config.get('slack_token')
    slack_channel_id = config.get('slack_channel_id')
    client = WebClient(token=slack_token)

    try:
        response = client.chat_postMessage(
            channel=slack_channel_id,
            text= "api change log",
            blocks = message
        )
        print(response)
    except Exception as e:
        print(e)


