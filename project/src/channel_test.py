from error import *
from Global_variables import *
import pytest
from channel import *
from other import *
from auth import *
from channels import *
from message import *


Invalid_channel_id = -1
Invalid_user_id = -2
INVALID_ID = -1


def test_channel_invite_InputError():
    clear()
    auth_register("vicky@gmail.com", "12345678", "vicky", "Hu")
    user = auth_login("vicky@gmail.com", "12345678")
    token = user['token']

    channel_id1 = channels_create(token, "cctv1", True)['channel_id']

    user2 = auth_register("peter@gmail.com", "22345678", "peter", "Xie")
    user2_id = user2['u_id']

    with pytest.raises(InputError):
        channel_invite(token, Invalid_channel_id, user2_id)
    with pytest.raises(InputError):
        channel_invite(token, channel_id1, Invalid_user_id)


def test_channel_invite_AccessError():
    clear()
    auth_register("vicky@gmail.com", "12345678", "vicky", "Hu")
    user = auth_login("vicky@gmail.com", "12345678")
    token = user['token']

    channel_id1 = channels_create(token, "cctv1", True)['channel_id']
    channel_id2 = channels_create(token, "cctv2", False)['channel_id']

    auth_register("peter@gmail.com", "22345678", "peter", "Xie")
    user2 = auth_login("peter@gmail.com", "22345678")
    user2_id = user2['u_id']
    user2_token = user2['token']

    user3 = auth_register("anthony@gmail.com", "32345678", "anthony", "Pomes")
    user3_id = user3['u_id']

    with pytest.raises(AccessError):
        channel_invite(user2_token, channel_id1, user3_id)
    assert channel_invite(token, channel_id1, user2_id) == {}
    with pytest.raises(AccessError):
        channel_invite(user2_token, channel_id2, user3_id)


def test_channel_invite_duplicate_case():
    clear()
    auth_register("vicky@gmail.com", "12345678", "vicky", "Hu")
    user = auth_login("vicky@gmail.com", "12345678")
    user_id = user['u_id']
    token = user['token']

    channel_id1 = channels_create(token, "cctv1", True)['channel_id']

    channel_invite(token, channel_id1, user_id)
    assert channel_details(token, channel_id1) == {
        'name': 'cctv1',
        'owner_members': [
            {
                'u_id': user_id,
                'name_first': 'vicky',
                'name_last': 'Hu',
                'profile_img_url': "",
            }
        ],
        'all_members': [
            {
                'u_id': user_id,
                'name_first': 'vicky',
                'name_last': 'Hu',
                'profile_img_url': "",
            }
        ],
    }


def test_channel_invite_public_case():
    clear()
    auth_register("vicky@gmail.com", "12345678", "vicky", "Hu")
    user = auth_login("vicky@gmail.com", "12345678")
    user_id = user['u_id']
    token = user['token']

    channel_id1 = channels_create(token, "cctv1", True)['channel_id']

    auth_register("peter@gmail.com", "22345678", "peter", "Xie")
    user2 = auth_login("peter@gmail.com", "22345678")
    user2_token = user2['token']

    user3 = auth_register("anthony@gmail.com", "32345678", "anthony", "Pomes")
    user3_id = user3['u_id']

    assert channel_details(token, channel_id1) == {
        'name': 'cctv1',
        'owner_members': [
            {
                'u_id': user_id,
                'name_first': 'vicky',
                'name_last': 'Hu',
                'profile_img_url': "",
            }
        ],
        'all_members': [
            {
                'u_id': user_id,
                'name_first': 'vicky',
                'name_last': 'Hu',
                'profile_img_url': "",
            }
        ],
    }
    with pytest.raises(AccessError):
        channel_invite(user2_token, channel_id1, user3_id)

    channel_invite(token, channel_id1, user3_id)
    assert channel_details(token, channel_id1) == {
        'name': 'cctv1',
        'owner_members': [
            {
                'u_id': user_id,
                'name_first': 'vicky',
                'name_last': 'Hu',
                'profile_img_url': "",
            },

        ],
        'all_members': [
            {
                'u_id': user_id,
                'name_first': 'vicky',
                'name_last': 'Hu',
                'profile_img_url': "",
            },
            {
                'u_id': user3_id,
                'name_first': 'anthony',
                'name_last': 'Pomes',
                'profile_img_url': "",
            }
        ],
    }


