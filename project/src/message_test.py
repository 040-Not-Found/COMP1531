''' we need to use pytest!'''
######################################################################

import pytest
from Global_variables import *
import Global_variables as globals
from other import clear
from error import InputError, AccessError
from message import *
from channels import channels_create
from channel import channel_invite, channel_messages
from auth import auth_register, auth_login
from datetime import datetime, timezone, timedelta
# test for the case that the message is over 1000 chars

INVALID_ID = -1


def test_over_length():
    clear()
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']
    # Celine create a new channel
    channel_info = channels_create(token_1, 'OwnedByCeline', True)
    channel_id = channel_info['channel_id']
    long_string = "I am over length" * 100
    # case that an owner send an over_length message
    with pytest.raises(InputError):
        message_send(token_1, channel_id, long_string)
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']
    u_2_id = user_2_detail['u_id']
    channel_invite(token_1, channel_id, u_2_id)
    # case that the mem in channnel but not owner send an over_length message
    with pytest.raises(InputError):
        message_send(token_2, channel_id, long_string)

# test that the person is not authorised in the channel


def test_not_in_channel():
    clear()
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']
    # Celine create a channel
    channel_info = channels_create(token_1, 'OwnedByCeline', True)
    channel_id = channel_info['channel_id']
    # Theresa registered but not in this channel
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']
    with pytest.raises(AccessError):
        message_send(token_2, channel_id, "Hello World!")


def test_not_in_channel_over_length():
    clear()
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']
    # Celine create a channel
    channel_info = channels_create(token_1, 'OwnedByCeline', True)
    channel_id = channel_info['channel_id']
    # Theresa registered but not in this channel
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']
    # message is over length, and theresa is not in this channel
    with pytest.raises(AccessError):
        message_send(token_2, channel_id, "I am over length" * 100)
# tset that if the channel_id is not exist, it will raise an Input Error


def test_channel_is_not_exist():
    clear()
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']
    # Celine create a new channel
    invalid_channel_id = -1
    with pytest.raises(InputError):
        message_send(token_1, invalid_channel_id, "Hello World")
# test for the success message_send case


def test_message_send_success():
    clear()
    # Celine registered
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']
    user_1_id = user_1_detail['u_id']
    # Celine create a new channel
    channel_info = channels_create(token_1, 'OwnedByCeline', True)
    channel_id = channel_info['channel_id']
    # Theresa registered
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']
    u_2_id = user_2_detail['u_id']
    # add Theresa to channel
    channel_invite(token_1, channel_id, u_2_id)
    # send the first message

    message_send(
        token_1, channel_id, "Hello, my name is Celine")

    message_check = channel_messages(token_1, channel_id, 0)
    assert datetime.utcnow().replace(tzinfo=timezone.utc).timestamp() - \
        message_check['messages'][0]['time_created'] <= 1
    assert message_check['messages'][0]['message_id'] == 0
    assert message_check['messages'][0]['u_id'] == user_1_id
    assert message_check['messages'][0]['message'] == "Hello, my name is Celine"
    assert message_check['start'] == 0
    assert message_check['end'] == -1

    # not sure here
    message_send(
        token_2, channel_id, "Hello, my name is Theresa")
    message_check_2 = channel_messages(token_1, channel_id, 0)
    assert datetime.utcnow().replace(tzinfo=timezone.utc).timestamp() - \
        message_check_2['messages'][0]['time_created'] <= 1
    assert message_check_2['messages'][0]['message_id'] == 0
    assert message_check_2['messages'][0]['u_id'] == user_1_id
    assert message_check_2['messages'][1]['message'] == "Hello, my name is Theresa"
    assert message_check_2['start'] == 0
    assert message_check_2['end'] == -1


######################################################################
@pytest.fixture
def register_create_channel():
    clear()
    user_1_detail = auth_register(
        'celine@gmail.com', '123456', 'Celine', 'Lin')
    token_1 = user_1_detail['token']

    channel_info = channels_create(token_1, 'OwnedByCeline', True)
    channel_id = channel_info['channel_id']
    return token_1, channel_id




def test_msg_remove_invalid_user(register_create_channel):
    token_1, channel_id = register_create_channel

    message_info = message_send(token_1, channel_id, "Hello I am Celine")
    message_id = message_info['message_id']

    with pytest.raises(AccessError):
        message_remove(-1, message_id)


