import pytest
import re
from server import *
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
from error import *
from Global_variables import *

############################# Pytest Fixture #############################


@pytest.fixture
def url():
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")


@pytest.fixture
def register_users(url):
    first_user = {
        'email': 'celine@gmail.com',
        'password': '123456',
        'name_first': 'Celine',
        'name_last': 'Lin',
    }
    user_1_detail_json = requests.post(f'{url}/auth/register', json=first_user)
    user_1_detail = user_1_detail_json.json()

    second_user = {
        'email': 'theresa@gmail.com',
        'password': '123456',
        'name_first': 'Theresa',
        'name_last': 'Tao',
    }
    user_2_detail_json = requests.post(
        f'{url}/auth/register', json=second_user)
    user_2_detail = user_2_detail_json.json()

    third_user = {
        'email': 'peter@gmail.com',
        'password': '123456',
        'name_first': 'Peter',
        'name_last': 'Xie',
    }
    user_3_detail_json = requests.post(
        f'{url}/auth/register', json=third_user)
    user_3_detail = user_3_detail_json.json()

    return user_1_detail, user_2_detail, user_3_detail


@pytest.fixture
def user(url):
    '''
    Registers one user to use for testing
    '''

    user = {
        'email': 'celine@gmail.com',
        'password': '123456',
        'name_first': 'Celine',
        'name_last': 'Lin',
    }
    user_json = requests.post(f'{url}/auth/register', json=user)
    user = user_json.json()
    # Returns token and u_id for one user
    return user

########################## User_profile HTTP Test #############################


def test_user_profile_token_invalid(url, user):
    '''
    Invalid token provided: User logged out or has incorrect token return
    '''

    user_uid = user['u_id']

    # Empty Token (ie user is logged out)
    invalid_token_1 = {
        'token': '',
        'u_id': user_uid
    }
    # Incorrect non-empty token
    invalid_token_2 = {
        'token': 'wrong4token',
        'u_id': user_uid
    }

    # Incorrect input errors will be raised
    response = requests.get(f'{url}/user/profile', params=invalid_token_1)
    assert response.status_code == 400

    response = requests.get(f'{url}/user/profile', params=invalid_token_2)
    assert response.status_code == 400


def test_user_profile_uid_invalid(url, user):
    '''
    Invalid u_id provided: U_id does not exist in database
    '''

    user_token = user['token']

    # Invalid non-empty u_id
    invalid_uid_1 = {
        'token': user_token,
        'u_id': 10
    }

    # Incorrect input errors will be raised
    response = requests.get(f'{url}/user/profile', params=invalid_uid_1)
    assert response.status_code == 400


def test_user_profile_token_uid_valid(url, user):
    '''
    Tests a valid u_id and token input
    '''

    user_token = user['token']
    user_uid = user['u_id']

    # Valid token, first name and last name are inputted
    valid_token_uid = {
        'token': user_token,
        'u_id': user_uid
    }
    # Correct input code raised
    response = requests.get(f'{url}/user/profile', params=valid_token_uid)
    assert response.status_code == 200


########################## User_profile_setname HTTP Test #############################

def test_user_profile_namefirst_not_valid(url, user):
    '''
    Tests invalid first name input to reset name
    '''
    user_token = user['token']

    # First name is empty
    invalid_name_1 = {
        'token': user_token,
        'name_first': '',
        'name_last': 'last'
    }

    # First name has invalid symbols and spaces
    invalid_name_2 = {
        'token': user_token,
        'name_first': '$!d ip',
        'name_last': 'last'
    }

    # First name too long
    invalid_name_3 = {
        'token': user_token,
        'name_first': 'a' * 100,
        'name_last': 'last'
    }

    # Will raise incorrect input errors
    response = requests.put(f'{url}/user/profile/setname', json=invalid_name_1)
    assert response.status_code == 400

    response = requests.put(f'{url}/user/profile/setname', json=invalid_name_2)
    assert response.status_code == 400

    response = requests.put(f'{url}/user/profile/setname', json=invalid_name_3)
    assert response.status_code == 400


