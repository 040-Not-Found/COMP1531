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
from datetime import datetime, timezone, timedelta
from Global_variables import *
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


########################################### message_send ###############################################


def test_over_length_http(url, register_create_channel):
    ''' test for the case that the message is over 1000 chars'''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']
    user_2_id = user_2_detail['u_id']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    long_string = 'I am over length!' * 100
    # case that an owner send an over_length message
    send_1 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'message': long_string
    }
    response = requests.post(f'{url}/message/send', json=send_1)
    assert response.status_code == 400

    invite_1 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'u_id': user_2_id,
    }
    response = requests.post(f'{url}/channel/invite', json=invite_1)
    assert response.status_code == 200
    # case that the mem in channnel but not owner send an over_length message
    send_2 = {
        'token': user_2_token,
        'channel_id': channel_1_id,
        'message': long_string
    }
    response = requests.post(f'{url}/message/send', json=send_2)
    assert response.status_code == 400

# TODO: check fixture


def test_not_in_channel_http(url):
    ''' test that the person is not authorised in the channel'''
    '''user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']'''
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
    user_2_token = user_2_detail['token']

    first_channel = {
        'token': user1_token,
        'name': 'cctv1',
        'is_public': True
    }

    channel_info1_json = requests.post(
        f'{url}/channels/create', json=first_channel)
    channel_info1 = channel_info1_json.json()
    channel_1_id = channel_info1['channel_id']

    send = {
        'token': user_2_token,
        'channel_id': channel_1_id,
        'message': 'Hello World!'
    }
    response = requests.post(f'{url}/message/send', json=send)
    assert response.status_code == 400


def test_not_in_channel_over_length_http(url, register_create_channel):
    ''' case that the person not in channel and send an overlength message'''

    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    long_string = 'I am over length!' * 100
    # case that an owner send an over_length message
    send_1 = {
        'token': user_2_token,
        'channel_id': channel_1_id,
        'message': long_string
    }
    response = requests.post(f'{url}/message/send', json=send_1)
    assert response.status_code == 400


def test_channel_is_not_exist_http(url, register_create_channel):
    ''' tset that if the channel_id is not exist, it will raise an Input Error'''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    send = {
        'token': user_1_token,
        'channel_id': INVALID_ID,
        'message': 'Hello World!',
    }
    response = requests.post(f'{url}/message/send', json=send)
    assert response.status_code == 400


def test_message_send_success_http(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']
    user_1_id = user_1_detail['u_id']
    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']
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

    send_1 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'message': "Hello, my name is Celine",
    }
    response = requests.post(f'{url}/message/send', json=send_1)
    assert response.status_code == 200

    message = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'start': 0,
    }
    response = requests.get(f'{url}/channel/messages', params=message)
    assert response.status_code == 200
    message_check = response.json()
    assert datetime.utcnow().replace(tzinfo=timezone.utc).timestamp() - \
        message_check['messages'][0]['time_created'] <= 1
    assert message_check['messages'][0]['message_id'] == 0
    assert message_check['messages'][0]['u_id'] == user_1_id
    assert message_check['messages'][0]['message'] == "Hello, my name is Celine"
    assert message_check['start'] == 0
    assert message_check['end'] == -1

    send_2 = {
        'token': user_2_token,
        'channel_id': channel_1_id,
        'message': "Hello, my name is Theresa",
    }
    response = requests.post(f'{url}/message/send', json=send_2)
    assert response.status_code == 200

    message_2 = {
        'token': user_2_token,
        'channel_id': channel_1_id,
        'start': 0,
    }
    response_2 = requests.get(f'{url}/channel/messages', params=message_2)
    assert response_2.status_code == 200
    message_check = response_2.json()
    assert datetime.utcnow().replace(tzinfo=timezone.utc).timestamp() - \
        message_check['messages'][1]['time_created'] <= 1
    assert message_check['messages'][1]['message_id'] == 1
    assert message_check['messages'][1]['u_id'] == user_2_id
    assert message_check['messages'][1]['message'] == "Hello, my name is Theresa"
    assert message_check['start'] == 0
    assert message_check['end'] == -1


