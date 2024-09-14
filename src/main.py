import requests

import http.client
import sys

from slack import message_api
from diff.compare_ import compareto
from utils import file_util

api_url = sys.argv[1]


def main():
    if len(api_url) == 0:
        print("api path is null.")
    else:
        try:
            swagger_url = api_url + '/v3/api-docs'
            response = requests.get(swagger_url)
            swagger_json = response.json()
            diff_messages = compareto(api_url, swagger_json)

            if len(diff_messages) > 0:
                print(diff_messages)
                message_api.send(diff_messages)
            file_util.save_snapshot(api_url, swagger_json)
        except http.client.IncompleteRead as e:
            print("IncompleteRead error occurred exception.!!", e)

        except Exception as e:
            print("occur exception.!!", e)


if __name__ == "__main__":
    main()
