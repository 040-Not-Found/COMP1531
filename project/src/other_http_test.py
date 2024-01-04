import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
import jwt
from auth import SECRET
from error import *
from Global_variables import *
from datetime import datetime, timezone
# Use this fixture to get the URL of the server. sIt starts the server for you,
# so you don't need to.
owners = 1
members = 2
INVALID_ID = -1


@pytest.fixture
def url():
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")


@pytest.fixture
def register_create_channel(url):
    first_user = {
        'email': 'celine@gmail.com',
        'password': '123456',
        'name_first': 'Celine',
        'name_last': 'Lin',
    }
    user_1_detail_json = requests.post(f'{url}/auth/register', json=first_user)
    user_1_detail = user_1_detail_json.json()
    user1_token = user_1_detail['token']

    second_user = {
        'email': 'theresa@gmail.com',
        'password': '123456',
        'name_first': 'Theresa',
        'name_last': 'Tao',
    }
    user_2_detail_json = requests.post(
        f'{url}/auth/register', json=second_user)
    user_2_detail = user_2_detail_json.json()

    third_user = {
        'email': 'peter@gmail.com',
        'password': '123456',
        'name_first': 'Peter',
        'name_last': 'Xie',
    }
    user_3_detail_json = requests.post(
        f'{url}/auth/register', json=third_user)
    user_3_detail = user_3_detail_json.json()

    first_channel = {
        'token': user1_token,
        'name': 'cctv1',
        'is_public': True
    }

    channel_info1_json = requests.post(
        f'{url}/channels/create', json=first_channel)
    channel_info1 = channel_info1_json.json()

    second_channel = {
        'token': user1_token,
        'name': 'cctv2',
        'is_public': True
    }

    channel_info2_json = requests.post(
        f'{url}/channels/create', json=second_channel)
    channel_info2 = channel_info2_json.json()

    return user_1_detail, user_2_detail, user_3_detail, channel_info1, channel_info2


@pytest.fixture
def register_channel_message(url):
    # user register
    user_1 = {
        'email': 'vicky@gmail.com',
        'password': '1234567',
        'name_first': 'Vicky',
        'name_last': 'Hu',
    }

    user_1_detail_json = requests.post(f'{url}/auth/register', json=user_1)
    user_1_detail = user_1_detail_json.json()
    user_1_token = user_1_detail['token']
    # create a channel
    channel = {
        'token': user_1_token,
        'name': 'cctv1',
        'is_public': True
    }

    channel_info_json = requests.post(
        f'{url}/channels/create', json=channel)
    channel_info = channel_info_json.json()
    channel_id = channel_info['channel_id']
    # user send messages
    first_msg = {
        'token': user_1_token,
        'channel_id': channel_id,
        'messages': "Search test: qwerty"
    }
    second_msg = {
        'token': user_1_token,
        'channel_id': channel_id,
        'messages': "Search test: asdfgh"
    }

    requests.post(f'{url}/message/send', json=first_msg)
    requests.post(f'{url}/message/send', json=second_msg)

    return user_1_token


@pytest.fixture
def register_two_users(url):
    # register two users
    user_1 = {
        'email': 'vicky@gmail.com',
        'password': '1234567',
        'name_first': 'Vicky',
        'name_last': 'Hu',
    }

    user_1_detail_json = requests.post(f'{url}/auth/register', json=user_1)
    user_1_detail = user_1_detail_json.json()
    user_1_token = user_1_detail['token']

    return user_1_token


###################################### user_permission_change ################################

def test_permission_not_global_owner_http(url, register_create_channel):
    user_detail_1 = register_create_channel[0]
    user_detail_2 = register_create_channel[1]
    token_2 = user_detail_2['token']
    u_1_id = user_detail_1['u_id']

    permission_1 = {
        'token': token_2,
        'u_id': u_1_id,
        'permission_id': members
    }
    response = requests.post(
        f'{url}/admin/userpermission/change', json=permission_1)
    assert response.status_code == 400

    user_detail_3 = register_create_channel[2]
    u_3_id = user_detail_3['u_id']

    permission_2 = {
        'token': token_2,
        'u_id': u_3_id,
        'permission_id': owners
    }
    response = requests.post(
        f'{url}/admin/userpermission/change', json=permission_2)
    assert response.status_code == 400


def test_permission_invalid_user_http(url, register_create_channel):
    user_detail_1 = register_create_channel[0]
    token_1 = user_detail_1['token']

    permission = {
        'token': token_1,
        'u_id': INVALID_ID,
        'permission_id': owners
    }

    response = requests.post(
        f'{url}/admin/userpermission/change', json=permission)
    assert response.status_code == 400


def test_permission_invalid_permission_http(url, register_create_channel):
    user_detail_1 = register_create_channel[0]
    token_1 = user_detail_1['token']

    user_detail_2 = register_create_channel[1]
    u_2_id = user_detail_2['u_id']

    invalid_permission = 3
    permission = {
        'token': token_1,
        'u_id': u_2_id,
        'permission_id': invalid_permission
    }
    response = requests.post(
        f'{url}/admin/userpermission/change', json=permission)
    assert response.status_code == 400


def test_permission_global_owner_http(url, register_create_channel):
    user_detail_1 = register_create_channel[0]
    token_1 = user_detail_1['token']

    user_detail_2 = register_create_channel[1]
    u_2_id = user_detail_2['u_id']

    permission_1 = {
        'token': token_1,
        'u_id': u_2_id,
        'permission_id': owners
    }

    response_1 = requests.post(
        f'{url}/admin/userpermission/change', json=permission_1)
    assert response_1.status_code == 200

    permission_2 = {
        'token': token_1,
        'u_id': u_2_id,
        'permission_id': members
    }

    response_2 = requests.post(
        f'{url}/admin/userpermission/change', json=permission_2)
    assert response_2.status_code == 200


def test_search_http(url, register_channel_message):
    token_1 = register_channel_message
    token = {
        'token': token_1,
    }
    response = requests.get(f'{url}/search', params=token)
    assert response.status_code == 200


def test_search_invalid_token_http(url):
    token = {
        'token': -1,
    }
    response = requests.get(f'{url}/search', params=token)
    assert response.status_code == 400


def test_channel_users_all_http(url, register_two_users):
    token_1 = register_two_users
    token = {
        'token': token_1,
    }
    response = requests.get(f'{url}/users/all', params=token)
    assert response.status_code == 200


def test_users_all_invalid_token_http(url):
    token = {
        'token': -1,
    }
    response = requests.get(f'{url}/users/all', params=token)
    assert response.status_code == 400