def test_invalid_message_id(register_create_channel):
    ''' case for message_id does not exist'''
    token_1, channel_id = register_create_channel
    invalid_message_id = -1

    with pytest.raises(InputError):
        message_remove(token_1, invalid_message_id)

    message_info = message_send(token_1, channel_id, "Hello I am Celine")
    # print(total_message)
    print(channels[channel_id]['messages'])
    message_id = message_info['message_id']

    # successfully remove the message, this message is no longer exist\
    assert message_remove(token_1, message_id) == {}

    # since the message is no longer exist, it will raise an InputError
    assert message_id == 0
    with pytest.raises(InputError):
        message_remove(token_1, message_id)


def test_not_owner_not_authorised(register_create_channel):
    ''' person is neither owner of channel nor the person who sent the message, he cannot reomve'''
    token_1, channel_id = register_create_channel

    message_info = message_send(token_1, channel_id, "Hello I am Celine")
    message_id = message_info['message_id']
    # Invite Theresa to the channel, but she does not have permission to remove the message

    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    u_2_id = user_2_detail['u_id']
    token_2 = user_2_detail['token']
    channel_invite(token_1, channel_id, u_2_id)

    with pytest.raises(AccessError):
        message_remove(token_2, message_id)


def test_invalid_message_id_not_authorised(register_create_channel):
    ''' test both message size is outbound and person sent the message by himself '''
    token_1, channel_id = register_create_channel
    invalid_message_id = -1

    # Invite Theresa to the channel, but she does not have permission to remove the message
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    u_2_id = user_2_detail['u_id']
    token_2 = user_2_detail['token']

    channel_invite(token_1, channel_id, u_2_id)
    with pytest.raises(InputError):
        message_remove(token_2, invalid_message_id)


def test_owner_case(register_create_channel):
    '''test for the owner in the channel want to delete message'''
    token_1, channel_id = register_create_channel

    # Invite Theresa to the channel
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    u_2_id = user_2_detail['u_id']
    token_2 = user_2_detail['token']

    message_send(token_1, channel_id, "Coverage")

    channel_invite(token_1, channel_id, u_2_id)
    message_info = message_send(token_2, channel_id, "Hello I am Theresa")
    message_id = message_info['message_id']
    assert message_remove(token_1, message_id) == {}


def test_authorised_case(register_create_channel):
    ''' test person who sent the message then want to delete it'''
    token_1, channel_id = register_create_channel

    # Invite Theresa to the channel
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    u_2_id = user_2_detail['u_id']
    token_2 = user_2_detail['token']

    channel_invite(token_1, channel_id, u_2_id)
    message_info = message_send(token_2, channel_id, "Hello I am Theresa")
    message_id = message_info['message_id']
    assert message_remove(token_2, message_id) == {}


#################################### message_edit #########################################
def test_msg_edit_invalid_token(register_create_channel):
    token_1, channel_id = register_create_channel

    # The owner send a message to the channel
    message_info = message_send(token_1, channel_id, "A message to be edited")
    message_id = message_info['message_id']

    with pytest.raises(Exception):
        message_edit(None, message_id, "Edited successfully")


def test_auth_owner_edit(register_create_channel):
    '''
    An authorised user who is also an owner of the channel, no error is thrown
    '''
    token_1, channel_id = register_create_channel

    # The owner send one message to the channel
    message_send(token_1, channel_id, "Coverage")

    # The owner send two messages to the channel
    message_info = message_send(token_1, channel_id, "A message to be edited")
    message_id = message_info['message_id']

    message_edit(token_1, message_id, "Edited successfully")
    assert channels[channel_id]['messages'][message_id]['message'] == "Edited successfully"

    message_edit(token_1, message_id, "")

    found = False
    for each_msg in channels[channel_id]['messages']:
        if each_msg['message'] == "A message to be edited":
            found = True

    assert not found


def test_auth_msg_sent_edit(register_create_channel):
    '''
    An authorised user who sent the msg but not the owner of the channel, no error
    '''
    token_1, channel_id = register_create_channel

    # Second user logged in
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']
    u_2_id = user_2_detail['u_id']

    channel_invite(token_1, channel_id, u_2_id)

    # The member send a message to the channel
    message_info = message_send(token_2, channel_id, "A message to be edited")
    message_id = message_info['message_id']

    message_edit(token_2, message_id, "Edited successfully")
    assert channels[channel_id]['messages'][message_id -
                                            1]['message'] == "Edited successfully"

    message_edit(token_2, message_id, "")
    found = False
    for each_msg in channels[channel_id]['messages']:
        if each_msg['message'] == "Edited successfully":
            found = True

    assert not found