###################################### message remove ################################################
def test_invalid_message_id_http(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    remove_1 = {
        'token': user_1_token,
        'message_id': INVALID_ID,
    }
    response = requests.delete(f'{url}/message/remove', json=remove_1)
    assert response.status_code == 400

    send_1 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'message': "Hello I am Celine",
    }
    response = requests.post(f'{url}/message/send', json=send_1)
    assert response.status_code == 200
    message_id = response.json()['message_id']
    assert message_id == 0

    remove_2 = {
        'token': user_1_token,
        'message_id': message_id,
    }
    response = requests.delete(f'{url}/message/remove', json=remove_2)
    assert response.status_code == 200


def test_not_owner_not_authorised_http(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    user_2_detail = register_create_channel[1]
    user_2_id = user_2_detail['u_id']
    user_2_token = user_2_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    send_1 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'message': 'Hello I am Celine',
    }
    response = requests.post(f'{url}/message/send', json=send_1)
    assert response.status_code == 200
    message_id = response.json()['message_id']

    invite_1 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'u_id': user_2_id,
    }
    response = requests.post(f'{url}/channel/invite', json=invite_1)
    assert response.status_code == 200

    remove_1 = {
        'token': user_2_token,
        'message_id': message_id,
    }
    response = requests.delete(f'{url}/message/remove', json=remove_1)
    assert response.status_code == 400


def test_invalid_message_id_not_authorised_http(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    user_2_detail = register_create_channel[1]
    user_2_id = user_2_detail['u_id']
    user_2_token = user_2_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    invite_1 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'u_id': user_2_id,
    }
    response = requests.post(f'{url}/channel/invite', json=invite_1)
    assert response.status_code == 200
    remove_1 = {
        'token': user_2_token,
        'message_id': INVALID_ID,
    }
    response = requests.delete(f'{url}/message/remove', json=remove_1)
    assert response.status_code == 400


def test_owner_case_http(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    user_2_detail = register_create_channel[1]
    user_2_id = user_2_detail['u_id']
    user_2_token = user_2_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    invite_1 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'u_id': user_2_id,
    }
    response = requests.post(f'{url}/channel/invite', json=invite_1)
    assert response.status_code == 200

    send_1 = {
        'token': user_2_token,
        'channel_id': channel_1_id,
        'message': "Hello I am Theresa"
    }
    response = requests.post(f'{url}/message/send', json=send_1)
    assert response.status_code == 200
    message_id = response.json()['message_id']

    remove_1 = {
        'token': user_1_token,
        'message_id': message_id,
    }
    response = requests.delete(f'{url}/message/remove', json=remove_1)
    assert response.status_code == 200
    assert response.json() == {}


def test_authorised_case_http(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    user_2_detail = register_create_channel[1]
    user_2_id = user_2_detail['u_id']
    user_2_token = user_2_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    invite_1 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'u_id': user_2_id,
    }
    response = requests.post(f'{url}/channel/invite', json=invite_1)
    assert response.status_code == 200

    send_1 = {
        'token': user_2_token,
        'channel_id': channel_1_id,
        'message': "Hello I am Theresa"
    }
    response = requests.post(f'{url}/message/send', json=send_1)
    assert response.status_code == 200
    message_id = response.json()['message_id']

    remove_1 = {
        'token': user_2_token,
        'message_id': message_id,
    }
    response = requests.delete(f'{url}/message/remove', json=remove_1)
    assert response.status_code == 200
    assert response.json() == {}

############################## message_edit #####################################


