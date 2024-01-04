'''
This file contains functions that can send, modify and delete messages in a channel
'''
from datetime import timezone, datetime, timedelta
from Global_variables import users_detail, channels
import Global_variables as globals
from error import InputError, AccessError
import threading
import time
from helper import *

INVALID_ID = -1


def message_send(token, channel_id, message):
    '''
    Send a message from the authorised user to channel with channel_id. The message cannot be
    longer than 1000 characters. And the user should have already joined the channel.
    '''
    print(users_detail)
    user_is_exist = False
    channel_is_exist = False
    is_in_channel = False
    u_id = -1
    user_is_exist, u_id = check_user_exist(token)
    for channel in channels:
        if channel_id == channel['channel_id']:
            channel_is_exist = True
            if u_id in channel['all_mem']:
                is_in_channel = True
    if not channel_is_exist:
        raise InputError("channel does not exist")
    print(user_is_exist, u_id, is_in_channel)
    if not user_is_exist or not is_in_channel:
        raise AccessError(
            "the authorised user not joined the channel they are trying to post to")
    if len(message) > 1000:
        raise InputError("Message is more than 1000 characters")
    msg = {
        'message_id': globals.total_message,
        'u_id': u_id,
        'message': message,
        'time_created': int(datetime.now().replace(tzinfo=timezone.utc).timestamp()),
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False,
            }
        ],
        'is_pinned': False,
    }
    channels[channel_id]['messages'].append(msg)

    globals.total_message += 1
    return {
        'message_id': int(msg['message_id'])
    }


def message_remove(token, message_id):
    '''
    This fucntion will remove a message with message_id only if this message
    is sent by the person requested or the person is an owner of the channel.
    '''

    message_id_exist = False
    user_is_authorised = False
    user_is_owner = False
    user_is_exist, u_id = check_user_exist(token)
    channel_num = 0
    message_num = 0

    if not user_is_exist:
        raise AccessError("User is not exist")
    for channel in channels:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                if message['u_id'] == u_id:
                    user_is_authorised = True
                message_id_exist = True
                if u_id in channel['owner_id']:
                    user_is_owner = True
            if not message_id_exist:
                message_num += 1
        if not message_id_exist:
            channel_num += 1

    if not user_is_authorised and not user_is_owner:
        if not message_id_exist:
            raise InputError("Message (based on ID) no longer exists")
        raise AccessError("NO Authority to remove")

    del channels[channel_num]['messages'][message_num]
    return {
    }


def message_edit(token, message_id, message):
    '''
    Given a nessage, update it's new next. If the message
    is an empty string, the message is deleted.
    '''
    # Find the corresponding user_id given by the token
    user_found, u_id = check_user_exist(token)

    if not user_found:
        raise Exception('Unauthorised user.')

    for each_channel in channels:
        for each_msg in each_channel['messages']:
            if each_msg['message_id'] == message_id and \
                    (u_id == each_msg['u_id'] or u_id in each_channel['owner_id']):
                if message != '':
                    each_msg['message'] = message
                    each_msg['u_id'] = u_id
                    each_msg['time_create'] = datetime.now().replace(
                        tzinfo=timezone.utc).timestamp()
                else:
                    each_channel['messages'].remove(each_msg)

            elif each_msg['message_id'] == message_id:
                raise AccessError('Cannot edit the message.')

    return {
    }


################################################# message/sendlater ######################################################
def message_sendlater(token, channel_id, message, time_sent):
    '''
    Send a message from authorised_user to the channel specified by
    channel_id automatically at a specified time in the future
    '''

    # Check time sent
    date = datetime.fromtimestamp(time_sent)
    time_sent = date.replace(tzinfo=timezone.utc).timestamp()
    if (time_sent < int(datetime.now().replace(tzinfo=timezone.utc).timestamp())):
        raise InputError("Time sent is a time in the past")
    
    # Check msg length
    if len(message) > 1000:
        raise InputError("Message is more than 1000 characters")

    # Check user exists
    u_id = get_user_data('token', token, 'u_id')


    channel_is_exist = False
    is_in_channel = False
    for channel in channels:
        if channel['channel_id'] == channel_id:
            channel_is_exist = True
            if u_id in channel['all_mem']:
                is_in_channel = True

    if not channel_is_exist:
        raise InputError("Channel ID is not a valid channel")
    if not is_in_channel:
        raise AccessError(
            "the authorised user has not joined the channel they are trying to post to")

    message_id = globals.total_message
    delay = time_sent - \
        int(datetime.now().replace(tzinfo=timezone.utc).timestamp())
    
    # Another thread created
    thread_1 = threading.Timer(delay, sendlater_thread, args=(
        u_id, channel_id, message, message_id))
    thread_1.start()
    globals.total_message += 1
    return {
        'message_id': message_id,
    }