def test_channel_invite_private_case():
    clear()
    auth_register("vicky@gmail.com", "12345678", "vicky", "Hu")
    user = auth_login("vicky@gmail.com", "12345678")
    user_id = user['u_id']
    token = user['token']

    channel_id1 = channels_create(token, "cctv1", False)['channel_id']

    auth_register("peter@gmail.com", "22345678", "peter", "Xie")
    user2 = auth_login("peter@gmail.com", "22345678")
    user2_id = user2['u_id']

    channel_invite(token, channel_id1, user2_id)
    assert channel_details(token, channel_id1) == {
        'name': 'cctv1',
        'owner_members': [
            {
                'u_id': user_id,
                'name_first': 'vicky',
                'name_last': 'Hu',
                'profile_img_url': "",
            },

        ],
        'all_members': [
            {
                'u_id': user_id,
                'name_first': 'vicky',
                'name_last': 'Hu',
                'profile_img_url': "",
            },
            {
                'u_id': user2_id,
                'name_first': 'peter',
                'name_last': 'Xie',
                'profile_img_url': "",
            }
        ],
    }


def test_global_permission():
    clear()
    auth_register("vicky@gmail.com", "12345678", "vicky", "Hu")
    user = auth_login("vicky@gmail.com", "12345678")
    token = user['token']

    channel_id1 = channels_create(token, "cctv1", True)['channel_id']

    auth_register("peter@gmail.com", "22345678", "peter", "Xie")
    user2 = auth_login("peter@gmail.com", "22345678")
    user2_id = user2['u_id']

    admin_userpermission_change(token, user2_id, owners)

    with pytest.raises(AccessError):
        channel_invite(INVALID_ID, channel_id1, user2_id)

    channel_invite(token, channel_id1, user2_id)
    assert user2_id in channels[channel_id1]['owner_id']
    assert channel_invite(token, channel_id1, user2_id) == {}

    channel_id2 = channels_create(token, "cctv2", False)['channel_id']

    with pytest.raises(AccessError):
        channel_invite(INVALID_ID, channel_id2, user2_id)

    channel_invite(token, channel_id2, user2_id)
    assert channel_invite(token, channel_id2, user2_id) == {}
    assert user2_id in channels[channel_id2]['owner_id']


def test_channel_details_InputError():

    clear()
    auth_register("vicky@gmail.com", "12345678", "vicky", "Hu")
    user = auth_login("vicky@gmail.com", "12345678")
    user_id = user['u_id']

    with pytest.raises(InputError):
        channel_details(user_id, Invalid_channel_id)


def test_channel_details_AccessError():

    clear()
    auth_register("vicky@gmail.com", "12345678", "vicky", "Hu")
    user = auth_login("vicky@gmail.com", "12345678")
    token = user['token']

    channel_id = channels_create(token, "cctv2", False)['channel_id']

    auth_register("peter@gmail.com", "22345678", "peter", "Xie")
    user2 = auth_login("peter@gmail.com", "22345678")
    user2_token = user2['token']

    with pytest.raises(AccessError):
        channel_details(user2_token, channel_id)


def test_channel_details():
    clear()
    auth_register("vicky@gmail.com", "12345678", "vicky", "Hu")
    user = auth_login("vicky@gmail.com", "12345678")
    user_id = user['u_id']
    token = user['token']

    channel_id1 = channels_create(token, "cctv1", True)['channel_id']
    channels_create(token, "cctv2", True)['channel_id']

    user2 = auth_register("peter@gmail.com", "22345678", "peter", "Xie")
    user2_id = user2['u_id']
    channel_invite(token, channel_id1, user2_id)
    assert len(channels[channel_id1]['all_mem']) == 2
    assert channel_details(token, channel_id1) == {
        'name': 'cctv1',
        'owner_members': [
            {
                'u_id': user_id,
                'name_first': 'vicky',
                'name_last': 'Hu',
                'profile_img_url': "",
            }
        ],
        'all_members': [
            {
                'u_id': user_id,
                'name_first': 'vicky',
                'name_last': 'Hu',
                'profile_img_url': "",
            },

            {
                'u_id': user2_id,
                'name_first': 'peter',
                'name_last': 'Xie',
                'profile_img_url': "",
            },

        ],
    }


def test_channel_messages_InputError():
    clear()

    auth_register("vicky@gmail.com", "12345678", "vicky", "Hu")
    user = auth_login("vicky@gmail.com", "12345678")
    token = user['token']
    channel_id1 = channels_create(token, "cctv1", True)['channel_id']
    auth_register("peter@gmail.com", "22345678", "peter", "Xie")
    user2 = auth_login("peter@gmail.com", "22345678")
    user2_token = user2['token']
    with pytest.raises(InputError):
        channel_messages(token, Invalid_channel_id, 0)
    with pytest.raises(InputError):
        channel_messages(token, channel_id1, 1)
    with pytest.raises(InputError):
        channel_messages(user2_token, channel_id1, 5)


def test_channel_messages_AccessError():

    clear()

    auth_register("vicky@gmail.com", "12345678", "vicky", "Hu")
    user = auth_login("vicky@gmail.com", "12345678")
    token = user['token']

    channel_id1 = channels_create(token, "cctv1", True)['channel_id']

    auth_register("peter@gmail.com", "22345678", "peter", "Xie")
    user2 = auth_login("peter@gmail.com", "22345678")
    user2_token = user2['token']

    with pytest.raises(AccessError):
        channel_messages(user2_token, channel_id1, 0)