def test_auth_owner_edit_http(url, register_create_channel):
    '''
    An authorised user who is also an owner of the channel, no error is thrown
    '''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']
    user_1_id = user_1_detail['u_id']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    msg_send = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'message':  "A message to be edited"
    }

    # The owner send a message to the channel
    new_msg_json = requests.post(f'{url}/message/send', json=msg_send)
    new_msg = new_msg_json.json()
    msg_id = new_msg['message_id']

    # The owner edit the msg
    edit_msg = {
        'token': user_1_token,
        'message_id': msg_id,
        'message':  "Edited successfully"
    }
    response_1 = requests.put(f'{url}/message/edit', json=edit_msg)
    assert response_1.status_code == 200

    message = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'start': 0,
    }
    response = requests.get(f'{url}/channel/messages', params=message)
    assert response.status_code == 200
    message_check = response.json()
    assert datetime.utcnow().replace(tzinfo=timezone.utc).timestamp() - \
        message_check['messages'][msg_id - 1]['time_created'] <= 1
    assert message_check['messages'][msg_id - 1]['message_id'] == msg_id
    assert message_check['messages'][msg_id - 1]['u_id'] == user_1_id
    assert message_check['messages'][msg_id -
                                     1]['message'] == "Edited successfully"

    # The owner delete the msg
    delete_msg = {
        'token': user_1_token,
        'message_id': msg_id,
        'message':  ""
    }

    response_2 = requests.put(f'{url}/message/edit', json=delete_msg)
    assert response_2.status_code == 200

    response = requests.get(f'{url}/channel/messages', params=message)
    assert response.status_code == 200
    message_check = response.json()
    found = False
    for each_msg in message_check['messages']:
        if each_msg['message'] == "Edited successfully":
            found = True
    assert not found


def test_auth_msg_sent_edit_http(url, register_create_channel):
    '''
    An authorised user who sent the msg but not the owner of the channel, no error
    '''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']
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

    msg_send = {
        'token': user_2_token,
        'channel_id': channel_1_id,
        'message':  "A message to be edited"
    }

    # The member send a message to the channel
    new_msg_json = requests.post(f'{url}/message/send', json=msg_send)
    new_msg = new_msg_json.json()
    msg_id = new_msg['message_id']

    # The user edit the msg
    edit_msg = {
        'token': user_2_token,
        'message_id': msg_id,
        'message':  "Edited successfully"
    }

    response_1 = requests.put(f'{url}/message/edit', json=edit_msg)
    assert response_1.status_code == 200

    message = {
        'token': user_2_token,
        'channel_id': channel_1_id,
        'start': 0,
    }
    response = requests.get(f'{url}/channel/messages', params=message)
    assert response.status_code == 200
    message_check = response.json()
    assert datetime.utcnow().replace(tzinfo=timezone.utc).timestamp() - \
        message_check['messages'][msg_id - 1]['time_created'] <= 1
    assert message_check['messages'][msg_id - 1]['message_id'] == msg_id
    assert message_check['messages'][msg_id - 1]['u_id'] == u_2_id
    assert message_check['messages'][msg_id -
                                     1]['message'] == "Edited successfully"
    # The user delete the msg
    delete_msg = {
        'token': user_2_token,
        'message_id': msg_id,
        'message':  ""
    }

    response_2 = requests.put(f'{url}/message/edit', json=delete_msg)
    assert response_2.status_code == 200

    response = requests.get(f'{url}/channel/messages', params=message)
    assert response.status_code == 200
    message_check = response.json()
    found = False
    for each_msg in message_check['messages']:
        if each_msg['message'] == "Edited successfully":
            found = True
    assert not found


def test_auth_owner_not_sent_edit_http(url, register_create_channel):
    '''
    An authorised user who is an owner but didn't sent the msg, no error
    '''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']
    u_1_id = user_1_detail['u_id']

    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']
    u_2_id = user_2_detail['u_id']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    invite_1 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'u_id': u_2_id,
    }

    requests.post(f'{url}/channel/invite', json=invite_1)

    # The member send a message to the channel
    msg_send = {
        'token': user_2_token,
        'channel_id': channel_1_id,
        'message':  "A message to be edited"
    }

    # The member send a message to the channel
    new_msg_json = requests.post(f'{url}/message/send', json=msg_send)
    new_msg = new_msg_json.json()
    msg_id = new_msg['message_id']

    # The owner edit the msg
    edit_msg = {
        'token': user_1_token,
        'message_id': msg_id,
        'message':  "Edited successfully"
    }

    response_1 = requests.put(f'{url}/message/edit', json=edit_msg)
    assert response_1.status_code == 200

    message = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'start': 0,
    }
    response = requests.get(f'{url}/channel/messages', params=message)
    assert response.status_code == 200
    message_check = response.json()
    assert datetime.utcnow().replace(tzinfo=timezone.utc).timestamp() - \
        message_check['messages'][msg_id - 1]['time_created'] <= 1
    assert message_check['messages'][msg_id - 1]['message_id'] == msg_id
    assert message_check['messages'][msg_id - 1]['u_id'] == u_1_id
    assert message_check['messages'][msg_id -
                                     1]['message'] == "Edited successfully"

    # The owner delete the msg
    delete_msg = {
        'token': user_1_token,
        'message_id': msg_id,
        'message':  ""
    }

    response_2 = requests.put(f'{url}/message/edit', json=delete_msg)
    assert response_2.status_code == 200

    response = requests.get(f'{url}/channel/messages', params=message)
    assert response.status_code == 200
    message_check = response.json()
    found = False
    for each_msg in message_check['messages']:
        if each_msg['message'] == "Edited successfully":
            found = True
    assert not found


