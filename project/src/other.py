import Global_variables as globals
from Global_variables import *
from error import InputError, AccessError
from auth import create_handle
from helper import *

owners = 1
members = 2


def users_all(token):
    '''
    Returns a list of all users and their associated details
    '''
    global users_detail
    return_user = []

    # check if the token is vaild
    user_exist = check_user_exist(token)[0]

    if user_exist:
        for user in users_detail:
            return_user.append(
                {
                    'u_id': user["u_id"],
                    'email': user["user_email"],
                    'name_first': user["first_name"],
                    'name_last': user["last_name"],
                    'handle_str': create_handle(user["first_name"], user["last_name"]),
                    'profile_img_url': user['profile_img_url']
                }
            )
        return return_user
    else:
        raise AccessError('Token is invalid')


def clear():
    globals.users_detail.clear()
    globals.channels.clear()
    globals.total_message = 0


def admin_userpermission_change(token, u_id, permission_id):
    '''
    Given a User by their user ID, set their permissions to new permissions described by permission_id
    '''
    user_found = False
    for each_user in users_detail:
        if each_user['token'] == token:
            if each_user['permission'] != owners:
                raise AccessError("You cannot set other users' permissions.")

        if each_user['u_id'] == u_id:
            user_found = True

    if not user_found:
        raise InputError('Unauthorised user.')
    if permission_id != owners and permission_id != members:
        raise InputError('Invalid permission_id')

    users_detail[u_id]['permission'] = permission_id


def search(token, query_str):
    '''
    Given a query string, return a collection of messages in all of the channels 
    that the user has joined that match the query
    '''
    global message
    global users_detail
    return_message = []

    # check if the token is vaild
    u_id = check_user_exist(token)[1]

    # raise access error if token is invalid
    if u_id == -1:
        raise AccessError("Invalid token")

    else:
        # check the user is in the channels
        for channel in channels:
            if u_id in channel["all_mem"]:
                # the query_str exist in current channel message
                for message in channel["messages"]:
                    if not message["message"].find(query_str) == -1:
                        return_message.append(message)

        return return_message
