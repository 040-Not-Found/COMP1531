import pytest
import re
from auth import *
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
from error import *
from Global_variables import *
from other import *

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
    '''
    Registers two user to use for testing
    '''
    clear()
    first_user = {
        'email': 'vickyhu010@gmail.com',
        'password': '123456',
        'name_first': 'Vicky',
        'name_last': 'Hu'
    }
    user_1_detail_json = requests.post(f'{url}/auth/register', json=first_user)
    user_1_detail = user_1_detail_json.json()

    second_user = {
        'email': 'theresa@gmail.com',
        'password': '38739201',
        'name_first': 'Theresa',
        'name_last': 'Tao'
    }
    user_2_detail_json = requests.post(
        f'{url}/auth/register', json=second_user)
    user_2_detail = user_2_detail_json.json()
    print(f"fixture:{users_detail}")
    return user_1_detail, first_user, user_2_detail, second_user


#############################Auth_login#############################

# Test for valid logins
def test_valid_auth_login(url, register_users):
    '''
    Valid email and password input
    '''

    user_email = register_users[1]['email']
    user_password = register_users[1]['password']

    # Valid token, first name and last name are inputted
    valid_login = {
        'email': user_email,
        'password': user_password
    }
    # Correct input code raised
    response = requests.post(f'{url}/auth/login', json=valid_login)
    assert response.status_code == 200


def test_invalid_email_login(url, register_users):
    '''
    Invalid email and valid password
    '''
    # Setting user details to variables that we need to test

    user_1_password = register_users[1]['password']
    user_2_email = register_users[3]['email']

    # Incorrect email format
    invalid_login_1 = {
        'email': 'email',
        'password': user_1_password
    }

    # Email and password does not link to same account
    invalid_login_2 = {
        'email': user_2_email,
        'password': user_1_password
    }

    # Empty email
    invalid_login_3 = {
        'email': '',
        'password': user_1_password
    }
    # Incorrect input code raised
    response = requests.post(f'{url}/auth/login', json=invalid_login_1)
    assert response.status_code == 400

    response = requests.post(f'{url}/auth/login', json=invalid_login_2)
    assert response.status_code == 400

    response = requests.post(f'{url}/auth/login', json=invalid_login_3)
    assert response.status_code == 400


def test_invalid_pw_login(url, register_users):
    '''
    Invalid password and valid email
    '''
    # Setting user details to variables that we need to test
    user_1_email = register_users[1]['email']

    # Incorrect password
    invalid_login_1 = {
        'email': user_1_email,
        'password': 'incorrect'
    }
    # Empty password
    invalid_login_2 = {
        'email': user_1_email,
        'password': ''
    }
    # Incorrect input code raised
    response = requests.post(f'{url}/auth/login', json=invalid_login_1)
    assert response.status_code == 400

    response = requests.post(f'{url}/auth/login', json=invalid_login_2)
    assert response.status_code == 400


def test_invalid_emailpw_login(url, register_users):
    '''
    Invalid password and invalid email
    '''
    # Both email and password are unregistered
    invalid_login = {
        'email': 'first@gmail.com',
        'password': 'pass1234'
    }

    # Both email and password are empty
    invalid_login_1 = {
        'email': '',
        'password': ''
    }

    # Incorrect input code raised
    response = requests.post(f'{url}/auth/login', json=invalid_login)
    assert response.status_code == 400

    response = requests.post(f'{url}/auth/login', json=invalid_login_1)
    assert response.status_code == 400


#############################Auth_logout#############################

def test_logout(url, register_users):
    '''
    Tests correct and incorrect logout flask functions
    '''
    # Setting user details to variables that we need to test

    user_1_token = register_users[0]['token']

    # Valid token for logout
    valid_logout = {
        'token': user_1_token
    }

    # Valid logout should return correct code
    response = requests.post(f'{url}/auth/logout', json=valid_logout)
    assert response.status_code == 200

    # Already logged out token, ie token is None
    invalid_logout_1 = {
        'token': ''
    }

    # Invalid 'token'
    invalid_logout_2 = {
        'token': 'Invalid_token'
    }

    # Incorrect input code raised
    response = requests.post(f'{url}/auth/logout', json=invalid_logout_1)
    assert response.status_code == 200

    response = requests.post(f'{url}/auth/logout', json=invalid_logout_2)
    assert response.status_code == 200