def test_auth_not_owner_not_sent_edit(url, register_create_channel):
    '''
    An authorised user who did't send the msg and is not the owner, AccessError raised
    '''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']
    u_2_id = user_2_detail['u_id']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    invite_1 = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'u_id': u_2_id,
    }

    requests.post(f'{url}/channel/invite', json=invite_1)

    # The member send a message to the channel
    msg_send = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'message':  "A message to be edited"
    }

    # The member send a message to the channel
    new_msg_json = requests.post(f'{url}/message/send', json=msg_send)
    new_msg = new_msg_json.json()
    msg_id = new_msg['message_id']

    edit_msg = {
        'token': user_2_token,
        'message_id': msg_id,
        'message':  "Edited successfully"
    }

    response_1 = requests.put(f'{url}/message/edit', json=edit_msg)
    assert response_1.status_code == 400

    delete_msg = {
        'token': user_2_token,
        'message_id': msg_id,
        'message':  ""
    }

    response_2 = requests.put(f'{url}/message/edit', json=delete_msg)
    assert response_2.status_code == 400


def test_global_owner_http(url, register_create_channel):
    '''
    A global owner who doesn't join the channel cannot edit or delete the msgs
    '''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']

    channel_2 = register_create_channel[5]
    channel_2_id = channel_2['channel_id']

    # The owner of channel send a message to the channel
    msg_send = {
        'token': user_2_token,
        'channel_id': channel_2_id,
        'message':  "A message to be edited"
    }

    # The member send a message to the channel
    new_msg_json = requests.post(f'{url}/message/send', json=msg_send)
    new_msg = new_msg_json.json()
    msg_id = new_msg['message_id']

    edit_msg = {
        'token': user_1_token,
        'message_id': msg_id,
        'message':  "Edited successfully"
    }

    response_1 = requests.put(f'{url}/message/edit', json=edit_msg)
    assert response_1.status_code == 400

    delete_msg = {
        'token': user_1_token,
        'message_id': msg_id,
        'message':  ""
    }

    response_2 = requests.put(f'{url}/message/edit', json=delete_msg)
    assert response_2.status_code == 400


def test_global_mem_http(url, register_create_channel):
    '''
    A global member who doesn't joined the channel cannot edit any msgs
    '''
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    msg_send = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'message':  "A message to be edited"
    }

    # The member send a message to the channel
    new_msg_json = requests.post(f'{url}/message/send', json=msg_send)
    new_msg = new_msg_json.json()
    msg_id = new_msg['message_id']

    edit_msg = {
        'token': user_2_token,
        'message_id': msg_id,
        'message':  "Edited unsuccessfully"
    }

    response_1 = requests.put(f'{url}/message/edit', json=edit_msg)
    assert response_1.status_code == 400

    delete_msg = {
        'token': user_2_token,
        'message_id': msg_id,
        'message':  ""
    }

    response_2 = requests.put(f'{url}/message/edit', json=delete_msg)
    assert response_2.status_code == 400


############################# message/sendlater #############################
@pytest.fixture
def message_sendlater_fixture(url):
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

    return user1_token, channel_id


def test_message_sendlater_invalid_channel_id_http(url, message_sendlater_fixture):
    token_1 = message_sendlater_fixture[0]
    message = "Hello World!"
    message_1 = {
        'token': token_1,
        'channel_id': INVALID_ID,
        'message': message,
        'time_sent': (datetime.utcnow(
        )+timedelta(seconds=180)).replace(tzinfo=timezone.utc).timestamp(),
    }
    response = requests.post(f'{url}/message/sendlater', json=message_1)
    assert response.status_code == 400


