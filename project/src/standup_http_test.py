from datetime import datetime, timedelta, timezone
from Global_variables import *
from error import *
from auth import SECRET
import jwt
import json
import requests
from time import sleep
import signal
from subprocess import Popen, PIPE
import re
import pytest


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
def register_user_create_channel(url):
    # clear()

    user = {
        'email': 'celine@gmail.com',
        'password': '123456',
        'name_first': 'Celine',
        'name_last': 'Lin',
    }
    user_detail_json = requests.post(f"{url}/auth/register", json=user)
    user_detail = user_detail_json.json()
    token = user_detail['token']

    channel = {
        'token': token,
        'name': 'OwnedByCeline',
        'is_public': True
    }

    channel_info_json = requests.post(
        f'{url}/channels/create', json=channel)
    channel_info = channel_info_json.json()
    channel_id = channel_info['channel_id']

    return token, channel_id

################################ standup_start ####################################


def test_standup_invalid_channel_id_http(url, register_user_create_channel):
    token = register_user_create_channel[0]
    invalid_channel_id = {
        'token': token,
        'channel_id': -1,
        'length': 60,
    }
    response = requests.post(f"{url}/standup/start", json=invalid_channel_id)
    assert response.status_code == 400


def test_standup_invalid_token_http(url, register_user_create_channel):
    channel_id = register_user_create_channel[1]
    invalid_token = {
        'token': "",
        'channel_id': channel_id,
        'length': 60
    }
    response = requests.post(f"{url}/standup/start", json=invalid_token)
    assert response.status_code == 400


def test_standup_start_not_member_http(url, register_user_create_channel):
    channel_id = register_user_create_channel[1]

    not_mem = {
        'email': 'peter@gmail.com',
        'password': '123456',
        'name_first': 'Peter',
        'name_last': 'Xie',
    }

    not_mem_detail_json = requests.post(f"{url}/auth/register", json=not_mem)
    not_mem_detail = not_mem_detail_json.json()
    not_mem_token = not_mem_detail['token']

    not_mem_standup = {
        'token': not_mem_token,
        'channel_id': channel_id,
        'length': 60
    }
    response = requests.post(f"{url}/standup/start", json=not_mem_standup)
    assert response.status_code == 400


def test_standup_active_already_owner_http(url, register_user_create_channel):
    '''
    An owner of the channel cannot start a standup when one is already active
    '''
    token = register_user_create_channel[0]
    channel_id = register_user_create_channel[1]

    standup = {
        'token': token,
        'channel_id': channel_id,
        'length': 60
    }
    response = requests.post(f"{url}/standup/start", json=standup)
    assert response.status_code == 200

    standup_again = {
        'token': token,
        'channel_id': channel_id,
        'length': 60
    }
    response = requests.post(f"{url}/standup/start", json=standup_again)
    assert response.status_code == 400


def test_standup_active_already_member_http(url, register_user_create_channel):
    '''
    A member of the channel cannot start a standup when one is already active
    '''
    token = register_user_create_channel[0]
    channel_id = register_user_create_channel[1]

    mem = {
        'email': 'peter@gmail.com',
        'password': '123456',
        'name_first': 'Peter',
        'name_last': 'Xie',
    }

    mem_detail_json = requests.post(f"{url}/auth/register", json=mem)
    mem_detail = mem_detail_json.json()
    mem_token = mem_detail['token']
    mem_id = mem_detail['u_id']

    invite = {
        'token': token,
        'channel_id': channel_id,
        'u_id': mem_id,
    }

    requests.post(f"{url}/channel/invite", json=invite)

    standup = {
        'token': mem_token,
        'channel_id': channel_id,
        'length': 60
    }
    response = requests.post(f"{url}/standup/start", json=standup)
    assert response.status_code == 200

    standup_again = {
        'token': mem_token,
        'channel_id': channel_id,
        'length': 60
    }
    response = requests.post(f"{url}/standup/start", json=standup_again)
    assert response.status_code == 400


