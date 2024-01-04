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

    third_channel = {
        'token': user1_token,
        'name': 'cctv3',
        'is_public': False
    }

    channel_info3_json = requests.post(
        f'{url}/channels/create', json=third_channel)
    channel_info3 = channel_info3_json.json()

    return user_1_detail, user_2_detail, user_3_detail, channel_info1, channel_info2, channel_info3


@pytest.fixture
def channel_create_addowner(url, register_create_channel):
    user_1_token = register_create_channel[0]['token']
    channel_id = register_create_channel[3]['channel_id']
    user_2_u_id = register_create_channel[1]['u_id']
    # make user_2 an owner
    addowner = {
        'token': user_1_token,
        'channel_id': channel_id,
        'u_id': user_2_u_id,
    }
    addowner_json = requests.post(f'{url}/channel/addowner', json=addowner)
    addowner_json.json()

    return user_1_token, channel_id, user_2_u_id


################################### channel_invite #####################################

def test_channel_invite_InputError_http(url, register_create_channel):
    # clear()
    user_detail_1 = register_create_channel[0]
    user_detail_2 = register_create_channel[1]
    channel_1 = register_create_channel[3]
    user1_token = user_detail_1['token']

    channel_id1 = channel_1['channel_id']

    user2_id = user_detail_2['u_id']

    INVALID_ID = -1
    invite_info1 = {
        'token': user1_token,
        'channel_id': INVALID_ID,
        'u_id': user2_id,
    }
    # with pytest.raises(InputError):
    response_1 = requests.post(f'{url}/channel/invite', json=invite_info1)
    assert response_1.status_code == 400

    invite_info2 = {
        'token': user1_token,
        'channel_id': channel_id1,
        'u_id': INVALID_ID
    }
    response_2 = requests.post(f'{url}/channel/invite', json=invite_info2)
    assert response_2.status_code == 400


