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
# Use this fixture to get the URL of the server. sIt starts the server for you,
# so you don't need to.
owners = 1
members = 2


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
    user2_token = user_2_detail['token']

    first_channel = {
        'token': user1_token,
        'name': 'cctv1',
        'is_public': True
    }

    channel_info1_json = requests.post(
        f'{url}/channels/create', json=first_channel)
    channel_info1 = channel_info1_json.json()

    second_channel = {
        'token': user2_token,
        'name': 'cctv2',
        'is_public': True
    }
    channel_info2_json = requests.post(
        f'{url}/channels/create', json=second_channel)
    channel_info2 = channel_info2_json.json()

    return user_1_detail, user_2_detail, channel_info1, channel_info2

################################### channels_list ###########################################


def test_channels_list_none_http(url):
    '''
    Test that an authorised user belongs to no channel
    '''
    first_user = {
        'email': 'celine@gmail.com',
        'password': '123456',
        'name_first': 'Celine',
        'name_last': 'Lin',
    }
    user_1_detail_json = requests.post(f'{url}/auth/register', json=first_user)
    user_1_detail = user_1_detail_json.json()
    user_1_token = user_1_detail['token']

    response = requests.get(f'{url}/channels/list',
                            params={'token': user_1_token})
    assert response.status_code == 200
    channel_list = response.json()
    assert channel_list['channels'] == []


def test_channels_list_not_owner_http(url, register_create_channel):
    '''
    Test to display the channels even if the user is not the owner of any ones
    '''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']
    u_1_id = user_1_detail['u_id']

    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    # Invite the first user to the channel
    invite_1 = {
        'token': user_2_token,
        'channel_id': channel_1_id,
        'u_id': u_1_id,
    }

    requests.post(f'{url}/channel/invite', json=invite_1)

    response = requests.get(f'{url}/channels/list',
                            params={'token': user_1_token})
    assert response.status_code == 200

    # The first user created one channel and was invited to another, therefore three in total
    channel_list = response.json()
    assert len(channel_list['channels']) == 2


def test_channels_list_is_owner(url, register_create_channel):
    '''
    Test that the input user is the owner of some channels
    '''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    response = requests.get(f'{url}/channels/list',
                            params={'token': user_1_token})
    assert response.status_code == 200

    channel_list = response.json()
    assert len(channel_list['channels']) == 1


def test_channels_list_isprivate(url, register_create_channel):
    '''
    Test if the returned list of channels include private ones
    '''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    response = requests.get(f'{url}/channels/list',
                            params={'token': user_1_token})
    assert response.status_code == 200

    channel_list = response.json()
    assert len(channel_list['channels']) == 1