def test_standup_owner_successfully_http(url, register_user_create_channel):
    '''
    An owner of the channel can start a standup if no error occurred
    '''
    token = register_user_create_channel[0]
    channel_id = register_user_create_channel[1]

    standup_check_active = {
        'token': token,
        'channel_id': channel_id,
    }
    response = requests.get(f"{url}/standup/active",
                            params=standup_check_active)
    assert response.status_code == 200
    assert not response.json()['is_active']

    length = 60
    discrepancy = 1
    standup = {
        'token': token,
        'channel_id': channel_id,
        'length': 60
    }
    response = requests.post(f"{url}/standup/start", json=standup)
    assert response.status_code == 200
    assert response.json()['time_finish'] > (datetime.utcnow(
    ) + timedelta(seconds=length - discrepancy)).replace(tzinfo=timezone.utc).timestamp()

    response = requests.get(f"{url}/standup/active",
                            params=standup_check_active)
    assert response.status_code == 200
    assert response.json()['is_active']


def test_standup_member_successfully_http(url, register_user_create_channel):
    token = register_user_create_channel[0]
    channel_id = register_user_create_channel[1]

    mem = {
        'email': 'peter@gmail.com',
        'password': '123456',
        'name_first': 'Peter',
        'name_last': 'Xie',
    }

    mem_detail_json = requests.post(f"{url}/auth/register", json=mem)
    mem_detail = mem_detail_json.json()
    mem_token = mem_detail['token']
    mem_id = mem_detail['u_id']

    invite = {
        'token': token,
        'channel_id': channel_id,
        'u_id': mem_id,
    }

    requests.post(f"{url}/channel/invite", json=invite)

    standup_check_active = {
        'token': token,
        'channel_id': channel_id,
    }
    response = requests.get(f"{url}/standup/active",
                            params=standup_check_active)
    assert response.status_code == 200
    assert not response.json()['is_active']

    length = 60
    discrepancy = 1
    standup = {
        'token': mem_token,
        'channel_id': channel_id,
        'length': 60
    }
    response = requests.post(f"{url}/standup/start", json=standup)
    assert response.status_code == 200
    assert response.json()['time_finish'] > (datetime.utcnow(
    ) + timedelta(seconds=length - discrepancy)).replace(tzinfo=timezone.utc).timestamp()

    response = requests.get(f"{url}/standup/active",
                            params=standup_check_active)
    assert response.status_code == 200
    assert response.json()['is_active']


############################## standup_active #####################################
def test_standup_active_invalid_channel_id_http(url, register_user_create_channel):
    '''
    Invalid channel_id will raise InputError
    '''
    token = register_user_create_channel[0]

    standup_check_active = {
        'token': token,
        'channel_id': -1,
    }
    response = requests.get(f"{url}/standup/active",
                            params=standup_check_active)
    assert response.status_code == 400


def test_standup_active_invalid_token_http(url, register_user_create_channel):
    '''
    Invalid token will raise AccessError
    '''
    channel_id = register_user_create_channel[1]
    standup_check_active = {
        'token': "",
        'channel_id': channel_id,
    }
    response = requests.get(f"{url}/standup/active",
                            params=standup_check_active)
    assert response.status_code == 400


def test_standup_active_owner_http(url, register_user_create_channel):
    '''
    An owner of the channel can see if a standup is happening in this channel
    '''
    token = register_user_create_channel[0]
    channel_id = register_user_create_channel[1]

    standup_check_active = {
        'token': token,
        'channel_id': channel_id,
    }
    response = requests.get(f"{url}/standup/active",
                            params=standup_check_active)
    assert response.status_code == 200
    assert not response.json()['is_active']

    standup = {
        'token': token,
        'channel_id': channel_id,
        'length': 60
    }
    response = requests.post(f"{url}/standup/start", json=standup)
    assert response.status_code == 200

    response = requests.get(f"{url}/standup/active",
                            params=standup_check_active)
    assert response.status_code == 200
    assert response.json()['is_active']