def test_auth_owner_not_sent_edit(register_create_channel):
    '''
    An authorised user who is an owner but didn't sent the msg, no error
    '''
    token_1, channel_id = register_create_channel

    # Second user logged in
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']
    u_2_id = user_2_detail['u_id']

    channel_invite(token_1, channel_id, u_2_id)

    # The member send a message to the channel
    message_info = message_send(token_2, channel_id, "A message to be edited")
    message_id = message_info['message_id']

    # Edit the msg
    message_edit(token_1, message_id, "Edited successfully")
    assert channels[channel_id]['messages'][message_id -
                                            1]['message'] == "Edited successfully"

    # Delete the msg
    message_edit(token_1, message_id, "")
    found = False
    for each_msg in channels[channel_id]['messages']:
        if each_msg['message'] == "Edited successfully":
            found = True

    assert not found


def test_auth_not_owner_not_sent_edit(register_create_channel):
    '''
    An authorised user who did't send the msg and is not the owner, AccessError raised
    '''
    token_1, channel_id = register_create_channel

    # Second user logged in
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']
    u_2_id = user_2_detail['u_id']

    channel_invite(token_1, channel_id, u_2_id)

    # The member send a message to the channel
    message_info = message_send(token_1, channel_id, "A message to be edited")
    message_id = message_info['message_id']

    with pytest.raises(AccessError):
        message_edit(token_2, message_id, "Edited successfully")

    with pytest.raises(AccessError):
        message_edit(token_2, message_id, "")


def test_global_owner(register_create_channel):
    '''
    A global owner who doesn't join the channel cannot edit or delete the msgs
    '''
    token_1, channel_id = register_create_channel
    # Second user logged in
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']

    # The second user creat a new channel
    channel_info = channels_create(token_2, 'OwnedByTheresa', True)
    channel_id = channel_info['channel_id']

    # The owner of channel send a message to the channel
    message_info = message_send(token_2, channel_id, "A message to be edited")
    message_id = message_info['message_id']

    with pytest.raises(AccessError):
        message_edit(token_1, message_id, "Edited unsuccessfully")

    with pytest.raises(AccessError):
        message_edit(token_1, message_id, "")


def test_global_mem(register_create_channel):
    '''
    A global member who doesn't joined the channel cannot edit any msgs
    '''
    token_1, channel_id = register_create_channel

    # The first user creat a new channel
    channel_info = channels_create(token_1, 'OwnedByCeline', True)
    channel_id = channel_info['channel_id']

    # The owner of channel send a message to the channel
    message_info = message_send(token_1, channel_id, "A message to be edited")
    message_id = message_info['message_id']

    # Second user logged in
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']

    with pytest.raises(AccessError):
        message_edit(token_2, message_id, "Edited unsuccessfully")

    with pytest.raises(AccessError):
        message_edit(token_2, message_id, "")

#################################### message_sendlater ##############################


def test_message_sendlater_invalid_channel_id(register_create_channel):
    token_1 = register_create_channel[0]
    message = "Hello World!"
    with pytest.raises(InputError):
        message_sendlater(token_1, INVALID_ID, message, (datetime.utcnow(
        )+timedelta(seconds=180)).replace(tzinfo=timezone.utc).timestamp())


def test_message_sendlater_overlength(register_create_channel):
    token, channel_id = register_create_channel
    invalid_message = "I am over length" * 100
    with pytest.raises(InputError):
        message_sendlater(token, channel_id, invalid_message, (datetime.utcnow(
        )+timedelta(seconds=180)).replace(tzinfo=timezone.utc).timestamp())


def test_message_sendlater_time_error(register_create_channel):
    token, channel_id = register_create_channel
    message = "Hello World!"
    with pytest.raises(InputError):
        message_sendlater(token, channel_id, message, (datetime.utcnow(
        )-timedelta(seconds=180)).replace(tzinfo=timezone.utc).timestamp())


def test_message_sendlater_not_authorised(register_create_channel):
    channel_id = register_create_channel[1]
    message = "Hello World!"
    user_2_info = auth_register(
        "theresa@gmail.com", '123456', 'Theresa', 'Tao')
    user_2_token = user_2_info['token']
    with pytest.raises(AccessError):
        message_sendlater(user_2_token, channel_id, message, (datetime.utcnow(
        )+timedelta(seconds=180)).replace(tzinfo=timezone.utc).timestamp())


