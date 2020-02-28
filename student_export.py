from lib.belt_scripts import get_ninjas_info
from datetime import datetime
import requests
import json

DOJO2_URL = 'http://localhost:5101'
TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NjQzNjA2MTgsIm5iZiI6MTU2NDM2MDYxOCwianRpIjoiNGQ4M2ZkMjUtNDJiZi00YzFjLWEyNzctN2Y3YWI2NzFmYTQyIiwiZXhwIjoxNTY0MzYxNTE4LCJpZGVudGl0eSI6InJ5YW4uc2NoYWZmZXJAY29kZW5pbmphcy5jb20iLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJ1c2VyX2NsYWltcyI6eyJyb2xlcyI6W119fQ._hW8et_ururdyUBT0Z5RpR8sYg9xOYm15UfvkEF9VDk'
headers = {'Authorization': 'Bearer {}'.format(TOKEN)}


def export_students():

    # ninjas = get_ninjas_info('cn-ma-wellesley')
    # with open('data.json', 'w') as fp:
    #     json.dump(ninjas, fp)

    with open('data.json', 'r') as fp:
        ninjas = json.load(fp)

    for ninja in ninjas:
        new_user = create_user(ninja)
        status = create_dojo_user(new_user['uuid'], ninja['Current Belt'])
        print(status)


def create_user(ninja):
    user = {
        'name': '{} {}'.format(ninja['First Name'], ninja['Last Name']),
        'active': ninja['Is Active'],
        'birthday': ninja['Birthday'],
        'roles': [{'name': 'ninja'}]
    }
    resp = requests.post(DOJO2_URL + '/api/users/', json=user, headers=headers)
    return resp.json()[0]


def create_dojo_user(uuid, belt):
    duser = {
        'current_lesson_plan': belt,
        'user': {'uuid': uuid}
    }
    resp = requests.post(DOJO2_URL + '/api/dojousers/', json=duser, headers=headers)
    return resp.json()


if __name__ == '__main__':
    export_students()
