

def markdown_block(messages):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": messages
        }
    }