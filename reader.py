import json


def read_json():
    with open('data.json') as f:
        data = json.load(f)
        return data
