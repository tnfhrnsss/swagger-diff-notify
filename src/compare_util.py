import json
import requests
from deepdiff import DeepDiff


def compareto(newjson):
    # 이전 및 새로운 Swagger 파일 로드
    with open('../output/lastest_snapshot.json') as file:
        swagger_old = json.load(file)


    # Swagger 파일 비교
    diff = DeepDiff(swagger_old, newjson, ignore_order=True)

    # 변경 사항이 있는 경우 슬랙으로 알림 전송
    if diff:
        print("123123")
        #slack_webhook_url = 'https://hooks.slack.com/services/your/webhook/url'
        #message = f"Swagger API 변경사항 감지됨: {diff}"
        #requests.post(slack_webhook_url, json={"text": message})


if __name__ == "__main__":
    compareto(newjson)