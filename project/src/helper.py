from Global_variables import *
from error import *


def check_channel_exist(channel_id):
    channel_exist = False
    for each_channel in channels:
        if each_channel['channel_id'] == channel_id:
            channel_exist = True
    return channel_exist


def check_user_exist(token):
    user_exist = False
    u_id = -1
    for each_user in users_detail:
        if each_user['token'] == token:
            user_exist = True
            u_id = each_user['u_id']
    return user_exist, u_id


def check_user_in_channel(channel_id, token):
    user_in_channel = False
    user_exist, u_id = check_user_exist(token)
    if user_exist and check_channel_exist(channel_id):
        if u_id in channels[channel_id]['all_mem']:
            user_in_channel = True
    return user_in_channel


def check_user_data_exists(data_type, data_value):
    '''
    Checks if there exists a user with a certain point of data
    ie.
        if data_type:token = value exists
        if data_type:email = value exists
    Returns a boolean, True if the data exists and false if it does not
    '''

    for user in users_detail:
        if user[data_type] == data_value:
            return True
    return False


def get_user_data(checking_type, checking_value, return_datatype):
    '''
    Gets one piece of data from the users_detail database (eg password or uid)

    Takes in a checking type and value which is used to identify the correct user,
    then a return type which is what data should be returned.
    ie get_user_data(email,example@gmail.com,handle) returns a handle value

    Returns the information or raises an error if the user can't be found.
    '''

    for user in users_detail:
        if user[checking_type] == checking_value:
            return user[return_datatype]

    raise InputError('The user input information is incorrect!')


def change_user_data(checking_type, checking_value, change_datatype, change_value):
    '''
    Changes one piece of user data when inputed with the checking data type to find the right user.
    When correct user is found, uses change datatype to set new value.

    ie checking_type:token = token value
        then change change_datatype:email to new email value

    If successful, returns nothing.
    If unsuccessful, raises and error.
    '''

    global users_detail
    i = 0
    for user in users_detail:
        if user[checking_type] == checking_value:
            users_detail[i][change_datatype] = change_value
            return True
        i += 1
    return False
