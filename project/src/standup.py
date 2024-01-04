from Global_variables import *
from error import InputError, AccessError
from datetime import timezone, datetime, timedelta
from message import *
from helper import *
import threading
import time


def standup_start(token, channel_id, length):
    '''
    it is buffered during the X second window 
    then at the end of the X second window a message 
    will be added to the message queue in the channel 
    from the user who started the standup.
    '''
    if not check_channel_exist(channel_id):
        raise InputError("No such channel")

    user_exist = check_user_exist(token)[0]

    if not user_exist or not check_user_in_channel(channel_id, token):
        raise AccessError("Unauthorised user")
    if standup_active(token, channel_id)['is_active']:
        raise InputError("A standup is already active")

    channels[channel_id]['time_finish'] = (datetime.utcnow(
    ) + timedelta(seconds=length)).replace(tzinfo=timezone.utc).timestamp()

    channels[channel_id]['standup_user_token'] = token
    channels[channel_id]['standup_send'] = ""
    channels[channel_id]['standup_thread_started'] = False

    return {
        'time_finish': channels[channel_id]['time_finish'],
    }


def standup_active(token, channel_id):
    '''
    For a given channel, return whether a standup is active in it, 
    and what time the standup finishes. 
    If no standup is active, then time_finish returns None
    '''

    if not check_channel_exist(channel_id):
        raise InputError("No such channel")

    if not check_user_in_channel(channel_id, token):
        raise AccessError("Unauthorised user")

    is_active = False
    if channels[channel_id]['time_finish'] < datetime.utcnow().replace(tzinfo=timezone.utc).timestamp():
        is_active = False
        time_finish = None
    else:
        is_active = True
        time_finish = channels[channel_id]['time_finish']

    return {
        'is_active': is_active,
        'time_finish': time_finish,
    }


def standup_send(token, channel_id, message):
    '''
    Sending a message to get buffered in the standup queue, 
    assuming a standup is currently active
    '''
    if len(message) > 1000:
        raise InputError("Message to long.")

    channel_exist = False
    for each_channel in channels:
        if each_channel['channel_id'] == channel_id:
            channel_exist = True

    if not channel_exist:
        raise InputError("No such channel.")

    user_exist = False
    for each_user in users_detail:
        if each_user['token'] == token:
            u_id = each_user['u_id']
            name = each_user['handle']
            user_exist = True

    user_in_channel = False
    if user_exist and channel_exist:
        if u_id in channels[channel_id]['all_mem']:
            user_in_channel = True

    if not user_exist or not user_in_channel:
        raise AccessError("Unauthorised user")

    if not standup_active(token, channel_id)['is_active']:
        raise InputError("No standup running.")

    # Add new messages waiting to be sent
    channels[channel_id]['standup_send'] = channels[channel_id]['standup_send'] + \
        f"{name}: {message}\n"

    # Tag the threading if the first message is received
    if channels[channel_id]['standup_thread_started'] == False:
        channels[channel_id]['standup_thread_started'] = True

        time_finish = standup_active(token, channel_id)[
            'time_finish']
        delay = time_finish - datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()

        thread_1 = threading.Thread(target=send_thread, args=(
            channels[channel_id]['standup_user_token'], channel_id, delay))
        thread_1.start()

    return {}


def send_thread(token, channel_id, delay):
    '''
    New thread for send a message in standup
    '''
    time.sleep(delay)
    message_send(token, channel_id, channels[channel_id]['standup_send'])
    channels[channel_id]['standup_send'] = ""
    channels[channel_id]['standup_thread_started'] = False
    return {}