def test_standup_active_member_http(url, register_user_create_channel):
    '''
    A member of the channel can see if a standup is happening in this channel
    '''
    token = register_user_create_channel[0]
    channel_id = register_user_create_channel[1]

    mem = {
        'email': 'peter@gmail.com',
        'password': '123456',
        'name_first': 'Peter',
        'name_last': 'Xie',
    }

    mem_detail_json = requests.post(f"{url}/auth/register", json=mem)
    mem_detail = mem_detail_json.json()
    mem_token = mem_detail['token']
    mem_id = mem_detail['u_id']

    invite = {
        'token': token,
        'channel_id': channel_id,
        'u_id': mem_id,
    }

    requests.post(f"{url}/channel/invite", json=invite)

    standup_check_active = {
        'token': mem_token,
        'channel_id': channel_id,
    }
    response = requests.get(f"{url}/standup/active",
                            params=standup_check_active)
    assert response.status_code == 200
    assert not response.json()['is_active']

    standup = {
        'token': token,
        'channel_id': channel_id,
        'length': 60
    }
    requests.post(f"{url}/stadup/start", json=standup)

    response = requests.get(f"{url}/standup/active",
                            params=standup_check_active)
    assert response.status_code == 200
    assert not response.json()['is_active']


def test_standup_active_not_member_http(url, register_user_create_channel):
    '''
    A user who is not a member of the channel cannot use this feature
    '''
    channel_id = register_user_create_channel[1]

    not_mem = {
        'email': 'peter@gmail.com',
        'password': '123456',
        'name_first': 'Peter',
        'name_last': 'Xie',
    }

    not_mem_detail_json = requests.post(f"{url}/auth/register", json=not_mem)
    not_mem_detail = not_mem_detail_json.json()
    not_mem_token = not_mem_detail['token']

    standup_check_active = {
        'token': not_mem_token,
        'channel_id': channel_id,
    }
    response = requests.get(f"{url}/standup/active",
                            params=standup_check_active)
    assert response.status_code == 400


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
    user2_token = user_2_detail['token']

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
        'token': user2_token,
        'name': 'cctv3',
        'is_public': True
    }
    channel_info3_json = requests.post(
        f'{url}/channels/create', json=third_channel)
    channel_info3 = channel_info3_json.json()

    return user_1_detail, user_2_detail, user_3_detail, channel_info1, channel_info2, channel_info3


def test_standup_send_invalid_token(url, register_create_channel):
    '''
    Test standup send invalid token
    '''
    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']

    message = 'Test message'

    sent_packet_1 = {
        'token': user_2_token,
        'channel_id': channel_1_id,
        'message': message
    }

    sent_packet_2 = {
        'token': None,
        'channel_id': channel_1_id,
        'message': message
    }

    response = requests.post(f'{url}/standup/send', json=sent_packet_2)
    assert response.status_code == 400
    response = requests.post(f'{url}/standup/send', json=sent_packet_1)
    assert response.status_code == 400


def test_standup_send_invalid_channel_id(url, register_create_channel):
    '''
    Test standup send invalid channel
    '''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    message = 'Test message'

    sent_packet_1 = {
        'token': user_1_token,
        'channel_id': -1,
        'message': message
    }

    sent_packet_2 = {
        'token': user_1_token,
        'channel_id': 99,
        'message': message
    }

    response = requests.post(f'{url}/standup/send', json=sent_packet_1)
    assert response.status_code == 400

    response = requests.post(f'{url}/standup/send', json=sent_packet_2)
    assert response.status_code == 400


def test_standup_send_more_than_1000_chars_or_none(url, register_create_channel):
    '''
    Test invalid message
    '''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    message_long = 'This is over 1000 chars' * 1000
    message_none = ''

    sent_packet_1 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'message': message_long
    }

    sent_packet_2 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'message': message_none
    }

    response = requests.post(f'{url}/standup/send', json=sent_packet_1)
    assert response.status_code == 400

    response = requests.post(f'{url}/standup/send', json=sent_packet_2)
    assert response.status_code == 400


def test_standup_send_not_currently_active(url, register_create_channel):
    '''
    Test standup not active
    '''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    message = 'Test message'

    sent_packet_1 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'message': message
    }

    response = requests.post(f'{url}/standup/send', json=sent_packet_1)
    assert response.status_code == 400


def test_standup_send_currently_active(url, register_create_channel):
    '''
    Test standup active valid for standup send
    '''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    message = 'Test message'

    sent_packet_1 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'message': message
    }

    sent_packet_start = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'length': 60
    }

    requests.post(f'{url}/standup/start', json=sent_packet_start)

    response = requests.post(f'{url}/standup/send', json=sent_packet_1)
    assert response.status_code == 200