def test_channel_message_over_50():
    clear()

    auth_register("vicky@gmail.com", "12345678", "vicky", "Hu")
    user = auth_login("vicky@gmail.com", "12345678")
    token = user['token']

    channel_id1 = channels_create(token, "cctv1", True)['channel_id']
    message_send(token, channel_id1, "hello world")

    with pytest.raises(AccessError):
        channel_messages(INVALID_ID, channel_id1, 0)

    message_info1 = channel_messages(token, channel_id1, 0)
    assert message_info1['start'] == 0
    assert message_info1['end'] == -1
    i = 0
    while i < 50:
        message_send(token, channel_id1, "hello world!")
        i += 1
    message_info2 = channel_messages(token, channel_id1, 0)
    assert message_info2['end'] == 50


# channel_addowner
Invalid_channel_id = -1
Invalid_user_id = -2


def test_channel_addowner_InputError():
    clear()
    auth_register("vicky@gmail.com", "12345678", "vicky", "Hu")
    user = auth_login("vicky@gmail.com", "12345678")
    user_id = user['u_id']
    token = user['token']

    channel_id1 = channels_create(token, "cctv1", True)['channel_id']

    user2 = auth_register("peter@gmail.com", "22345678", "peter", "Xie")
    user2_id = user2['u_id']

    assert channels[channel_id1]['owner_id'] == [user_id]
    with pytest.raises(InputError):
        channel_addowner(token, Invalid_channel_id, user_id)
    '''
    with pytest.raises(InputError):
        channel_addowner(token, channel_id1, Invalid_user_id)
    '''
    channel_addowner(token, channel_id1, user2_id)
    with pytest.raises(InputError):
        channel_addowner(token, channel_id1, user2_id)


def test_channel_addOwner_AccessError():
    clear()
    auth_register("vicky@gmail.com", "12345678", "vicky", "Hu")
    user = auth_login("vicky@gmail.com", "12345678")
    token = user['token']

    channel_id1 = channels_create(token, "cctv1", True)['channel_id']

    auth_register("peter@gmail.com", "22345678", "peter", "Xie")
    assert len(channels[channel_id1]['owner_id']) == 1
    user2 = auth_login("peter@gmail.com", "22345678")
    user2_token = user2['token']
    user3 = auth_register("theresa@gmail.com", '32345678', 'theresa', 'Tao')
    user3_id = user3['u_id']
    with pytest.raises(AccessError):
        channel_addowner(user2_token, channel_id1, user3_id)


def test_channel_addOwner_success():
    clear()
    auth_register("vicky@gmail.com", "12345678", "vicky", "Hu")
    user = auth_login("vicky@gmail.com", "12345678")
    token = user['token']

    channel_id1 = channels_create(token, "cctv1", True)['channel_id']

    auth_register("peter@gmail.com", "22345678", "peter", "Xie")
    assert len(channels[channel_id1]['owner_id']) == 1

    user2 = auth_login("peter@gmail.com", "22345678")
    user2_id = user2['u_id']
    user2_token = user2['token']
    user3 = auth_register("theresa@gmail.com", '32345678', 'theresa', 'Tao')
    user3_id = user3['u_id']
    channel_addowner(token, channel_id1, user2_id)
    assert len(channels[channel_id1]['owner_id']) == 2
    channel_addowner(user2_token, channel_id1, user3_id)
    assert len(channels[channel_id1]['owner_id']) == 3


# channel_removeowner

def test_channel_removeowner_InvalidChannel():
    clear()
    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    # Second user logged in
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    u_2_id = user_2_detail['u_id']

    with pytest.raises(InputError):
        channel_removeowner(token_1, 1, u_2_id)


def test_channel_removeowner_NotCreator():
    clear()
    # The user with user id u_id is not an owner of the channel
    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    u_1_id = user_1_detail['u_id']

    # Second user logged in
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']

    # Second user created a new channel
    channel_info = channels_create(token_2, 'OwnedBytheresa', True)
    channel_id = channel_info['channel_id']

    with pytest.raises(InputError):
        channel_removeowner(token_2, channel_id, u_1_id)


def test_channel_removeowner_AccessError():
    clear()
    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    u_1_id = user_1_detail['u_id']

    # Second user logged in
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']

    # Second user created a new channel
    channel_info = channels_create(token_2, 'OwnedBytheresa', True)
    channel_id = channel_info['channel_id']

    channel_addowner(token_2, channel_id, u_1_id)

    auth_logout(token_2)

    with pytest.raises(AccessError):
        channel_removeowner(token_2, channel_id, u_1_id)