def test_message_sendlater_overlength_http(url, message_sendlater_fixture):
    token, channel_id = message_sendlater_fixture
    invalid_message = "I am over length" * 100

    message_1 = {
        'token': token,
        'channel_id': channel_id,
        'message': invalid_message,
        'time_sent': (datetime.utcnow(
        )+timedelta(seconds=180)).replace(tzinfo=timezone.utc).timestamp(),
    }
    response = requests.post(f'{url}/message/sendlater', json=message_1)
    assert response.status_code == 400


def test_message_sendlater_time_error_http(url, message_sendlater_fixture):
    token, channel_id = message_sendlater_fixture
    message = "Hello World!"
    message_1 = {
        'token': token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': (datetime.utcnow(
        )-timedelta(seconds=180)).replace(tzinfo=timezone.utc).timestamp(),
    }
    response = requests.post(f'{url}/message/sendlater', json=message_1)
    assert response.status_code == 400


def test_message_sendlater_not_authorised_http(url, message_sendlater_fixture):
    channel_id = message_sendlater_fixture[1]
    message = "Hello World!"

    second_user = {
        'email': 'theresa@gmail.com',
        'password': '123456',
        'name_first': 'Theresa',
        'name_last': 'Tao',
    }
    user_2_detail_json = requests.post(
        f'{url}/auth/register', json=second_user)
    user_2_detail = user_2_detail_json.json()
    user_2_token = user_2_detail['token']

    assert user_2_detail_json.status_code == 200

    message_1 = {
        'token': user_2_token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': (datetime.utcnow(
        )+timedelta(seconds=180)).replace(tzinfo=timezone.utc).timestamp(),
    }
    response = requests.post(f'{url}/message/sendlater', json=message_1)
    assert response.status_code == 400


def test_message_sendlater_invalid_token_http(url, message_sendlater_fixture):
    channel_id = message_sendlater_fixture[1]
    message = "hello world"
    Invalid_token = ""
    message_1 = {
        'token': Invalid_token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': (datetime.utcnow(
        )+timedelta(seconds=180)).replace(tzinfo=timezone.utc).timestamp(),
    }
    response = requests.post(f'{url}/message/sendlater', json=message_1)
    assert response.status_code == 400


def test_message_sendlater_success_case_http(url, message_sendlater_fixture):
    user_1_token, channel_id = message_sendlater_fixture
    message = "hello"

    message_1 = {
        'token': user_1_token,
        'channel_id': channel_id,
        'message': 'hello',
    }
    message_1_info_json = requests.post(f'{url}/message/send', json=message_1)

    assert message_1_info_json.status_code == 200

    message_1_info = message_1_info_json.json()
    message_size = message_1_info['message_id']

    message_2 = {
        'token': user_1_token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': (datetime.utcnow(
        )+timedelta(seconds=180)).replace(tzinfo=timezone.utc).timestamp(),
    }
    response = requests.post(f'{url}/message/sendlater', json=message_2)
    assert response.status_code == 200
    message_id_dict = response.json()
    message_id = message_id_dict['message_id']
    assert message_id == message_size + 1


############################ message/react #####################################
@pytest.fixture
def message_react_fixture(url):
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
    message_1 = {
        'token': user1_token,
        'channel_id': channel_id,
        'message': 'hello',
    }
    message_1_info_json = requests.post(f'{url}/message/send', json=message_1)
    message_1_info = message_1_info_json.json()
    message_id = message_1_info['message_id']

    return user1_token, message_id


def test_message_react_invalid_message_id_http(url, message_react_fixture):
    user_1_token, message_id = message_react_fixture
    react_1 = {
        'token': user_1_token,
        'message_id': INVALID_ID,
        'react_id': 1,
    }
    response = requests.post(f'{url}/message/react', json=react_1)
    assert response.status_code == 400

    user_2_token = "Invalid"

    react_2 = {
        'token': user_2_token,
        'message_id': message_id,
        'react_id': 1,
    }
    response = requests.post(f'{url}/message/react', json=react_2)
    assert response.status_code == 400


def test_message_react_invalid_react_id_http(url, message_react_fixture):
    user_1_token, message_id = message_react_fixture
    react_1 = {
        'token': user_1_token,
        'message_id': message_id,
        'react_id': INVALID_ID,
    }
    response = requests.post(f'{url}/message/react', json=react_1)
    assert response.status_code == 400


