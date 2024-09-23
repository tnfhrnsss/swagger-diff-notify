import requests

import http.client
import sys

from slack import message_api
from diff.compare_ import diff
from utils import file_util

api_url = sys.argv[1]


def main():
    if len(api_url) == 0:
        print("api path is null.")
    else:
        try:
            api_docs = api_url + '/v3/api-docs'
            response = requests.get(api_docs)
            api_docs_json = response.json()
            diff_messages = diff(api_url, api_docs_json)

            if len(diff_messages) > 0:
                print(diff_messages)
                message_api.send(diff_messages)
            file_util.save_snapshot(api_url, api_docs_json)
        except http.client.IncompleteRead as e:
            print("IncompleteRead error occurred exception.!!", e)

        except Exception as e:
            print("occur exception.!!", e)


if __name__ == "__main__":
    main()