def test_channel_removeowner_Not_owner():
    clear()
    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    token_1 = user_1_detail['token']

    # Second user logged in
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']
    u_2_id = user_2_detail['u_id']

    # Second user created a new channel
    channel_info = channels_create(token_2, 'OwnedBytheresa', True)
    channel_id = channel_info['channel_id']

    with pytest.raises(AccessError):
        channel_removeowner(token_1, channel_id, u_2_id)


def test_channel_removeowner_successfully():
    clear()
    # First user logged in
    auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')
    user_1_detail = auth_login('celine@gmail.com', '123456')
    u_1_id = user_1_detail['u_id']

    # Second user logged in
    auth_register('theresa@gmail.com', '345678', 'Theresa', 'Tao')
    user_2_detail = auth_login('theresa@gmail.com', '345678')
    token_2 = user_2_detail['token']

    # Second user created a new channel
    channel_info = channels_create(token_2, 'OwnedBytheresa', True)
    channel_id = channel_info['channel_id']

    channel_addowner(token_2, channel_id, u_1_id)

    channel_removeowner(token_2, channel_id, u_1_id)

    found = False
    for channel in channels:
        if u_1_id in channel['owner_id']:
            found = True

    assert found == False

# TESTS FOR channel_leave and channel_join


@pytest.fixture
def initialse():
    clear()
    # auth_register('example@email.com', '123456', 'First', 'Last')
    # auth_register('secexample@email.com', '654321', 'FirstTwo', 'LastTwo')

    info_1 = auth_register('example@gmail.com', '123456', 'First', 'Last')
    encoded_jwt_1 = info_1['token']
    info_2 = auth_register('secexample@email.com',
                           '654321', 'FirstTwo', 'LastTwo')
    encoded_jwt_2 = info_2['token']
    channels_create(encoded_jwt_1, 'FirstChannel1', True)
    channels_create(encoded_jwt_1, 'FirstChannel2', False)

    user_id_2 = info_2['u_id']

    return encoded_jwt_1, encoded_jwt_2, user_id_2


def check_channel_join(tokenid, channelid):
    for channel in channels:
        if channel["channel_id"] == channelid:
            memberList = channels[channelid].get("all_mem")
            for member in memberList:
                if member == tokenid:
                    return True
    return False


def check_channel_leave(tokenid, channelid):
    for channel in channels:
        if channel["channel_id"] == channelid:
            memberList = channels[channelid].get("all_mem")
            for member in memberList:
                if member == tokenid:
                    return False
    return True

# =====================CHANNEL LEAVE TESTS=======================


def test_channel_leave_InputError(initialse):
    user_1_token = initialse[0]
    with pytest.raises(InputError):
        channel_leave('NotExist@email.com', 1)
    with pytest.raises(InputError):
        channel_leave('NotExist@email.com', 10)
    with pytest.raises(InputError):
        channel_leave(user_1_token, 3)


def test_channel_leave_AccessError(initialse):
    user_2_token = initialse[1]
    with pytest.raises(AccessError):
        channel_leave(user_2_token, 1)


def test_channel_leave_allowed(initialse):
    user_2_id = initialse[2]
    user_1_token = initialse[0]
    user_2_token = initialse[1]
    channel_invite(user_1_token, 0, user_2_id)
    channel_leave(user_2_token, 0)
    assert check_channel_leave(2, 0) == True

# =====================CHANNEL JOIN TESTS=======================


def test_channel_join_InputError(initialse):
    user_1_token = initialse[0]
    with pytest.raises(InputError):
        channel_join('NotExist@email.com', 1)
    with pytest.raises(InputError):
        channel_join('NotExist@email.com', 10)
    with pytest.raises(InputError):
        channel_join(user_1_token, 3)


def test_channel_join_AccessError(initialse):
    user_1_token = initialse[0]
    user_2_token = initialse[1]
    user_2_id = initialse[2]
    with pytest.raises(AccessError):
        channel_join(user_1_token, 1)

    channel_id = channels_create(user_1_token, 'TestChannel1', True)[
        'channel_id']
    channel_join(user_2_token, channel_id)
    channel_info = channel_details(user_1_token, channel_id)
    print(channel_info)
    assert channel_info['all_members'][1]['u_id'] == user_2_id
    assert len(channel_info['owner_members']) == 1


def test_channel_join_private_AccessError(initialse):
    user_2_token = initialse[1]
    with pytest.raises(AccessError):
        channel_join(user_2_token, 1)


def test_channel_join_allowed(initialse):
    user_1_token = initialse[0]
    user_2_token = initialse[1]
    channel_id = channels_create(user_2_token, 'TestChannel', True)[
        'channel_id']
    channel_join(user_1_token, channel_id)
    assert check_channel_join(1, channel_id) == True