def test_message_react_already_reacted(url, message_react_fixture):
    user_1_token, message_id = message_react_fixture

    react_1 = {
        'token': user_1_token,
        'message_id': message_id,
        'react_id': 1,
    }
    response = requests.post(f'{url}/message/react', json=react_1)
    assert response.status_code == 200

    response = requests.post(f'{url}/message/react', json=react_1)
    assert response.status_code == 400


def test_message_react_success_case_http(url, message_react_fixture):
    user_1_token, message_id = message_react_fixture

    react_1 = {
        'token': user_1_token,
        'message_id': message_id,
        'react_id': 1,
    }
    response = requests.post(f'{url}/message/react', json=react_1)
    assert response.status_code == 200

#################################### message/unreact #########################################


def test_message_unreact_invalid_message_id_http(url, message_react_fixture):
    user_1_token, message_id = message_react_fixture
    unreact_1 = {
        'token': user_1_token,
        'message_id': INVALID_ID,
        'react_id': 1,
    }
    response = requests.post(f'{url}/message/unreact', json=unreact_1)
    assert response.status_code == 400

    user_2_token = "Invalid"

    unreact_2 = {
        'token': user_2_token,
        'message_id': message_id,
        'react_id': 1,
    }
    response = requests.post(f'{url}/message/unreact', json=unreact_2)
    assert response.status_code == 400


def test_message_unreact_invalid_react_id_http(url, message_react_fixture):
    user_1_token, message_id = message_react_fixture
    unreact_1 = {
        'token': user_1_token,
        'message_id': message_id,
        'react_id': INVALID_ID,
    }
    response = requests.post(f'{url}/message/unreact', json=unreact_1)
    assert response.status_code == 400


def test_message_unreact_not_reacted_http(url, message_react_fixture):
    user_1_token, message_id = message_react_fixture
    unreact_1 = {
        'token': user_1_token,
        'message_id': message_id,
        'react_id': 1,
    }
    response = requests.post(f'{url}/message/unreact', json=unreact_1)
    assert response.status_code == 400


def test_message_unreact_success_case_http(url, message_react_fixture):
    user_1_token, message_id = message_react_fixture
    react_1 = {
        'token': user_1_token,
        'message_id': message_id,
        'react_id': 1,
    }
    response = requests.post(f'{url}/message/react', json=react_1)
    assert response.status_code == 200

    unreact_1 = {
        'token': user_1_token,
        'message_id': message_id,
        'react_id': 1,
    }
    response = requests.post(f'{url}/message/unreact', json=unreact_1)
    assert response.status_code == 200


# =====================message_pin/unpin=========================
@pytest.fixture
def user_send_message(url, register_create_channel):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    channel_1 = register_create_channel[3]
    channel_1_id = channel_1['channel_id']

    string = "To test message_pin and message_unpin"

    send = {
        'token': user_1_token,
        'channel_id': channel_1_id,
        'message': string
    }

    message_info_json = requests.post(f'{url}/message/send', json=send)
    message_info = message_info_json.json()

    return message_info

# =====================message_pin=========================


def test_message_pin_success_and_already_pinned(url, register_create_channel, user_send_message):
    user_detail = register_create_channel[0]
    user_token = user_detail['token']

    message_detail = user_send_message
    message_id = message_detail['message_id']

    message_pin = {
        'token': user_token,
        'message_id': message_id,
    }

    response = requests.post(f'{url}/message/pin', json=message_pin)
    assert response.status_code == 200

    # message already pinned
    response = requests.post(f'{url}/message/pin', json=message_pin)
    assert response.status_code == 400


def test_message_pin_invalid_token(url, user_send_message):
    message_detail = user_send_message
    message_id = message_detail['message_id']

    message_pin = {
        'token': -1,
        'message_id': message_id,
    }

    response = requests.post(f'{url}/message/pin', json=message_pin)
    assert response.status_code == 400


def test_message_pin_invaild_message_id(url, register_create_channel):
    user_detail = register_create_channel[0]
    user_token = user_detail['token']

    message_pin = {
        'token': user_token,
        'message_id': -1,
    }

    response = requests.post(f'{url}/message/pin', json=message_pin)
    assert response.status_code == 400


