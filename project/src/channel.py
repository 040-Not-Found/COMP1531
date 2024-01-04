from Global_variables import *
from error import *
from channels import *
from helper import *


def channel_invite(token, channel_id, u_id):
    '''
    Invites a user (with user id u_id) to join a channel with ID channel_id. 
    Once invited the user is added to the channel immediately
    '''
    # set all variables to False first to check if it exists
    user_is_exist = False
    token_to_id = -1
    # loop the channels to check if the input channel_id exists
    # if so, set channel_is_exist to True
    channel_is_exist = check_channel_exist(channel_id)
    # if the channel_id is not exist, raise InputError
    if not channel_is_exist:
        raise InputError("channel_id does not refer to a valid channel.")
    # loop the users_detail to check if u_id exists
    # if so, set user_is_exist to True
    # when the token is matches one's email, set token_to_id to that user's u_id
    for user in users_detail:
        if user["u_id"] == u_id:
            user_is_exist = True
            permission = user['permission']
        if user["token"] == token:
            token_to_id = user["u_id"]
    # if user doesn't exist, raise an InputError
    if not user_is_exist:
        raise InputError("u_id does not refer to a valid user")
    # if cannot find the correspond u_id of the token, then raise AccessError
    if token_to_id not in channels[channel_id]["all_mem"]:
        raise AccessError(
            "the authorised user is not already a member of the channel")
    # check the condition if the channel is private
    # if so, only the owner can invite others
    # if not, all members in the channel can invite others
    # if the person be invited has already in the channel, nothing happen
    if not u_id in channels[channel_id]["all_mem"]:
        channels[channel_id]["all_mem"].append(u_id)
        if permission == 1:
            channels[channel_id]['owner_id'].append(u_id)
    return {}


def channel_details(token, channel_id):
    '''
    Given a Channel with ID channel_id that the authorised user is part of, 
    provide basic details about the channel
    '''
    channel_info = {}
    channel_is_exist = check_channel_exist(channel_id)
    token_to_id = -1
    if not channel_is_exist:
        raise InputError("Channel ID is not a valid channel")

    owner_id = channels[channel_id]["owner_id"]
    member_id = channels[channel_id]["all_mem"]
    owner = []
    member = []
    # create empty onwer_info and member_info dictionaries through each loop
    # add required info to the dictionaries.
    # append the dictionaries to the member list
    for user in users_detail:
        owner_info = {}
        member_info = {}
        if user["token"] == token:
            token_to_id = user["u_id"]
        if user["u_id"] in owner_id:
            owner_info['u_id'] = user["u_id"]
            owner_info['name_first'] = user['first_name']
            owner_info['name_last'] = user['last_name']
            owner_info['profile_img_url'] = user['profile_img_url']
            owner.append(owner_info)
        if user["u_id"] in member_id:
            member_info['u_id'] = user["u_id"]
            member_info['name_first'] = user['first_name']
            member_info['name_last'] = user["last_name"]
            member_info['profile_img_url'] = user['profile_img_url']
            member.append(member_info)

        #raise AccessError
    if not token_to_id in channels[channel_id]["all_mem"]:
        raise AccessError(
            "Authorised user is not a member of channel with channel_id")
    channel_info["name"] = channels[channel_id]["channel_name"]
    channel_info["owner_members"] = owner
    channel_info["all_members"] = member
    return channel_info


def channel_messages(token, channel_id, start):
    '''
    Given a Channel with ID channel_id that the authorised user is part of, 
	return up to 50 messages between index "start" and "start + 50". 
	Message with index 0 is the most recent message in the channel. 
	This function returns a new index "end" which is the value of "start + 50",
	or, if this function has returned the least recent messages in the channel, 
	returns -1 in "end" to indicate there are no more messages to load after this return.
    '''
    channel_is_exist = check_channel_exist(channel_id)
    if not channel_is_exist:
        raise InputError("Channel ID is not a valid channel")
    # count the length of the message sizes
    message_size = len(channels[channel_id]["messages"])
    # case that start index is greater than the total number of messages
    if start > message_size:
        raise InputError(
            "start is greater than the total number of messages in the channel")
    if message_size - 1 - start >= 50:
        end = start + 50
    else:
        end = -1
    token_to_id = check_user_exist(token)[1]
    if token_to_id == -1:
        raise AccessError(
            "Authorised user is not a member of channel with channel_id")
    if not token_to_id in channels[channel_id]["all_mem"]:
        raise AccessError(
            "Authorised user is not a member of channel with channel_id")
    result = {}
    result["messages"] = []
    # if number of messages are greater than 50
    # append the recent 50 messages
    # else, append all messages, end = -1
    if end != -1:
        for i in range(end):
            result["messages"].append(channels[channel_id]["messages"][i])
    else:
        for i in range(message_size):
            result["messages"].append(channels[channel_id]["messages"][i])
    result["start"] = start
    result["end"] = end

    return result