def test_user_profile_namelast_not_valid(url, user):
    '''
    Tests invalid last name input to reset name
    '''

    user_token = user['token']
    # Last name is empty
    invalid_name_1 = {
        'token': user_token,
        'name_first': 'first',
        'name_last': ''
    }
    # Last name has invalid symbols and spaces
    invalid_name_2 = {
        'token': user_token,
        'name_first': 'first',
        'name_last': '$!d ip'
    }
    # Last name too long
    invalid_name_3 = {
        'token': user_token,
        'name_first': 'first',
        'name_last': 'a' * 100
    }
    # Will raise incorrect input errors
    response = requests.put(f'{url}/user/profile/setname', json=invalid_name_1)
    assert response.status_code == 400

    response = requests.put(f'{url}/user/profile/setname', json=invalid_name_2)
    assert response.status_code == 400

    response = requests.put(f'{url}/user/profile/setname', json=invalid_name_3)
    assert response.status_code == 400


def test_user_profile_setname_token_invalid(url, user):
    '''
    Invalid token provided: User logged out or has incorrect token return
    '''

    # Empty Token (ie user is logged out)
    invalid_token_1 = {
        'token': '',
        'name_first': 'first',
        'name_last': 'last'
    }
    # Incorrect non-empty token
    invalid_token_2 = {
        'token': 'wrong4token',
        'name_first': 'first',
        'name_last': 'last'
    }
    # Incorrect input errors will be raised
    response = requests.put(
        f'{url}/user/profile/setname', json=invalid_token_1)
    assert response.status_code == 400

    response = requests.put(
        f'{url}/user/profile/setname', json=invalid_token_2)
    assert response.status_code == 400


def test_user_profile_name_valid(url, user):
    '''
    Test valid name and token input
    '''

    user_token = user['token']

    # Valid token, first name and last name are inputted
    valid_name = {
        'token': user_token,
        'name_first': 'first',
        'name_last': 'last'
    }
    # Correct input code raised
    response = requests.put(f'{url}/user/profile/setname', json=valid_name)
    assert response.status_code == 200


####################### User Profile Set Email Tests ######################
def test_user_profile_setemail_not_valid(url, register_users):
    '''
    Test if email not valid
    '''
    user_1_detail = register_users[0]
    user_1_token = user_1_detail['token']

    invalid_email_1 = {
        'token': user_1_token,
        'email': ''
    }

    invalid_email_2 = {
        'token': user_1_token,
        'email': 'invalidemail.com'
    }

    invalid_email_3 = {
        'token': user_1_token,
        'email': '1'
    }

    response = requests.put(
        f'{url}/user/profile/setemail', json=invalid_email_1)
    assert response.status_code == 400

    response = requests.put(
        f'{url}/user/profile/setemail', json=invalid_email_2)
    assert response.status_code == 400

    response = requests.put(
        f'{url}/user/profile/setemail', json=invalid_email_3)
    assert response.status_code == 400


def test_user_profile_setemail_already_used(url, register_users):
    '''
    Test if email already in use
    '''
    user_1_detail = register_users[0]
    user_1_token = user_1_detail['token']

    invalid_email_1 = {
        'token': user_1_token,
        'email': 'celine@gmail.com'
    }

    invalid_email_2 = {
        'token': user_1_token,
        'email': 'theresa@gmail.com'
    }

    response = requests.put(
        f'{url}/user/profile/setemail', json=invalid_email_1)
    assert response.status_code == 400

    response = requests.put(
        f'{url}/user/profile/setemail', json=invalid_email_2)
    assert response.status_code == 400


