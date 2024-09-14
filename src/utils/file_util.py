import json

from utils.datetime_util import get_current_datetime
from utils.url_parser_util import extract_domain_port


def save_diff(diff):
    current_time = get_current_datetime()
    diff_file_name = "../output/{}_diff_result.json".format(current_time)
    with open(diff_file_name, 'w') as file:
        json.dump(diff, file, indent=4)


def save_snapshot(prefix, data):
    with open('../output/{}_lastest_snapshot.json'.format(extract_domain_port(prefix)), 'w') as file:
        json.dump(data, file, indent=4)


def find_latest_snapshot(prefix):
    try:
        with open('../output/{}_lastest_snapshot.json'.format(extract_domain_port(prefix))) as file:
            swagger_old = json.load(file)
        return swagger_old
    except FileNotFoundError as e:
        print("can't find snapshop file. {}".format(e))
        return json.dumps({})

