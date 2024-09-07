import json

from utils.datetime_util import get_current_datetime


def save_diff(diff):
    current_time = get_current_datetime()
    diff_file_name = "../output/{}_diff_result.json".format(current_time)
    with open(diff_file_name, 'w') as file:
        json.dump(diff, file, indent=4)


def save_snapshot(data):
    with open('../output/lastest_snapshot.json', 'w') as file:
        json.dump(data, file, indent=4)


def find_latest_snapshot():
    with open('../output/lastest_snapshot.json') as file:
        swagger_old = json.load(file)
    return swagger_old