#############################Auth_register#############################

def test_valid_auth_register(url):
    '''
    Testing Auth Register: Valid register of details
    '''
    # Standard input values
    valid_register_1 = {
        'email': 'example@email.com',
        'password': '134567',
        'name_first': 'Example',
        'name_last': 'Name'
    }
    # Maximum length name
    valid_register_2 = {
        'email': 'example1@email.com',
        'password': '134567',
        'name_first': 'a'*50,
        'name_last': 'a'*50
    }
    # Unique long password register
    valid_register_3 = {
        'email': 'example2@email.com',
        'password': '137%password3678.xXDFG',
        'name_first': 'Example',
        'name_last': 'Name'
    }
    # Valid register should return correct code
    response = requests.post(f'{url}/auth/register', json=valid_register_1)
    assert response.status_code == 200

    response = requests.post(f'{url}/auth/register', json=valid_register_2)
    assert response.status_code == 200

    response = requests.post(f'{url}/auth/register', json=valid_register_3)
    assert response.status_code == 200


def test_invalid_email_register(url, register_users):

    user_email = register_users[1]['email']
    user_password = register_users[1]['password']
    user_firstname = register_users[1]['name_first']
    user_lastname = register_users[1]['name_last']

    # Invalid email
    invalid_register_1 = {
        'email': 'exampleemailcom',
        'password': '134567',
        'name_first': 'Example',
        'name_last': 'Name'
    }
    # Empty email
    invalid_register_2 = {
        'email': '',
        'password': '134567',
        'name_first': 'Example',
        'name_last': 'Name'
    }
    # Already registered email
    invalid_register_3 = {
        'email': user_email,
        'password': user_password,
        'name_first': user_firstname,
        'name_last': user_lastname
    }
    # Invalid register should return input error code
    response = requests.post(f'{url}/auth/register', json=invalid_register_1)
    assert response.status_code == 400

    response = requests.post(f'{url}/auth/register', json=invalid_register_2)
    assert response.status_code == 400

    response = requests.post(f'{url}/auth/register', json=invalid_register_3)
    assert response.status_code == 400


def test_invalid_password_register(url):

    # Short Password
    invalid_register_1 = {
        'email': 'example@email.com',
        'password': '123',
        'name_first': 'Example',
        'name_last': 'Name'
    }
    # Empty password
    invalid_register_2 = {
        'email': 'example@email.com',
        'password': '',
        'name_first': 'Example',
        'name_last': 'Name'
    }

    # Invalid register should return input error code
    response = requests.post(f'{url}/auth/register', json=invalid_register_1)
    assert response.status_code == 400

    response = requests.post(f'{url}/auth/register', json=invalid_register_2)
    assert response.status_code == 400


def test_invalid_name_register(url):

    # Name > 50 character
    invalid_register_1 = {
        'email': 'example1@email.com',
        'password': '123',
        'name_first': 'a'*100,
        'name_last': 'Name'
    }
    # Empty first name
    invalid_register_2 = {
        'email': 'example2@email.com',
        'password': '123',
        'name_first': '',
        'name_last': 'Name'
    }
    # Last name > 50 characters
    invalid_register_3 = {
        'email': 'example3@email.com',
        'password': '123',
        'name_first': 'Example',
        'name_last': 'a'*100
    }
    # Empty last name
    invalid_register_4 = {
        'email': 'example4@email.com',
        'password': '123',
        'name_first': 'Example',
        'name_last': ''
    }
    # Empty first and last name
    invalid_register_5 = {
        'email': 'example5@email.com',
        'password': '123',
        'name_first': '',
        'name_last': ''
    }
    # Invalid name format
    invalid_register_6 = {
        'email': 'example6@email.com',
        'password': '123',
        'name_first': '%Dais y',
        'name_last': 'Wa n#'
    }
    # Invalid register should return input error code
    response = requests.post(f'{url}/auth/register', json=invalid_register_1)
    assert response.status_code == 400

    response = requests.post(f'{url}/auth/register', json=invalid_register_2)
    # Invalid register should return input error code
    assert response.status_code == 400

    response = requests.post(f'{url}/auth/register', json=invalid_register_3)
    assert response.status_code == 400

    response = requests.post(f'{url}/auth/register', json=invalid_register_4)
    # Invalid register should return input error code
    assert response.status_code == 400

    response = requests.post(f'{url}/auth/register', json=invalid_register_5)
    assert response.status_code == 400

    response = requests.post(f'{url}/auth/register', json=invalid_register_6)
    assert response.status_code == 400