def test_user_profile_setemail_valid(url, register_users):
    '''
    Test for valid change email
    '''
    user_1_detail = register_users[0]
    user_1_token = user_1_detail['token']

    user_2_detail = register_users[1]
    user_2_token = user_2_detail['token']

    new_email = {
        'token': user_1_token,
        'email': 'thirdexample@gmail.com'
    }

    response = requests.put(f'{url}/user/profile/setemail', json=new_email)
    assert response.status_code == 200

    # Testing if second user tries to change email to the one that the first user just changed to.

    invalid_email = {
        'token': user_2_token,
        'email': 'thirdexample@gmail.com'
    }

    response = requests.put(f'{url}/user/profile/setemail', json=invalid_email)
    assert response.status_code == 400

####################### User Profile Set Handle Tests ######################


def test_user_profile_sethandle_handle_length_InputError(url, register_users):
    '''
    Test handle length error
    '''
    user_1_detail = register_users[0]
    user_1_token = user_1_detail['token']

    invalid_handle_1 = {
        'token': user_1_token,
        'handle_str': 'Am'
    }

    invalid_handle_2 = {
        'token': user_1_token,
        'handle_str': ''
    }

    invalid_handle_3 = {
        'token': user_1_token,
        'handle_str': 'ThisIsAnExampleHandleOver20'
    }

    invalid_handle_4 = {
        'token': user_1_token,
        'handle_str': '    The Handle Will Go        Over 20 Like This    '
    }

    response = requests.put(
        f'{url}/user/profile/sethandle', json=invalid_handle_1)
    assert response.status_code == 400

    response = requests.put(
        f'{url}/user/profile/sethandle', json=invalid_handle_2)
    assert response.status_code == 400

    response = requests.put(
        f'{url}/user/profile/sethandle', json=invalid_handle_3)
    assert response.status_code == 400

    response = requests.put(
        f'{url}/user/profile/sethandle', json=invalid_handle_4)
    assert response.status_code == 400


def test_user_profile_sethandle_already_in_use(url, register_users):
    '''
    Test handle already in use
    '''
    user_1_detail = register_users[0]
    user_1_token = user_1_detail['token']

    user_2_detail = register_users[1]
    user_2_token = user_2_detail['token']

    new_handle = {
        'token': user_1_token,
        'handle_str': 'Name1'
    }

    response = requests.put(f'{url}/user/profile/sethandle', json=new_handle)

    invalid_handle_1 = {
        'token': user_1_token,
        'handle_str': 'Name1'
    }

    invalid_handle_2 = {
        'token': user_2_token,
        'handle_str': 'Name1'
    }

    response = requests.put(
        f'{url}/user/profile/sethandle', json=invalid_handle_1)
    assert response.status_code == 400

    response = requests.put(
        f'{url}/user/profile/sethandle', json=invalid_handle_2)
    assert response.status_code == 400


def test_user_profile_sethandle_not_alphanum(url, register_users):
    '''
    Test handle not alphanum
    '''
    user_1_detail = register_users[0]
    user_1_token = user_1_detail['token']

    invalid_handle_1 = {
        'token': user_1_token,
        'handle_str': 'Not alpha %$'
    }

    invalid_handle_2 = {
        'token': user_1_token,
        'handle_str': 'Nota|pha%$'
    }

    invalid_handle_3 = {
        'token': user_1_token,
        'handle_str': '-%@#%'
    }

    invalid_handle_4 = {
        'token': user_1_token,
        'handle_str': '|'
    }

    response = requests.put(
        f'{url}/user/profile/sethandle', json=invalid_handle_1)
    assert response.status_code == 400

    response = requests.put(
        f'{url}/user/profile/sethandle', json=invalid_handle_2)
    assert response.status_code == 400

    response = requests.put(
        f'{url}/user/profile/sethandle', json=invalid_handle_3)
    assert response.status_code == 400

    response = requests.put(
        f'{url}/user/profile/sethandle', json=invalid_handle_4)
    assert response.status_code == 400


