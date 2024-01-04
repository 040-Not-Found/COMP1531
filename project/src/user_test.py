'''
File tests functions which manipulate the user profile
'''

import pytest
from error import InputError, AccessError
from other import clear
from Global_variables import *
from auth import *
from user import *

########################## Pytest Fixture #############################


@pytest.fixture
def two_users():
    '''
    Registers two users for testing
    '''
    clear()
    user_1 = auth_register('example@gmail.com',
                           'password123', 'Julian', 'Caesar')
    user_2 = auth_register('simple@gmail.com', 'bunny4252', 'Bunny', 'Rabbit')
    # Return the two users token and u_id
    return user_1, user_2


@pytest.fixture
def user():
    '''
    Registers one user for testing
    '''
    clear()
    # Return one user's token and u_id
    return auth_register('celine@gmail.com', '123456', 'Celine', 'Lin')


@pytest.fixture
def reg_usrs():
    ''' registering users for setemail & sethandle with pytest.fixtures '''
    clear()
    user_1 = auth_register('example@email.com', '123456', 'First', 'Last')
    token_1 = user_1['token']
    user_2 = auth_register('secexample@email.com',
                           '654321', 'FirstTwo', 'LastTwo')
    token_2 = user_2['token']
    return token_1, token_2


def test_not_valid_email(reg_usrs):
    ''' Non valid emails input '''
    token_1 = reg_usrs[0]
    with pytest.raises(InputError):
        user_profile_setemail(token_1, '')
    with pytest.raises(InputError):
        user_profile_setemail(token_1, 'invalidemail.com')
    with pytest.raises(InputError):
        user_profile_setemail(token_1, '1')
    with pytest.raises(AccessError):
        user_profile_setemail(None, '1')


def test_email_already_used(reg_usrs):
    ''' Email already in use '''
    token_1 = reg_usrs[0]
    with pytest.raises(InputError):
        user_profile_setemail(token_1, 'example@email.com')
    with pytest.raises(InputError):
        user_profile_setemail(token_1, 'secexample@email.com')


def test_email_change(reg_usrs):
    ''' TEST Change the email of a user '''
    token_1 = reg_usrs[0]
    user_profile_setemail(token_1, 'thirdexample@email.com')
    user1 = user_profile(token_1, 0)
    print(user1)

    assert user1['user']['email'] == 'thirdexample@email.com'


def test_handle_length_InputError(reg_usrs):
    ''' Non valid handle input '''
    token_1 = reg_usrs[0]
    with pytest.raises(InputError):
        user_profile_sethandle(token_1, 'Am')
    with pytest.raises(InputError):
        user_profile_sethandle(token_1, 'ThisIsAnExampleHandleOver20')
    with pytest.raises(InputError):
        user_profile_sethandle(
            token_1, '    The Handle Will Go        Over 20 Like This    ')


def test_handle_used_already(reg_usrs):
    ''' Handle already in use '''
    token_1 = reg_usrs[0]
    token_2 = reg_usrs[1]
    user_profile_sethandle(token_1, 'Name1')
    with pytest.raises(InputError):
        user_profile_sethandle(token_1, 'Name1')
    with pytest.raises(InputError):
        user_profile_sethandle(token_2, 'Name1')
    with pytest.raises(AccessError):
        user_profile_sethandle("", 'Name2')


def test_handle_not_alphanum(reg_usrs):
    ''' Handle is not alphanum '''
    token_1 = reg_usrs[0]
    with pytest.raises(InputError):
        user_profile_sethandle(token_1, 'Not alpha %$')
    with pytest.raises(InputError):
        user_profile_sethandle(token_1, 'Nota|pha%$')
    with pytest.raises(InputError):
        user_profile_sethandle(token_1, '-%@#%')
    with pytest.raises(InputError):
        user_profile_sethandle(token_1, '|')


def test_handle_change(reg_usrs):
    '''TEST Change the handle of a user'''
    token_1 = reg_usrs[0]
    token_2 = reg_usrs[1]
    user_profile_sethandle(token_1, 'NewName')

    user_profile_sethandle(token_2, '  Han  Dle  ')
    user1 = user_profile(token_1, 0)

    user2 = user_profile(token_2, 1)

    assert user1['user']['handle_str'] == 'NewName'
    assert user2['user']['handle_str'] == 'Han  Dle'

########################## User Profile Tests #############################


def test_valid_uid_and_token(two_users):
    '''
    Test function for user_profile:
    '''
    user_1, user_2 = two_users
    # Assert the return of the function is correct
    assert user_profile(user_1['token'], user_2['u_id']) == {'user': {'u_id': user_2['u_id'],
                                                                      'email': 'simple@gmail.com',
                                                                      'name_first': 'Bunny',
                                                                      'name_last': 'Rabbit',
                                                                      'handle_str': 'BunnyRabbit',
                                                                      'profile_img_url': ""
                                                                      }}


def test_invalid_uid(user):
    '''
    Test function for user_profile: Tests for a valid token but invalid user id
    '''
    with pytest.raises(InputError):
        user_profile(user['token'], 5)


def test_invalid_token_user_profile(user):
    '''
    Test function for user_profile: Tests for a valid user id but invalid token
    '''
    # Empty token
    with pytest.raises(AccessError):
        user_profile('', user['u_id'])
    # Invalid token
    with pytest.raises(AccessError):
        user_profile('wrongtoken', user['u_id'])