# The thread for msg_sendlater
def sendlater_thread(u_id, channel_id, message, message_id):
    new_msg = {
        'message_id': message_id,
        'u_id': u_id,
        'message': message,
        'time_created': int(datetime.now().replace(tzinfo=timezone.utc).timestamp()),
        'reacts': [],
    }
    channels[channel_id]['messages'].append(new_msg)

################################################# message_react ##########################################################


def message_react(token, message_id, react_id):
    '''
    Given a message within a channel the authorised user is part of,
    add a "react" to that particular message
    '''

    if not react_id == 1:
        raise InputError("react_id is not a valid React ID. ")

    token_to_id = INVALID_ID

    for user in users_detail:
        if user['token'] == token:
            token_to_id = user['u_id']

    if token_to_id == INVALID_ID:
        raise InputError("user not exist")

    for channel in channels:
        for message in channel['messages']:
            if message_id == message['message_id']:
                if not token_to_id in channel['all_mem']:
                    raise InputError("authorised user not in this channel")
                if token_to_id in message['reacts'][react_id - 1]['u_ids']:
                    raise InputError("user already reacted")
                message['reacts'][react_id - 1]['u_ids'].append(token_to_id)
                message['reacts'][react_id - 1]['is_this_user_reacted'] = True
                return {}

    raise InputError("message_id not exist")


################################################# message_unreact ########################################################


def message_unreact(token, message_id, react_id):
    '''
    Given a message within a channel the authorised user is part of, 
    remove a "react" to that particular message
    '''

    if not react_id == 1:
        raise InputError("react_id is not a valid React ID. ")

    token_to_id = INVALID_ID

    for user in users_detail:
        if user['token'] == token:
            token_to_id = user['u_id']

    if token_to_id == INVALID_ID:
        raise InputError("user not exist")

    for channel in channels:
        for message in channel['messages']:
            if message_id == message['message_id']:
                if not token_to_id in channel['all_mem']:
                    raise InputError("authorised user not in this channel")
                if not token_to_id in message['reacts'][react_id - 1]['u_ids']:
                    raise InputError("user already reacted")
                message['reacts'][react_id - 1]['u_ids'].remove(token_to_id)
                message['reacts'][react_id - 1]['is_this_user_reacted'] = False
                return {}

    raise InputError("message_id not exist")


# ==============================message_pin===========================


def message_pin(token, message_id):
    '''
    Given a message within a channel, mark it as "pinned" to be given 
    special display treatment by the frontend
    '''
    # Find the corresponding user_id given by the token
    valid_token = check_user_data_exists('token', token)
    if not valid_token:
        raise AccessError('Unauthorised user.')
    u_id = get_user_data('token', token, 'u_id')

    # find the channel that the message is within
    for channel in channels:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                # check the auth user is in the channel
                if not u_id in channel['all_mem']:
                    raise AccessError(
                        "the user is not in the channel that the message is with in")
                
                # check the auth user is the owner
                if not u_id in channel['owner_id']:
                    raise AccessError("the user is not the owner of the channel")
                
                if not message['is_pinned']:
                    message['is_pinned'] = True
                    return {}
                else:
                    raise InputError("message is already pinned")
        
    raise InputError("invalid message id")




# =======================message_unpin===========================
def message_unpin(token, message_id):
    '''
    Given a message within a channel, remove it's mark as unpinned
    '''
    # Find the corresponding user_id given by the token
    valid_token = check_user_data_exists('token', token)
    if not valid_token:
        raise AccessError('Unauthorised user.')
    u_id = get_user_data('token', token, 'u_id')

    # find the channel that the message is within
    for channel in channels:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                # check the auth user is in the channel
                if not u_id in channel['all_mem']:
                    raise AccessError(
                        "the user is not in the channel that the message is with in")
                
                # check the auth user is the owner
                if not u_id in channel['owner_id']:
                    raise AccessError("the user is not the owner of the channel")
                
                if message['is_pinned']:
                    message['is_pinned'] = False
                    return {}
                else:
                    raise InputError("message is already unpinned")
        
    raise InputError("invalid message id")