def test_user_profile_sethandle_valid(url, register_users):
    '''
    Test handle change valid
    '''
    user_1_detail = register_users[0]
    user_1_token = user_1_detail['token']

    user_2_detail = register_users[1]
    user_2_token = user_2_detail['token']

    new_handle_1 = {
        'token': user_1_token,
        'handle_str': 'NewName'
    }

    new_handle_2 = {
        'token': user_2_token,
        'handle_str': '  Han  Dle  '
    }

    response = requests.put(f'{url}/user/profile/sethandle', json=new_handle_1)
    assert response.status_code == 200

    response = requests.put(f'{url}/user/profile/sethandle', json=new_handle_2)
    assert response.status_code == 200

####################### User Profile Upload Photo Tests ######################


def test_uploadphoto_not_valid_token(url, register_users):
    '''
    Test photo not valid token
    '''

    invalid_photo = {
        'token': None,
        'img_url': 'www.test.com',
        'x_start': 0,
        'x_end': 0,
        'y_start': 0,
        'y_end': 0
    }

    response = requests.post(
        f'{url}/user/profile/uploadphoto', json=invalid_photo)
    assert response.status_code == 400


def test_uploadphoto_img_url_http_error(url, register_users):
    '''
    Test img_url http error
    '''
    user_1_detail = register_users[0]
    user_1_token = user_1_detail['token']

    img_url = 'https://upload.wikimedia.org/wikipedia/commons/1/1b/Square_200x200'

    invalid_photo = {
        'token': user_1_token,
        'img_url': img_url,
        'x_start': 0,
        'x_end': 0,
        'y_start': 0,
        'y_end': 0
    }

    response = requests.post(
        f'{url}/user/profile/uploadphoto', json=invalid_photo)
    assert response.status_code == 400


def test_uploadphoto_dimensions_out_of_bounds(url, register_users):
    '''
    Test Photo dimensions out of bounds
    '''
    user_1_detail = register_users[0]
    user_1_token = user_1_detail['token']

    img_url = 'https://processing.org/tutorials/pixels/imgs/tint1.jpg'

    invalid_photo_1 = {
        'token': user_1_token,
        'img_url': img_url,
        'x_start': -50,
        'x_end': 50,
        'y_start': 25,
        'y_end': 100
    }

    invalid_photo_2 = {
        'token': user_1_token,
        'img_url': img_url,
        'x_start': 0,
        'x_end': 300,
        'y_start': 25,
        'y_end': 100
    }

    invalid_photo_3 = {
        'token': user_1_token,
        'img_url': img_url,
        'x_start': 0,
        'x_end': 150,
        'y_start': -40,
        'y_end': 100
    }

    invalid_photo_4 = {
        'token': user_1_token,
        'img_url': img_url,
        'x_start': 50,
        'x_end': 200,
        'y_start': 30,
        'y_end': -5
    }

    invalid_photo_5 = {
        'token': user_1_token,
        'img_url': img_url,
        'x_start': 200,
        'x_end': 200,
        'y_start': 0,
        'y_end': 200
    }

    invalid_photo_6 = {
        'token': user_1_token,
        'img_url': img_url,
        'x_start': 500,
        'x_end': 100,
        'y_start': 50,
        'y_end': 60
    }

    invalid_photo_7 = {
        'token': user_1_token,
        'img_url': img_url,
        'x_start': 50,
        'x_end': 50,
        'y_start': 45,
        'y_end': 50
    }

    invalid_photo_8 = {
        'token': user_1_token,
        'img_url': img_url,
        'x_start': 0,
        'x_end': 0,
        'y_start': 0,
        'y_end': 0
    }

    response = requests.post(
        f'{url}/user/profile/uploadphoto', json=invalid_photo_1)
    assert response.status_code == 400

    response = requests.post(
        f'{url}/user/profile/uploadphoto', json=invalid_photo_2)
    assert response.status_code == 400

    response = requests.post(
        f'{url}/user/profile/uploadphoto', json=invalid_photo_3)
    assert response.status_code == 400

    response = requests.post(
        f'{url}/user/profile/uploadphoto', json=invalid_photo_4)
    assert response.status_code == 400

    response = requests.post(
        f'{url}/user/profile/uploadphoto', json=invalid_photo_5)
    assert response.status_code == 400

    response = requests.post(
        f'{url}/user/profile/uploadphoto', json=invalid_photo_6)
    assert response.status_code == 400

    response = requests.post(
        f'{url}/user/profile/uploadphoto', json=invalid_photo_7)
    assert response.status_code == 400

    response = requests.post(
        f'{url}/user/profile/uploadphoto', json=invalid_photo_8)
    assert response.status_code == 400


