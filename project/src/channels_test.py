import pytest
from Global_variables import channels
from auth import auth_login, auth_logout, auth_register
from channels import channels_list, channels_listall, channels_create
from channel import channel_invite, channel_details
from error import InputError, AccessError
from other import clear

'''This is a test file for channels.py '''

##### TESTS FOR channels_list #####


def test_channels_list_none():
    '''
    Test that an authorised user belongs to no channel
    '''
    clear()
    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    assert channels_list(token_1) == []


# Test to display the channels even if the user is not the owner of any ones
def test_channels_list_not_owner():
    clear()

    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']
    u_1_id = user_1_detail['u_id']

    # Second user logged in
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']

    channels_create(token_2, 'OwnedByTheresa', False)

    # Second user created a new channel
    channel_info = channels_create(token_2, 'OwnedBytheresa', True)
    channel_id = channel_info['channel_id']

    # Invite the first user to the channel
    channel_invite(token_2, channel_id, u_1_id)

    # Extract the core info from the channel details
    channel_info = channel_details(token_1, channel_id)
    result = [
        {
            'channel_id': channel_id,
            'name': channel_info['name']
        },
    ]
    assert channels_list(token_1) == result


# Test that the input user is the owner of some channels
def test_channels_list_is_owner():
    clear()

    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    # The user created a new channel
    channel_info = channels_create(token_1, 'OwnedByCeline', True)
    channel_id = channel_info['channel_id']

    # Extract the core info from the channel details
    channel_info = channel_details(token_1, channel_id)
    result = [
        {
            'channel_id': channel_id,
            'name': channel_info['name']
        },
    ]
    assert channels_list(token_1) == result


# Test if the returned list of channels include private ones
def test_channels_list_isprivate():
    clear()

    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    # The user created a new channel
    channel_info = channels_create(token_1, 'OwnedByCeline', True)
    channel_id = channel_info['channel_id']

    # Extract the core info from the channel details
    channel_info = channel_details(token_1, channel_id)
    result = [
        {
            'channel_id': channel_id,
            'name': channel_info['name']
        },
    ]
    assert channels_list(token_1) == result


# Test if an authorised user logged out, exception raises
def test_channels_list_logged_out():
    clear()

    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    # The user created a new channel
    channels_create(token_1, 'OwnedByCeline', True)

    # The user then logged out
    auth_logout(token_1)

    with pytest.raises(Exception):
        channels_list(token_1)


##### TESTS FOR channels_listall #####

# Test that an authorised user who are logged out will raise exception
def test_channels_listall_logged_out():
    clear()

    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    channels_create(token_1, 'OwnedByCeline1', False)
    channels_create(token_1, 'OwnedByCeline2', True)

    # The user then logged out
    auth_logout(token_1)
    with pytest.raises(Exception):
        channels_listall(token_1)


# Test that an empty list will be returned if no channel has been created
def test_channels_listall_no_channels():
    clear()

    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    # No channels being created
    assert channels_listall(token_1) == []


# Test that list all channels if the token is authorised
def test_channels_listall_valid_user():
    clear()

    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    # The user created a new channel
    channel_info = channels_create(token_1, 'OwnedByCeline', True)
    channel_id = channel_info['channel_id']

    # Extract the core info from the channel details
    channel_info = channel_details(token_1, channel_id)
    result = [
        {
            'channel_id': channel_id,
            'name': channel_info['name']
        },
    ]

    assert channels_listall(token_1) == result


##### Tests for channels_create #####

# Test if an authorised user who is logged out cannot create a new channel, raises exception
def test_channels_create_logged_out():
    clear()

    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    # The user then logged out
    auth_logout(token_1)

    assert channels == []
    with pytest.raises(Exception):
        channels_create(token_1, 'newChannel', True)


# Test that a new public channel is created by a valid token with its name less than 20 characters
def test_channels_create_short_pub():
    clear()

    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    # The user created a new channel
    channel_info = channels_create(token_1, 'OwnedByCeline', True)
    channel_id = channel_info['channel_id']

    found = False
    for each_channel in channels:
        if channel_id == each_channel['channel_id']:
            found = True

    assert found == True


# Test that a new private channel is created by a valid token with its name less than 20 characters
def test_channels_create_short_pri():
    clear()

    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    # The user created a new channel
    channel_info = channels_create(token_1, 'newChannel', True)
    channel_id = channel_info['channel_id']

    found = False
    for each_channel in channels:
        if channel_id == each_channel['channel_id']:
            found = True

    assert found == True


# Test that two channels are creates with their names less than 20 characters
def test_channels_create_short_pub_two():
    clear()

    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    # Create a new channel

    channel_info_1 = channels_create(token_1, 'newChannel1', True)
    channel_id_1 = channel_info_1['channel_id']

    channel_info_2 = channels_create(token_1, 'OwnedByCeline', True)
    channel_id_2 = channel_info_2['channel_id']

    found1 = False
    found2 = False
    for each_channel in channels:
        if channel_id_1 == each_channel['channel_id']:
            found1 = True
        if channel_id_2 == each_channel['channel_id']:
            found2 = True

    assert (found1 == True and found2 == True)


# Test that a new public channel is created by a valid token with its name with 20 characters
def test_channels_create_20_pub():
    clear()

    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    # The user created a new channel
    channel_info = channels_create(token_1, 'ThisChannelHasName20', True)
    channel_id = channel_info['channel_id']

    found = False
    for each_channel in channels:
        if channel_id == each_channel['channel_id']:
            found = True

    assert found == True


# Test that a new private channel is created by a valid token with its name with 20 characters
def test_channels_create_20_pri():
    clear()

    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    # The user created a new channel
    channel_info = channels_create(token_1, 'ThisChannelHasName20', False)
    channel_id = channel_info['channel_id']

    found = False
    for each_channel in channels:
        if channel_id == each_channel['channel_id']:
            found = True

    assert found == True


# Test that a new public channel created with its name more than 20 characters will raise InputError
def test_channels_create_long_pub():
    clear()
    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    with pytest.raises(InputError):
        channels_create(
            token_1, 'new----channels---larger---than---20---char', True)


# Test that a new private channel created
# with its name more than 20 characters will raise InputError
def test_channels_create_long_pri():
    clear()
    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    with pytest.raises(InputError):
        channels_create(
            token_1, 'new----channels---larger---than---20---char', False)
