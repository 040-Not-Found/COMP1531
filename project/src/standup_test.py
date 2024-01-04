import pytest
from datetime import datetime, timedelta, timezone
from Global_variables import *
from auth import *
from channels import *
from channel import *
from error import *
from other import *
from standup import *
from message import *

invalid_id = -1


@pytest.fixture
def register_two_users_create_two_channels():
    clear()
    user_1_detail = auth_register(
        'celine@gmail.com', '123456', 'Celine', 'Lin')
    token_1 = user_1_detail['token']

    channel_1_info = channels_create(token_1, 'OwnedByCeline', True)
    channel_1_id = channel_1_info['channel_id']

    return token_1, channel_1_id

################################ standup_start ####################################


def test_standup_invalid_channel_id(register_two_users_create_two_channels):
    token = register_two_users_create_two_channels[0]
    with pytest.raises(InputError):
        standup_start(token, invalid_id, 60)


def test_standup_invalid_token(register_two_users_create_two_channels):
    channel_id = register_two_users_create_two_channels[1]
    with pytest.raises(AccessError):
        standup_start("", channel_id, 60)


def test_standup_start_not_member(register_two_users_create_two_channels):
    channel_id = register_two_users_create_two_channels[1]

    not_mem_detail = auth_register(
        'peter@gmail.com', '123456', 'Peter', 'Xie')
    not_mem_token = not_mem_detail['token']

    with pytest.raises(AccessError):
        standup_start(not_mem_token, channel_id, 60)


def test_standup_active_already_owner(register_two_users_create_two_channels):
    '''
    An owner of the channel cannot start a standup when one is already active
    '''
    token = register_two_users_create_two_channels[0]
    channel_id = register_two_users_create_two_channels[1]
    standup_start(token, channel_id, 60)
    with pytest.raises(InputError):
        standup_start(token, channel_id, 60)


def test_standup_active_already_member(register_two_users_create_two_channels):
    '''
    A member of the channel cannot start a standup when one is already active
    '''
    token = register_two_users_create_two_channels[0]
    channel_id = register_two_users_create_two_channels[1]

    mem_detail = auth_register(
        'peter@gmail.com', '123456', 'Peter', 'Xie')
    mem_id = mem_detail['u_id']
    mem_token = mem_detail['token']

    channel_invite(token, channel_id, mem_id)
    standup_start(mem_token, channel_id, 60)
    with pytest.raises(InputError):
        standup_start(mem_token, channel_id, 60)


def test_standup_owner_successfully(register_two_users_create_two_channels):
    '''
    An owner of the channel can start a standup if no error occurred
    '''
    token = register_two_users_create_two_channels[0]
    channel_id = register_two_users_create_two_channels[1]

    assert not standup_active(token, channel_id)['is_active']

    length = 60
    discrepancy = 1
    assert standup_start(token, channel_id, length)['time_finish'] > (datetime.utcnow(
    ) + timedelta(seconds=length - discrepancy)).replace(tzinfo=timezone.utc).timestamp()

    assert standup_active(token, channel_id)['is_active']


def test_standup_member_successfully(register_two_users_create_two_channels):
    token = register_two_users_create_two_channels[0]
    channel_id = register_two_users_create_two_channels[1]

    mem_detail = auth_register(
        'peter@gmail.com', '123456', 'Peter', 'Xie')
    mem_id = mem_detail['u_id']
    mem_token = mem_detail['token']

    channel_invite(token, channel_id, mem_id)

    assert not standup_active(mem_token, channel_id)['is_active']

    length = 60
    discrepancy = 1
    assert standup_start(mem_token, channel_id, length)['time_finish'] > (datetime.utcnow(
    ) + timedelta(seconds=length - discrepancy)).replace(tzinfo=timezone.utc).timestamp()

    assert standup_active(mem_token, channel_id)['is_active']


############################## standup_active #####################################
def test_standup_active_invalid_channel_id(register_two_users_create_two_channels):
    '''
    Invalid channel_id will raise InputError
    '''
    token = register_two_users_create_two_channels[0]
    with pytest.raises(InputError):
        standup_active(token, invalid_id)