def test_channel_invite_AccessError_http(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_2_detail = register_create_channel[1]
    user_3_detail = register_create_channel[2]
    channel_info1 = register_create_channel[3]
    channel_info2 = register_create_channel[4]

    user1_token = user_1_detail['token']

    user2_token = user_2_detail['token']
    user2_id = user_2_detail['u_id']

    user3_id = user_3_detail['u_id']

    channel_id1 = channel_info1['channel_id']
    channel_id2 = channel_info2['channel_id']

    invite_1 = {
        'token': user2_token,
        'channel_id': channel_id1,
        'u_id': user3_id,
    }

    response_1 = requests.post(f'{url}/channel/invite', json=invite_1)
    assert response_1.status_code == 400

    invite_2 = {
        'token': user1_token,
        'channel_id': channel_id1,
        'u_id': user2_id,
    }

    response_2 = requests.post(f'{url}/channel/invite', json=invite_2)
    assert response_2.status_code == 200

    invite_3 = {
        'token': user2_token,
        'channel_id': channel_id2,
        'u_id': user3_id,
    }

    response_1 = requests.post(f'{url}/channel/invite', json=invite_3)
    assert response_1.status_code == 400


def test_channel_invite_duplicate_case_http(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']
    u_1_id = user_1_detail['u_id']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    invite_1 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'u_id': u_1_id,
    }

    response = requests.post(f'{url}/channel/invite', json=invite_1)
    assert response.status_code == 200
    details = {
        'token': user_1_token,
        'channel_id': channel_1_id,
    }
    response = requests.get(f'{url}/channel/details', params=details)
    assert response.status_code == 200
    assert response.json() == {
        'name': 'cctv1',
        'owner_members': [
            {
                'u_id': u_1_id,
                'name_first': 'Celine',
                'name_last': 'Lin',
                'profile_img_url': "",
            }
        ],
        'all_members': [
            {
                'u_id': u_1_id,
                'name_first': 'Celine',
                'name_last': 'Lin',
                'profile_img_url': "",
            },
        ],
    }


def test_channel_invite_public_case_http(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']
    user_1_id = user_1_detail['u_id']

    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']

    user_3_detail = register_create_channel[2]
    u_3_id = user_3_detail['u_id']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    invite_1 = {
        'token': user_2_token,
        'channel_id': channel_1_id,
        'u_id': u_3_id,
    }

    response = requests.post(f'{url}/channel/invite', json=invite_1)
    assert response.status_code == 400

    invite_2 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'u_id': u_3_id,
    }

    response = requests.post(f'{url}/channel/invite', json=invite_2)
    assert response.status_code == 200

    details = {
        'token': user_1_token,
        'channel_id': channel_1_id,
    }
    response = requests.get(f'{url}/channel/details', params=details)
    assert response.status_code == 200
    assert response.json() == {
        'name': 'cctv1',
        'owner_members': [
            {
                'u_id': user_1_id,
                'name_first': 'Celine',
                'name_last': 'Lin',
                'profile_img_url': "",
            }
        ],
        'all_members': [
            {
                'u_id': user_1_id,
                'name_first': 'Celine',
                'name_last': 'Lin',
                'profile_img_url': "",
            },

            {
                'u_id': u_3_id,
                'name_first': 'Peter',
                'name_last': 'Xie',
                'profile_img_url': "",
            },

        ],
    }


def test_channel_invite_private_case_http(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']
    u_1_id = user_1_detail['u_id']

    user_2_detail = register_create_channel[1]
    u_2_id = user_2_detail['u_id']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    invite_1 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'u_id': u_2_id,
    }

    response = requests.post(f'{url}/channel/invite', json=invite_1)
    assert response.status_code == 200

    details = {
        'token': user_1_token,
        'channel_id': channel_1_id
    }
    response = requests.get(f'{url}/channel/details', params=details)
    assert response.status_code == 200
    assert response.json() == {
        'name': 'cctv1',
        'owner_members': [
            {
                'u_id': u_1_id,
                'name_first': 'Celine',
                'name_last': 'Lin',
                'profile_img_url': "",
            }
        ],
        'all_members': [
            {
                'u_id': u_1_id,
                'name_first': 'Celine',
                'name_last': 'Lin',
                'profile_img_url': "",
            },

            {
                'u_id': u_2_id,
                'name_first': 'Theresa',
                'name_last': 'Tao',
                'profile_img_url': "",
            },

        ],
    }

##################################### channel_details #############################################


def test_channel_details_InputError_http(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    detail_1 = {
        'token': user_1_token,
        'channel_id': INVALID_ID,
    }
    response = requests.get(f'{url}/channel/details', params=detail_1)
    assert response.status_code == 400


def test_channel_details_AccessError_http(url, register_create_channel):
    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']

    channel_1 = register_create_channel[3]
    channel_id = channel_1['channel_id']

    detail = {
        'token': user_2_token,
        'channel_id': channel_id,
    }

    response = requests.get(f'{url}/channel/details', params=detail)
    assert response.status_code == 400


def test_channel_details_http(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']
    user_1_id = user_1_detail['u_id']
    user_2_detail = register_create_channel[1]
    user_2_id = user_2_detail['u_id']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    invite = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'u_id': user_2_id,
    }

    response = requests.post(f'{url}/channel/invite', json=invite)
    assert response.status_code == 200
    print(user_1_token, channel_1_id)
    response = requests.get(
        f'{url}/channel/details', params={'token': user_1_token, 'channel_id': channel_1_id})
    assert response.status_code == 200

    assert response.json() == {
        'name': 'cctv1',
        'owner_members': [
            {
                'u_id': user_1_id,
                'name_first': 'Celine',
                'name_last': 'Lin',
                'profile_img_url': "",
            }
        ],
        'all_members': [
            {
                'u_id': user_1_id,
                'name_first': 'Celine',
                'name_last': 'Lin',
                'profile_img_url': "",
            },

            {
                'u_id': user_2_id,
                'name_first': 'Theresa',
                'name_last': 'Tao',
                'profile_img_url': "",
            },

        ],
    }
####################################### channel_messages ###########################################


def test_channel_messages_InputError(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    message_1 = {
        'token': user_1_token,
        'channel_id': INVALID_ID,
        'start': 0
    }
    response = requests.get(f'{url}/channel/messages', params=message_1)
    assert response.status_code == 400

    message_2 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'start': 1,
    }
    response = requests.get(f'{url}/channel/messages', params=message_2)
    assert response.status_code == 400

    message_3 = {
        'token': user_2_token,
        'channel_id': channel_1_id,
        'start': 5
    }
    response = requests.get(f'{url}/channel/messages', params=message_3)
    assert response.status_code == 400


def test_channel_messages_AccessError_http(url, register_create_channel):
    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    messages = {
        'token': user_2_token,
        'channel_id': channel_1_id,
        'start': 0
    }
    response = requests.get(f'{url}/channel/messages', params=messages)
    assert response.status_code == 400


def test_channel_leave_InputError(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    leave_1 = {
        'token': None,
        'channel_id': channel_1_id
    }

    leave_2 = {
        'token': None,
        'channel_id': 99
    }

    leave_3 = {
        'token': user_1_token,
        'channel_id': 99
    }

    response = requests.post(f'{url}/channel/leave', json=leave_1)
    assert response.status_code == 400

    response = requests.post(f'{url}/channel/leave', json=leave_2)
    assert response.status_code == 400

    response = requests.post(f'{url}/channel/leave', json=leave_3)
    assert response.status_code == 400


def test_channel_leave_AccessError(url, register_create_channel):
    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    leave_1 = {
        'token': user_2_token,
        'channel_id': channel_1_id
    }

    response = requests.post(f'{url}/channel/leave', json=leave_1)
    assert response.status_code == 400


def test_channel_leave_allowed(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    leave = {
        'token': user_1_token,
        'channel_id': channel_1_id
    }

    response = requests.post(f'{url}/channel/leave', json=leave)
    assert response.status_code == 200


def test_channel_join_InputError(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    join_1 = {
        'token': None,
        'channel_id': channel_1_id
    }

    join_2 = {
        'token': None,
        'channel_id': 99
    }

    join_3 = {
        'token': user_1_token,
        'channel_id': 99
    }

    response = requests.post(f'{url}/channel/join', json=join_1)
    assert response.status_code == 400

    response = requests.post(f'{url}/channel/join', json=join_2)
    assert response.status_code == 400

    response = requests.post(f'{url}/channel/join', json=join_3)
    assert response.status_code == 400


def test_channel_join_AccessError(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    join_1 = {
        'token': user_1_token,
        'channel_id': channel_1_id
    }

    response = requests.post(f'{url}/channel/join', json=join_1)
    assert response.status_code == 400


def test_channel_join_private_AccessError(url, register_create_channel):
    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']

    channel_3 = register_create_channel[5]
    channel_3_id = channel_3['channel_id']

    join_1 = {
        'token': user_2_token,
        'channel_id': channel_3_id
    }

    response = requests.post(f'{url}/channel/join', json=join_1)
    assert response.status_code == 400


def test_channel_join_allowed(url, register_create_channel):
    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']

    user_3_detail = register_create_channel[2]
    user_3_token = user_3_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    join_1 = {
        'token': user_2_token,
        'channel_id': channel_1_id
    }

    join_2 = {
        'token': user_3_token,
        'channel_id': channel_1_id
    }

    response = requests.post(f'{url}/channel/join', json=join_1)
    assert response.status_code == 200

    response = requests.post(f'{url}/channel/join', json=join_2)
    assert response.status_code == 200

######################################### channel_addowner ##########################################


def test_channel_addowner_http(url, register_create_channel):
    user_detail_1 = register_create_channel[0]
    user_detail_2 = register_create_channel[1]
    token_1 = user_detail_1['token']
    u_2_id = user_detail_2['u_id']

    channel = register_create_channel[3]
    channel_id = channel['channel_id']
    addowner = {
        'token': token_1,
        'channel_id': channel_id,
        'u_id': u_2_id,
    }
    response = requests.post(f'{url}/channel/addowner', json=addowner)
    assert response.status_code == 200


def test_channel_addowner_invalid_u_id_http(url, channel_create_addowner):
    user_1_token = channel_create_addowner[0]
    channel_id = channel_create_addowner[1]
    removeowner = {
        'token': user_1_token,
        'channel_id': channel_id,
        'u_id': -1,
    }

    response = requests.post(f'{url}/channel/removeowner', json=removeowner)
    assert response.status_code == 400


def test_channel_addowner_invalid_token_http(url, channel_create_addowner):
    channel_id = channel_create_addowner[1]
    user_2_u_id = channel_create_addowner[2]
    removeowner = {
        'token': -1,
        'channel_id': channel_id,
        'u_id': user_2_u_id,
    }

    response = requests.post(f'{url}/channel/removeowner', json=removeowner)
    assert response.status_code == 400


def test_channel_addowner_invalid_channel_id(url, channel_create_addowner):
    user_1_token = channel_create_addowner[0]
    user_2_u_id = channel_create_addowner[2]
    removeowner = {
        'token': user_1_token,
        'channel_id': -1,
        'u_id': user_2_u_id,
    }

    response = requests.post(f'{url}/channel/removeowner', json=removeowner)
    assert response.status_code == 400


# ==============================CHANNEL_REMOVEOWNER===================================
def test_channel_removeowner_http(url, channel_create_addowner):
    user_1_token, channel_id, user_2_u_id = channel_create_addowner
    removeowner = {
        'token': user_1_token,
        'channel_id': channel_id,
        'u_id': user_2_u_id,
    }

    response = requests.post(f'{url}/channel/removeowner', json=removeowner)
    assert response.status_code == 200


def test_channel_removeowner_invalid_u_id_http(url, channel_create_addowner):
    user_1_token = channel_create_addowner[0]
    channel_id = channel_create_addowner[1]
    removeowner = {
        'token': user_1_token,
        'channel_id': channel_id,
        'u_id': -1,
    }

    response = requests.post(f'{url}/channel/removeowner', json=removeowner)
    assert response.status_code == 400


def test_channel_removeowner_invalid_token_http(url, channel_create_addowner):
    channel_id = channel_create_addowner[1]
    user_2_u_id = channel_create_addowner[2]
    removeowner = {
        'token': -1,
        'channel_id': channel_id,
        'u_id': user_2_u_id,
    }

    response = requests.post(f'{url}/channel/removeowner', json=removeowner)
    assert response.status_code == 400


def test_channel_removeowner_invalid_channel_id(url, channel_create_addowner):
    user_1_token = channel_create_addowner[0]
    user_2_u_id = channel_create_addowner[2]
    removeowner = {
        'token': user_1_token,
        'channel_id': -1,
        'u_id': user_2_u_id,
    }

    response = requests.post(f'{url}/channel/removeowner', json=removeowner)
    assert response.status_code == 400
