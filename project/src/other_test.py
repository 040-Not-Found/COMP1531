import pytest
from Global_variables import users_detail, channels
from auth import auth_login, auth_logout, auth_register
from channels import channels_list, channels_listall, channels_create
from channel import channel_invite, channel_details, channel_messages, channel_leave
from error import InputError, AccessError
from other import clear, admin_userpermission_change, search, users_all
from message import *

owners = 1
members = 2


def test_permission_not_global_owner():
    clear()
    # First user logged in (Global owner permission)
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    u_1_id = user_1_detail['u_id']

    # Second user logged in (Global member)
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']

    with pytest.raises(AccessError):
        admin_userpermission_change(token_2, u_1_id, members)

    # Third user logged in (Member of channel)
    auth_register('hello@gmail.com', 'blahblah', 'hello', 'there')
    user_3_detail = auth_login('hello@gmail.com', 'blahblah')
    u_3_id = user_3_detail['u_id']

    with pytest.raises(AccessError):
        admin_userpermission_change(token_2, u_3_id, owners)


# Invalid user will raise InputError
def test_permission_invalid_user():
    clear()
    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    invalid_user = 2
    with pytest.raises(InputError):
        admin_userpermission_change(token_1, invalid_user, owners)


# Invalid permission will raise InputError
def test_permission_invalid_permission():
    clear()
    # First user logged in (Global owner)
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    # Second user logged in (Global member)
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    u_2_id = user_2_detail['u_id']

    invalid_permission = 3
    with pytest.raises(InputError):
        admin_userpermission_change(token_1, u_2_id, invalid_permission)


def test_permission_global_owner():
    clear()
    # First user logged in (Global owner)
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    # Second user logged in (Global member)
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')

    u_2_id = user_2_detail['u_id']

    admin_userpermission_change(token_1, u_2_id, owners)
    assert users_detail[u_2_id]['permission'] == owners

    admin_userpermission_change(token_1, u_2_id, members)
    assert users_detail[u_2_id]['permission'] == members

# ================================SEARCH=====================================


@pytest.fixture
def register_send_msg():
    clear()
    # user register
    auth_register('theresa@gmail.com', '1234567', 'Theresa', 'Tao')
    user_1_detail = auth_login('theresa@gmail.com', '1234567')
    token_1 = user_1_detail['token']

    # user crearte a channel
    channel_info = channels_create(token_1, 'OwnedByTheresa', True)
    channel_id = channel_info['channel_id']

    return token_1, channel_id


def test_search_all_msg(register_send_msg):
    token_1, channel_id = register_send_msg
    # user send messages
    message_info_0 = message_send(token_1, channel_id, "Search test: qwerty")
    message_id_0 = message_info_0['message_id']

    message_info_1 = message_send(token_1, channel_id, "Search test: asdfgh")
    message_id_1 = message_info_1['message_id']

    channel_info_2 = channels_create(token_1, 'OwnedByTheresa2', True)
    channel_leave(token_1, channel_info_2['channel_id'])

    # test1
    query_str = "qwerty"
    list_of_msg_1 = search(token_1, query_str)

    assert len(list_of_msg_1) == 1

    found = False
    for msg in list_of_msg_1:
        if msg['message_id'] == message_id_0:
            found = True

    assert found

    # test2
    query_str = "test"
    list_of_msg_2 = search(token_1, query_str)

    assert len(list_of_msg_2) == 2

    found_0 = False
    found_1 = False
    for msg in list_of_msg_2:
        if msg['message_id'] == message_id_0:
            found_0 = True
        if msg['message_id'] == message_id_1:
            found_1 = True

    assert found_0 and found_1

    # test3
    query_str = "zxcvb"
    list_of_msg_3 = search(token_1, query_str)

    assert list_of_msg_3 == []


def test_search_invalid_token():
    with pytest.raises(AccessError):
        search(-1, "Test")


@pytest.fixture
def user_register():
    clear()

    # user register
    auth_register('vicky@gmail.com', '12345678', 'Vicky', 'Hu')
    user_1_detail = auth_login('vicky@gmail.com', '12345678')
    token_1 = user_1_detail['token']

    auth_register('theresa@gmail.com', '87654321', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '87654321')
    token_2 = user_2_detail['token']
    auth_logout(token_2)

    return token_1, token_2


# this function test multiple, logged_in and logged_out users

def test_users_all(user_register):
    token_1 = user_register[0]
    assert users_all(token_1) == [
        {
            'u_id': 0,
            'email': "vicky@gmail.com",
            'name_first': "Vicky",
            'name_last': "Hu",
            'handle_str': "VickyHu",
            'profile_img_url': "",
        },
        {
            'u_id': 1,
            'email': "theresa@gmail.com",
            'name_first': "Theresa",
            'name_last': "Tao",
            'handle_str': "TheresaTao",
            'profile_img_url': "",
        }
    ]


def test_users_all_invalid_token():
    with pytest.raises(AccessError):
        users_all(-1)