def test_message_sendlater_invalid_token(register_create_channel):
    channel_id = register_create_channel[1]
    message = "Hello World!"
    Invalid_token = ""
    with pytest.raises(InputError):
        message_sendlater(Invalid_token, channel_id, message, (datetime.utcnow(
        )+timedelta(seconds=180)).replace(tzinfo=timezone.utc).timestamp())


def test_message_sendlater_multi_errors(register_create_channel):
    channel_id = register_create_channel[1]
    message = "Hello World!"
    invalid_message = "I am overlength" * 100
    user_2_info = auth_register(
        "theresa@gmail.com", '123456', 'Theresa', 'Tao')
    user_2_token = user_2_info['token']
    with pytest.raises(InputError):
        message_sendlater(user_2_token, INVALID_ID, message, (datetime.utcnow(
        ) + timedelta(seconds=180)).replace(tzinfo=timezone.utc).timestamp())

    with pytest.raises(InputError):
        message_sendlater(user_2_token, channel_id, invalid_message, (datetime.utcnow(
        ) + timedelta(seconds=180)).replace(tzinfo=timezone.utc).timestamp())

    with pytest.raises(InputError):
        message_sendlater(user_2_token, channel_id, message, (datetime.utcnow(
        ) - timedelta(seconds=180)).replace(tzinfo=timezone.utc).timestamp())


def test_message_sendlater_success_case(register_create_channel):
    user_1_token, channel_id = register_create_channel
    message = "Hello"
    message_size = message_send(user_1_token, channel_id, message)[
        'message_id']
    message_id = message_sendlater(user_1_token, channel_id, message, (datetime.utcnow(
    )+timedelta(seconds=1)).replace(tzinfo=timezone.utc).timestamp())['message_id']
    assert message_id == message_size + 1

########################################### message_react #####################################################


@pytest.fixture
def message_react_part():
    clear()
    user_1_detail = auth_register(
        'celine@gmail.com', '123456', 'Celine', 'Lin')
    token_1 = user_1_detail['token']

    channel_info = channels_create(token_1, 'OwnedByCeline', True)
    channel_id = channel_info['channel_id']
    message_id1 = message_send(token_1, channel_id, "hello")['message_id']
    return token_1, message_id1


def test_message_react_invalid_message_id(message_react_part):
    user_1_token, message_id = message_react_part
    with pytest.raises(InputError):
        message_react(user_1_token, INVALID_ID, 1)

    user_2_token = "Invalid"

    with pytest.raises(InputError):
        message_react(user_2_token, message_id, 1)

    user_2_detail = auth_register(
        'theresa@gmail.com', '123456', 'Theresa', 'Tao')
    token_2 = user_2_detail['token']

    with pytest.raises(InputError):
        message_react(token_2, message_id, 1)


def test_message_react_invalid_react_id(message_react_part):
    user_1_token, message_id = message_react_part

    with pytest.raises(InputError):
        message_react(user_1_token, message_id, INVALID_ID)


def test_message_react_already_reacted(message_react_part):
    user_1_token, message_id = message_react_part

    message_react(user_1_token, message_id, 1)
    with pytest.raises(InputError):
        message_react(user_1_token, message_id, 1)


def test_message_react_success_case(message_react_part):
    user_1_token, message_id = message_react_part
    message_react(user_1_token, message_id, 1)

    assert channels[0]['messages'][0]['reacts'][0]['u_ids'] == [0]
    assert channels[0]['messages'][0]['reacts'][0]['is_this_user_reacted'] == True
##################################### message_unreact part ###########################################


def test_message_unreact_invalid_message_id(message_react_part):
    user_1_token, message_id = message_react_part
    with pytest.raises(InputError):
        message_unreact(user_1_token, INVALID_ID, 1)

    user_2_token = "Invalid"

    with pytest.raises(InputError):
        message_unreact(user_2_token, message_id, 1)

    user_2_detail = auth_register(
        'theresa@gmail.com', '123456', 'Theresa', 'Tao')
    token_2 = user_2_detail['token']

    with pytest.raises(InputError):
        message_unreact(token_2, message_id, 1)


def test_message_unreact_invalid_react_id(message_react_part):
    user_1_token, message_id = message_react_part
    with pytest.raises(InputError):
        message_unreact(user_1_token, message_id, INVALID_ID)