def test_message_pin_user_not_member(url, register_create_channel, user_send_message):
    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']

    message_detail = user_send_message
    message_id = message_detail['message_id']

    message_pin = {
        'token': user_2_token,
        'message_id': message_id,
    }

    # user 2 is not a member of the channel
    response = requests.post(f'{url}/message/pin', json=message_pin)
    assert response.status_code == 400


def test_message_pin_user_not_owner(url, register_create_channel, user_send_message):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    user_2_detail = register_create_channel[1]
    user_2_id = user_2_detail['u_id']

    channel_detail = register_create_channel[3]
    channel_id = channel_detail['channel_id']

    invite = {
        'token': user_1_token,
        'channel_id': channel_id,
        'u_id': user_2_id,
    }
    response = requests.post(f'{url}/channel/invite', json=invite)
    assert response.status_code == 200

    message_detail = user_send_message
    message_id = message_detail['message_id']

    user_2_token = user_2_detail['token']

    message_pin = {
        'token': user_2_token,
        'message_id': message_id,
    }

    # user 2 is not an owner of the channel
    response = requests.post(f'{url}/message/pin', json=message_pin)
    assert response.status_code == 400

# ===========================message_unpin==========================


@pytest.fixture
def user_pin_message(url, register_create_channel, user_send_message):
    user_detail = register_create_channel[0]
    user_token = user_detail['token']

    message_detail = user_send_message
    message_id = message_detail['message_id']

    message_pin = {
        'token': user_token,
        'message_id': message_id,
    }
    requests.post(f'{url}/message/pin', json=message_pin)
    return {}


def test_message_unpin_success_and_no_pinned(url, register_create_channel, user_send_message, user_pin_message):
    user_detail = register_create_channel[0]
    user_token = user_detail['token']

    message_detail = user_send_message
    message_id = message_detail['message_id']

    message_unpin = {
        'token': user_token,
        'message_id': message_id,
    }

    response = requests.post(f'{url}/message/unpin', json=message_unpin)
    assert response.status_code == 200

    #message is not pinned
    response = requests.post(f'{url}/message/unpin', json=message_unpin)
    assert response.status_code == 400


def test_message_unpin_invalid_token(url, user_send_message, user_pin_message):
    message_detail = user_send_message
    message_id = message_detail['message_id']

    message_unpin = {
        'token': -1,
        'message_id': message_id,
    }

    response = requests.post(f'{url}/message/unpin', json=message_unpin)
    assert response.status_code == 400


def test_message_unpin_invaild_message_id(url, register_create_channel, user_pin_message):
    user_detail = register_create_channel[0]
    user_token = user_detail['token']

    message_unpin = {
        'token': user_token,
        'message_id': -1,
    }

    response = requests.post(f'{url}/message/unpin', json=message_unpin)
    assert response.status_code == 400


def test_message_unpin_user_not_member(url, register_create_channel, user_send_message, user_pin_message):
    user_2_detail = register_create_channel[1]
    user_2_token = user_2_detail['token']

    message_detail = user_send_message
    message_id = message_detail['message_id']

    message_unpin = {
        'token': user_2_token,
        'message_id': message_id,
    }

    # user 2 is not a member of the channel
    response = requests.post(f'{url}/message/unpin', json=message_unpin)
    assert response.status_code == 400


def test_message_unpin_user_not_owner(url, register_create_channel, user_send_message, user_pin_message):
    user_1_detail = register_create_channel[0]
    user_1_token = user_1_detail['token']

    user_2_detail = register_create_channel[1]
    user_2_id = user_2_detail['u_id']

    channel_detail = register_create_channel[3]
    channel_id = channel_detail['channel_id']

    invite = {
        'token': user_1_token,
        'channel_id': channel_id,
        'u_id': user_2_id,
    }
    response = requests.post(f'{url}/channel/invite', json=invite)
    assert response.status_code == 200

    message_detail = user_send_message
    message_id = message_detail['message_id']

    user_2_token = user_2_detail['token']

    message_unpin = {
        'token': user_2_token,
        'message_id': message_id,
    }

    # user 2 is not an owner of the channel
    response = requests.post(f'{url}/message/unpin', json=message_unpin)
    assert response.status_code == 400
