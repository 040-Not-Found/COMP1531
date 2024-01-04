from Global_variables import users_detail, channels
from error import InputError, AccessError
from helper import *
logged_in = 0
logged_out = 1


def channels_list(token):
    '''
    Provide a list of all channels (and their associated details) that the authorised user is part of
    '''
    # Create a new dictionary to store all the return values
    channels_list_of_user = []

    # Fetch the userid corresponding to the token
    user_exist, u_id = check_user_exist(token)

    # Find all the channels that the user belongs to
    # and store them in a new list of dictionaries
    if user_exist and token != "":
        for channel in channels:
            if u_id in channel['all_mem']:
                insert_channel = {
                    'channel_id': channel['channel_id'],
                    'name': channel['channel_name'],
                }
                channels_list_of_user.append(insert_channel)
    else:
        raise AccessError('You have already logged out')

    return channels_list_of_user


def channels_listall(token):
    '''
    Provide a list of all channels (and their associated details)
    '''
    # Create a new list of dictionary
    list_all = []

    # If an unauthorised token was passed in, return an empty list
    user_exist = check_user_exist(token)[0]

    # if the user stay logged in, return all channels
    if user_exist and token != "":
        for channel in channels:
            if channel['is_public']:
                insert_channel = {
                    'channel_id': channel['channel_id'],
                    'name': channel['channel_name'],
                }
                list_all.append(insert_channel)
    else:
        raise AccessError('You have already logged out.')

    return list_all


def channels_create(token, name, is_public):
    '''
    Creates a new channel with that name that is either a public or private channel
    '''
    global channels
    # Initialize the user_id to unauthorised user
    user_id = check_user_exist(token)[1]

    # if the name is less than or equal to 20 char and the user is authorised, return the channel_id of the new channel
    if len(name) > 20:
        raise InputError('Channel_name too long.')
    # An unregistered or a logged_out user will not be able to create a new channel
    elif user_id == -1 or token == "":
        raise AccessError('You have already logged out.')
    else:
        new_channel = {}
        channel_id = len(channels)
        new_channel['channel_id'] = channel_id
        new_channel['channel_name'] = name
        new_channel['is_public'] = is_public
        new_channel['owner_id'] = [user_id]
        new_channel['all_mem'] = [user_id]
        new_channel['messages'] = []
        new_channel['time_finish'] = -1

        channels.append(new_channel)

    return {'channel_id': channel_id}