# TODO: Test if an authorised user logged out, exception raises
def test_channels_list_logged_out(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    response = requests.post(f'{url}/auth/logout',
                             json={'token': user_1_token})
    assert response.status_code == 200

    response = requests.get(f'{url}/channels/list',
                            params={'token': user_1_token})
    assert response.status_code == 400


##### TESTS FOR channels_listall #####

# TODO: Test that an authorised user who are logged out will raise exception


def test_channels_listall_logged_out_http(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    response = requests.post(f'{url}/auth/logout',
                             json={'token': user_1_token})
    assert response.status_code == 200

    response = requests.get(f'{url}/channels/listall',
                            params={'token': user_1_token})
    assert response.status_code == 400


def test_channels_listall_no_channels(url):
    '''
    Test that an empty list will be returned if no channel has been created
    '''
    first_user = {
        'email': 'celine@gmail.com',
        'password': '123456',
        'name_first': 'Celine',
        'name_last': 'Lin',
    }
    user_1_detail_json = requests.post(f'{url}/auth/register', json=first_user)
    user_1_detail = user_1_detail_json.json()
    user_1_token = user_1_detail['token']

    response = requests.get(f'{url}/channels/listall',
                            params={'token': user_1_token})
    assert response.status_code == 200

    channel_list = response.json()
    assert len(channel_list['channels']) == 0


def test_channels_listall_valid_user_http(url, register_create_channel):
    '''
    Test that list all channels if the token is authorised
    '''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    response = requests.get(f'{url}/channels/listall',
                            params={'token': user_1_token})
    assert response.status_code == 200

    channel_list = response.json()
    assert len(channel_list['channels']) == 2


########################### channels_create #############################
# TODO: Test if an authorised user who is logged out cannot create a new channel, raises exception
def test_channels_create_logged_out_http(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    response = requests.post(f'{url}/auth/logout',
                             json={'token': user_1_token})
    assert response.status_code == 200

    new_channel = {
        'token': user_1_token,
        'name': 'new',
        'is_public': True,
    }
    response = requests.post(f'{url}/channels/create',
                             json=new_channel)
    assert response.status_code == 400


def test_channels_create_short_pub_http(url):
    '''
    Test that a new public channel is created by a valid token with its name less than 20 characters
    '''
    first_user = {
        'email': 'celine@gmail.com',
        'password': '123456',
        'name_first': 'Celine',
        'name_last': 'Lin',
    }
    user_1_detail_json = requests.post(f'{url}/auth/register', json=first_user)
    user_1_detail = user_1_detail_json.json()
    user1_token = user_1_detail['token']

    first_channel = {
        'token': user1_token,
        'name': 'cctv1',
        'is_public': True
    }

    channel_info1_json = requests.post(
        f'{url}/channels/create', json=first_channel)
    channel_info1 = channel_info1_json.json()
    channel_id = channel_info1['channel_id']

    assert channel_info1_json.status_code == 200
    assert channel_id == 0


def test_channels_create_short_pri_http(url):
    '''
    Test that a new private channel is created by a valid token with its name less than 20 characters
    '''
    first_user = {
        'email': 'celine@gmail.com',
        'password': '123456',
        'name_first': 'Celine',
        'name_last': 'Lin',
    }
    user_1_detail_json = requests.post(f'{url}/auth/register', json=first_user)
    user_1_detail = user_1_detail_json.json()
    user1_token = user_1_detail['token']

    first_channel = {
        'token': user1_token,
        'name': 'cctv1',
        'is_public': False
    }

    channel_info1_json = requests.post(
        f'{url}/channels/create', json=first_channel)
    channel_info1 = channel_info1_json.json()
    channel_id = channel_info1['channel_id']

    assert channel_info1_json.status_code == 200
    assert channel_id == 0


def test_channels_create_20_pri_http(url, register_create_channel):
    '''
    Test that a new private channel is created by a valid token with its name with 20 characters
    '''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    first_channel = {
        'token': user_1_token,
        'name': 'ThisChannelHasName20',
        'is_public': False
    }

    channel_info1_json = requests.post(
        f'{url}/channels/create', json=first_channel)
    channel_info1 = channel_info1_json.json()
    channel_id = channel_info1['channel_id']

    assert channel_info1_json.status_code == 200
    assert channel_id >= 0


def test_channels_create_long_pub_http(url, register_create_channel):
    '''
    Test that a new public channel created with its name more than 20 characters will raise InputError
    '''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    first_channel = {
        'token': user_1_token,
        'name': 'new----channels---larger---than---20---char',
        'is_public': True
    }
    channel_info1_json = requests.post(
        f'{url}/channels/create', json=first_channel)

    assert channel_info1_json.status_code == 400


def test_channels_create_long_pri_http(url, register_create_channel):
    '''
    Test that a new private channel created 
    with its name more than 20 characters will raise InputError
    '''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    first_channel = {
        'token': user_1_token,
        'name': 'new----channels---larger---than---20---char',
        'is_public': False
    }
    channel_info1_json = requests.post(
        f'{url}/channels/create', json=first_channel)

    assert channel_info1_json.status_code == 400
