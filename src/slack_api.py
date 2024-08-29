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
            text= "coverage alarm message",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text":   " 테스트 코드 작성 ✍ 해주세요. ( Coverage 60% 이상 )"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "👀 대상 목록입니다.\n " + message
                        }
                    ]
                }
            ]
        )
        print(response)
    except Exception as e:
        print(e)