def channel_leave(token, channel_id):
    '''
    Given a channel ID, the user removed as a member of this channel
    '''
    channel_is_exist = False
    token_to_id = -1
    auth_user_of_channel = False

    for channel in channels:
        if (channel["channel_id"] == channel_id):
            channel_is_exist = True
            memberList = channels[channel_id].get("all_mem")
    if not channel_is_exist:
        raise InputError("channel_id does not refer to a valid channel.")

    token_to_id = check_user_exist(token)[1]
    if token_to_id == -1:
        raise InputError("token does not refer to a valid user.")

    for member in memberList:
        if member == token_to_id:
            auth_user_of_channel = True
            for person in memberList:
                if person == token_to_id:
                    memberList.remove(person)
    if auth_user_of_channel == False:
        raise AccessError(
            "Authorised user is not a member of channel with channel_id")

    return {

    }


def channel_join(token, channel_id):
    '''
    Given a channel_id of a channel that the authorised user can join, adds them to that channel
    '''
    channel_is_exist = False
    token_to_id = -1
    channel_already_joined = False
    public_channel = True

    for channel in channels:
        if (channel["channel_id"] == channel_id):
            channel_is_exist = True
            memberList = channels[channel_id].get("all_mem")
            public_channel = channels[channel_id].get("is_public")
    if not channel_is_exist:
        raise InputError("channel_id does not refer to a valid channel.")

    for user in users_detail:
        if (user["token"] == token):
            token_to_id = user["u_id"]
            permission = user['permission']

    if token_to_id == -1:
        raise InputError("token does not refer to a valid user.")

    for member in memberList:
        if member == token_to_id:
            channel_already_joined = True
            raise AccessError("User already joined the channel")

    if channel_already_joined == False and public_channel == True:
        channels[channel_id]['all_mem'].append(token_to_id)
        if permission == 1:
            channels[channel_id]['owner_id'].append(token_to_id)
    else:
        raise AccessError("channel_id refers to a channel that is private")


def channel_addowner(token, channel_id, u_id):
    '''
    Make user with user id u_id an owner of this channel
    '''
    global channels
    channel_exist = check_channel_exist(channel_id)
    owner_exist = False
    correct_auth_user = False

    # Channel ID is a valid channel

    # the user with user id u_id is not an owner of the channel
    if channel_exist == True:
        owner = channels[channel_id]["owner_id"]
        if u_id in owner:
            owner_exist = True
        # the authorsing user is the owner
        for user in users_detail:
            if token == user["token"]:
                auth_id = user["u_id"]
                status = user['token']
                permission_id = user['permission']

        owner = channels[channel_id]["owner_id"]
        if auth_id in owner:
            correct_auth_user = True
        if permission_id == 1:
            correct_auth_user = True
    if not channel_exist or owner_exist:
        raise InputError(
            "Channel not found or user is not an owner of the channel.")
    elif not correct_auth_user or status == '':
        raise AccessError(
            "You are not an owner of the channel, cannot remove others.")
    else:
        channels[channel_id]['owner_id'].append(u_id)

    return {}


def channel_removeowner(token, channel_id, u_id):
    '''
    Remove user with user id u_id an owner of this channel
    '''
    channel_exist = check_channel_exist(channel_id)
    owner_exist = False
    correct_auth_user = False

    # the user with user id u_id is not an owner of the channel
    if channel_exist == True:
        owner = channels[channel_id]["owner_id"]
        if u_id in owner:
            owner_exist = True

        auth_id = -1
        # the authorsing user is the owner
        auth_id = check_user_exist(token)[1]

        owner = channels[channel_id]["owner_id"]
        if auth_id in owner:
            correct_auth_user = True

    if not channel_exist or not owner_exist:
        raise InputError(
            "Channel not found or user is not an owner of the channel.")
    elif not correct_auth_user or token == '':
        raise AccessError(
            "You are not an owner of the channel, cannot remove others.")
    else:
        channels[channel_id]['owner_id'].remove(u_id)