def test_uploadphoto_not_jpg(url, register_users):
    '''
    Test photo not jpg
    '''
    user_1_detail = register_users[0]
    user_1_token = user_1_detail['token']

    img_url_1 = 'https://upload.wikimedia.org/wikipedia/commons/1/1b/Square_200x200.png'
    img_url_2 = 'https://www.verdict.co.uk/wp-content/uploads/2017/09/giphy-downsized-large.gif'
    img_url_3 = 'https://webcms3.cse.unsw.edu.au/'

    invalid_photo_1 = {
        'token': user_1_token,
        'img_url': img_url_1,
        'x_start': 0,
        'x_end': 0,
        'y_start': 0,
        'y_end': 0
    }

    invalid_photo_2 = {
        'token': user_1_token,
        'img_url': img_url_2,
        'x_start': 0,
        'x_end': 0,
        'y_start': 0,
        'y_end': 0
    }

    invalid_photo_3 = {
        'token': user_1_token,
        'img_url': img_url_3,
        'x_start': 0,
        'x_end': 0,
        'y_start': 0,
        'y_end': 0
    }

    response = requests.post(
        f'{url}/user/profile/uploadphoto', json=invalid_photo_3)
    assert response.status_code == 400

    response = requests.post(
        f'{url}/user/profile/uploadphoto', json=invalid_photo_2)
    assert response.status_code == 400

    response = requests.post(
        f'{url}/user/profile/uploadphoto', json=invalid_photo_1)
    assert response.status_code == 400


def test_uploadphoto_valid(url, register_users):
    '''
    Test valid photo upload
    '''
    user_1_detail = register_users[0]
    user_1_token = user_1_detail['token']

    img_url = 'https://processing.org/tutorials/pixels/imgs/tint1.jpg'

    valid_photo_1 = {
        'token': user_1_token,
        'img_url': img_url,
        'x_start': 0,
        'x_end': 10,
        'y_start': 20,
        'y_end': 30,
    }

    valid_photo_2 = {
        'token': user_1_token,
        'img_url': img_url,
        'x_start': 50,
        'x_end': 150,
        'y_start': 150,
        'y_end': 200
    }

    valid_photo_3 = {
        'token': user_1_token,
        'img_url': img_url,
        'x_start': 10,
        'x_end': 50,
        'y_start': 50,
        'y_end': 150
    }

    valid_photo_4 = {
        'token': user_1_token,
        'img_url': img_url,
        'x_start': 10,
        'x_end': 50,
        'y_start': 17,
        'y_end': 40
    }

    response = requests.post(
        f'{url}/user/profile/uploadphoto', json=valid_photo_1)
    assert response.status_code == 200

    response = requests.post(
        f'{url}/user/profile/uploadphoto', json=valid_photo_2)
    assert response.status_code == 200

    response = requests.post(
        f'{url}/user/profile/uploadphoto', json=valid_photo_3)
    assert response.status_code == 200

    response = requests.post(
        f'{url}/user/profile/uploadphoto', json=valid_photo_4)
    assert response.status_code == 200