def test_standup_active_invalid_token(register_two_users_create_two_channels):
    '''
    Invalid token will raise AccessError
    '''
    channel_id = register_two_users_create_two_channels[1]
    with pytest.raises(AccessError):
        standup_active("", channel_id)


def test_standup_active_owner(register_two_users_create_two_channels):
    '''
    An owner of the channel can see if a standup is happening in this channel
    '''
    token = register_two_users_create_two_channels[0]
    channel_id = register_two_users_create_two_channels[1]

    assert not standup_active(token, channel_id)['is_active']

    standup_start(token, channel_id, 60)

    assert standup_active(token, channel_id)['is_active']


def test_standup_active_member(register_two_users_create_two_channels):
    '''
    A member of the channel can see if a standup is happening in this channel
    '''
    token = register_two_users_create_two_channels[0]
    channel_id = register_two_users_create_two_channels[1]

    mem_detail = auth_register(
        'peter@gmail.com', '123456', 'Peter', 'Xie')
    mem_id = mem_detail['u_id']
    mem_token = mem_detail['token']

    channel_invite(token, channel_id, mem_id)

    assert not standup_active(mem_token, channel_id)['is_active']

    standup_start(token, channel_id, 60)

    assert standup_active(mem_token, channel_id)['is_active']


def test_standup_active_not_member(register_two_users_create_two_channels):
    '''
    A user who is not a member of the channel cannot use this feature
    '''
    channel_id = register_two_users_create_two_channels[1]

    not_mem_detail = auth_register(
        'peter@gmail.com', '123456', 'Peter', 'Xie')
    not_mem_token = not_mem_detail['token']

    with pytest.raises(AccessError):
        standup_active(not_mem_token, channel_id)['is_active']

# ===================STANDUP SEND TESTS====================== #

def test_standup_send_invalid_token(register_two_users_create_two_channels):
    '''
    Test standup send invalid token
    '''
    user_2_detail = auth_register(
        'peter@gmail.com', '123456', 'Peter', 'Xie')
    user_2_token = user_2_detail['token']
    channel_id_1 = register_two_users_create_two_channels[1]
    with pytest.raises(AccessError):
        standup_send(user_2_token, channel_id_1, 'Test message')
    with pytest.raises(AccessError):
        standup_send(None, channel_id_1, 'Test message')


def test_standup_send_invalid_channel_id(register_two_users_create_two_channels):
    '''
    Test standup send invalid channel
    '''
    user_1_token = register_two_users_create_two_channels[0]
    with pytest.raises(InputError):
        standup_send(user_1_token, None, 'Test')
    with pytest.raises(InputError):
        standup_send(user_1_token, 99, 'Test')


def test_standup_send_more_than_1000_chars_or_none(register_two_users_create_two_channels):
    '''
    Test invalid message
    '''
    user_1_token = register_two_users_create_two_channels[0]
    channel_1_id = register_two_users_create_two_channels[1]
    with pytest.raises(InputError):
        standup_send(user_1_token, channel_1_id,
                     'This is over 1000 chars' * 1000)
    with pytest.raises(InputError):
        standup_send(user_1_token, channel_1_id, '')


def test_standup_send_not_currently_active(register_two_users_create_two_channels):
    '''
    Test standup not active
    '''
    user_1_token = register_two_users_create_two_channels[0]
    channel_1_id = register_two_users_create_two_channels[1]
    with pytest.raises(InputError):
        standup_send(user_1_token, channel_1_id, 'Test message')


def test_standup_send_currently_active(register_two_users_create_two_channels):
    '''
    Test standup active valid for standup send
    '''
    user_1_token = register_two_users_create_two_channels[0]
    channel_1_id = register_two_users_create_two_channels[1]
    standup_start(user_1_token, channel_1_id, 60)

    assert standup_send(user_1_token, channel_1_id, 'Test message') == {}