def test_invalid_token_setname(user):
    '''
    User Profile Setname Test: Tests when the user token is invalid (ie logged out)
    '''
    # Invalid token but valid name raises error
    with pytest.raises(AccessError):
        user_profile_setname('', 'Jane', 'Wong')


########################## User Profile Setname Tests #############################

def test_valid_name(user):
    '''
    User Profile Setname Test: Set the user's name into new valid name
    '''
    token = user['token']
    u_id = user['u_id']
    # Set user's new name to Jane Wong
    user_profile_setname(token, 'Jane', 'Wong')
    user = user_profile(token, u_id)
    # Checking the first and last name are correct after running setname function
    assert user['user']['name_first'] == 'Jane'
    assert user['user']['name_last'] == 'Wong'


def test_invalid_firstname(user):
    '''
    User Profile Setname Test: Testing for incorrect format of first names but valid last name
    '''
    token = user['token']
    # Empty first name
    with pytest.raises(InputError):
        user_profile_setname(token, '', 'Wong')
    # First name over 50 characters long
    with pytest.raises(InputError):
        user_profile_setname(token, 'a'*100, 'Wong')


def test_invalid_lastname(user):
    '''
    User Profile Setname Test: Testing for incorrect format of last names but valid first name
    '''
    token = user['token']
    # Empty last name
    with pytest.raises(InputError):
        user_profile_setname(token, 'Jane', '')
    # Last name over 50 characters
    with pytest.raises(InputError):
        user_profile_setname(token, 'Jane', 'a'*100)


def test_empty_name(user):
    '''
    User Profile Setname Test: Testing for empty name
    '''
    token = user['token']
    with pytest.raises(InputError):
        user_profile_setname(token, '', '')

########################## User Profile Upload Photo Tests #############################


def test_uploadphoto_not_valid_token():
    '''
    Testing for non valid token
    '''
    with pytest.raises(AccessError):
        user_profile_uploadphoto(None, 'www.test.com', 0, 0, 0, 0)


def test_uploadphoto_img_url_http_error(user):
    '''
    Testing for image url http error
    '''
    # img_url contains a link to the same url used in dimensions_out_of_bounds but without the .png
    img_url = 'https://upload.wikimedia.org/wikipedia/commons/1/1b/Square_200x200'
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 0, 0, 0, 0)


def test_uploadphoto_dimensions_out_of_bounds(user):
    '''
    Testing for image dimensions out of bounds for x_start, x_end, y_start and y_end
    '''
    # Working with an image of 200 x 200 pixels
    img_url = 'https://processing.org/tutorials/pixels/imgs/tint1.jpg'
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, -50, 50, 25, 100)
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 0, 300, 25, 100)
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 0, 150, -40, 100)
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 50, 200, 30, -5)
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 0, 0, 0, 0)
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 0, 200, 0, 200)
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 50, 100, 50, 60)
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 0, 50, 45, 50)


def test_uploadphoto_not_jpg(user):
    '''
    Testing for if the image link is not a JPG
    '''
    img_url_1 = 'https://upload.wikimedia.org/wikipedia/commons/1/1b/Square_200x200.png'
    img_url_2 = 'https://www.verdict.co.uk/wp-content/uploads/2017/09/giphy-downsized-large.gif'
    img_url_3 = 'https://webcms3.cse.unsw.edu.au/'

    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], img_url_3, 0, 0, 0, 0)
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], img_url_2, 0, 0, 0, 0)
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], img_url_1, 0, 0, 0, 0)


def test_uploadphoto_out_of_bound(user):
    img_url = 'https://processing.org/tutorials/pixels/imgs/tint1.jpg'
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 100000, 0, 0, 0)


def test_uploadphoto_valid(user):
    '''
    Testing for a user uploading a new photo successfully
    '''
    img_url = 'https://processing.org/tutorials/pixels/imgs/tint1.jpg'
    # Image is 200 x 200 pixels

    '''assert valid_img_check(user_profile_uploadphoto(
        user['token'], img_url, 0, 0, 100, 200))

    assert valid_img_check(user_profile_uploadphoto(
        user['token'], img_url, 50, 150, 150, 150))

    assert valid_img_check(user_profile_uploadphoto(
        user['token'], img_url, 100, 50, 50, 150))

    assert valid_img_check(user_profile_uploadphoto(
        user['token'], img_url, 100, 50, 175, 40))'''

    assert user_profile_uploadphoto(
        user['token'], img_url, 20, 50, 75, 180) == {}
    assert requests.get(img_url).status_code == 200
    '''assert user_profile_uploadphoto(
        user['token'], img_url, 0, 0, 100, 200) == {}
    assert user_profile_uploadphoto(
        user['token'], img_url, 50, 150, 150, 150) == {}
    assert user_profile_uploadphoto(
        user['token'], img_url, 100, 50, 50, 150) == {}
    assert user_profile_uploadphoto(
        user['token'], img_url, 100, 50, 175, 40) == {}'''


'''def valid_img_check(uploadphoto):
    
    Validating img check
    
    if uploadphoto != {}:
        raise Exception('Image upload not valid')
    return True'''