def test_message_unreact_not_reacted(message_react_part):
    user_1_token, message_id = message_react_part
    with pytest.raises(InputError):
        message_unreact(user_1_token, message_id, 1)


def test_message_unreact_success_case(message_react_part):
    user_1_token, message_id = message_react_part
    message_react(user_1_token, message_id, 1)
    assert channels[0]['messages'][0]['reacts'][0]['u_ids'] == [0]
    assert channels[0]['messages'][0]['reacts'][0]['is_this_user_reacted'] == True
    message_unreact(user_1_token, message_id, 1)
    assert channels[0]['messages'][0]['reacts'][0]['u_ids'] == []
    assert channels[0]['messages'][0]['reacts'][0]['is_this_user_reacted'] == False


# ========================message/pin==========================
@pytest.fixture
def register_send_message():
    clear()
    # Celine registered
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']
    # Celine create a new channel
    channel_info = channels_create(token_1, 'OwnedByCeline', True)
    channel_id = channel_info['channel_id']

    # send the first message
    message_id_0 = message_send(
        token_1, channel_id, "Hello, my name is Celine")['message_id']

    return token_1, message_id_0, channel_id


def test_message_pin_invalid_token(register_send_message):
    message_id = register_send_message[1]
    with pytest.raises(AccessError):
        message_pin("", message_id)


def test_message_pin_invalid_message_id(register_send_message):
    token = register_send_message[0]
    with pytest.raises(InputError):
        message_pin(token, INVALID_ID)


def test_message_pin_success(register_send_message):
    token = register_send_message[0]
    message_id = register_send_message[1]
    channel_id = register_send_message[2]

    channels_create(token, 'OwnedByCeline2', True)
    message_send(token, channel_id, "Hello, my name is Celine2")

    message_pin(token, message_id)
    for channel in channels:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                assert message['is_pinned']


def test_message_pin(register_send_message):
    token = register_send_message[0]
    with pytest.raises(InputError):
        message_pin(token, -1)


def test_message_pin_message_already_pinned(register_send_message):
    token, message_id = register_send_message[0], register_send_message[1]

    message_pin(token, message_id)
    with pytest.raises(InputError):
        message_pin(token, message_id)


def test_message_pin_not_member(register_send_message):
    message_id = register_send_message[1]
    # Theresa registered
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']
    with pytest.raises(AccessError):
        message_pin(token_2, message_id)


def test_message_pin_not_owner(register_send_message):
    token_1, message_id = register_send_message[0], register_send_message[1]
    # Theresa registered
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']
    u_2_id = user_2_detail['u_id']
    # add Theresa to channel
    channel_invite(token_1, message_id, u_2_id)

    with pytest.raises(AccessError):
        message_pin(token_2, message_id)

# ==================message_unpin=====================


def test_message_unpin_success(register_send_message):
    token, message_id, channel_id = register_send_message

    channels_create(token, 'OwnedByCeline2', True)
    message_pin(token, message_id)
    for channel in channels:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                assert message['is_pinned']

    message_send(token, channel_id, "Hello, my name is Celine2")
    message_unpin(token, message_id)
    for channel in channels:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                assert not message['is_pinned']


def test_message_unpin(register_send_message):
    token = register_send_message[0]
    with pytest.raises(InputError):
        message_unpin(token, INVALID_ID)


def test_message_unpin_invalid_token(register_send_message):
    message_id = register_send_message[1]
    with pytest.raises(AccessError):
        message_unpin("", message_id)


def test_message_unpin_message_already_unpinned(register_send_message):
    token, message_id = register_send_message[0], register_send_message[1]

    with pytest.raises(InputError):
        message_unpin(token, message_id)


def test_message_unpin_not_member(register_send_message):
    token_1, message_id = register_send_message[0], register_send_message[1]
    # Theresa registered
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']
    message_pin(token_1, message_id)
    with pytest.raises(AccessError):
        message_unpin(token_2, message_id)


def test_message_unpin_not_owner(register_send_message):
    token_1, message_id = register_send_message[0], register_send_message[1]
    # Theresa registered
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']
    u_2_id = user_2_detail['u_id']
    # add Theresa to channel
    channel_invite(token_1, message_id, u_2_id)
    message_pin(token_1, message_id)
    with pytest.raises(AccessError):
        message_unpin(token_2, message_id)