############################# Auth_Passwordreset_Request #############################
def test_request_valid_email(url, register_users):
    token = register_users[0]['token']
    u_id = register_users[0]['u_id']

    response = requests.get(f"{url}/user/profile",
                            params={'token': token, 'u_id': u_id})
    assert response.status_code == 200
    user_email = response.json()['user']['email']

    valid_email = {
        'email': user_email,
    }

    response = requests.post(
        f'{url}/auth/passwordreset/request', json=valid_email)
    assert response.status_code == 200


def test_request_unregistered_email(url):
    invalid_email = {
        'email': 'hello@gmail.com'
    }

    response = requests.post(
        f'{url}/auth/passwordreset/request', json=invalid_email)
    assert response.status_code == 400


def test_request_empty_email(url):
    invalid_email = {
        'email': ' '
    }

    response = requests.post(
        f'{url}/auth/passwordreset/request', json=invalid_email)
    assert response.status_code == 400

############################# Auth_Passwordreset_Reset #############################


def test_correct_reset(url, register_users):

    token = register_users[0]['token']
    u_id = register_users[0]['u_id']

    response = requests.get(f"{url}/user/profile",
                            params={'token': token, 'u_id': u_id})
    assert response.status_code == 200
    user_email = response.json()['user']['email']

    valid_email = {
        'email': user_email,
    }

    response = requests.post(
        f'{url}/auth/passwordreset/request', json=valid_email)
    assert response.status_code == 200

    invalid_code = {
        'reset_code': '1000000',
        'new_password': 'helloworld'
    }
    response = requests.post(
        f'{url}/auth/passwordreset/reset', json=invalid_code)
    assert response.status_code == 400


'''def test_incorrect_code(url, register_users):
    # Empty verification code
    invalid_code1 = {
        'verification_code': ' ',
        'new_password': 'helloworld'
    }
    response = requests.post(
        f'{url}/auth/passwordreset/reset', json=invalid_code1)
    assert response.status_code == 400

    # Incorrect input digits
    invalid_code2 = {
        'verification_code': '12345',
        'new_password': 'helloworld'
    }
    response = requests.post(
        f'{url}/auth/passwordreset/reset', json=invalid_code2)
    assert response.status_code == 400

    # Correct code with random trailing values
    invalid_code3 = {
        'verification_code': (str(password_user) + 'wrong', 'helloworld'),
        'new_password': 'helloworld'
    }

    response = requests.post(
        f'{url}/auth/passwordreset/reset', json=invalid_code3)
    assert response.status_code == 400


def test_invalid_password(url, register_users):
    user = {
        'email': 'vickyhu010@gmail.com',
        'password': '123456',
        'name_first': 'Vicky',
        'name_last': 'Hu'
    }
    user_detail_json = requests.post(f'{url}/auth/register', json=user)
    user_detail = user_detail_json.json()
    assert user_detail_json.status_code == 200
    print(users_detail)
    code = auth_passwordreset_request('vickyhu010@gmail.com')

    email = {
        'email': 'vickyhu010@gmail.com'
    }
    code_json = requests.post(f'{url}/auth/passwordreset/request', json=email)
    code = code_json.json()

    # Empty password input
    invalid_code1 = {
        'verification_code': "1000000",
        'new_password': ' '
    }
    response = requests.post(
        f'{url}/auth/passwordreset/reset', json=invalid_code1)
    assert response.status_code == 400
    # New password is less than 6 characters
    invalid_code2 = {
        'verification_code': "1000000",
        'new_password': '123'
    }
    response = requests.post(
        f'{url}/auth/passwordreset/reset', json=invalid_code2)
    assert response.status_code == 400'''
