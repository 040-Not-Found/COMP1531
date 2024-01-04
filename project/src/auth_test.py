'''
This test file tests all the authorisation functions (auth_login, auth_logout, auth_register)
'''
import pytest
from Global_variables import *
from auth import auth_login, auth_logout, auth_register, SECRET, auth_passwordreset_request, auth_passwordreset_reset
from error import InputError, AccessError
from other import clear
import jwt
from user import user_profile
from helper import *

############################# Pytest Fixture ###########################

@pytest.fixture
def register_user():
    '''
    Registers one user for login, logout and registering tests
    '''
    clear()
    user_1 = auth_register('vickyhu010@gmail.com', 'password123', 'Julian', 'Caesar')
    return user_1

@pytest.fixture
def password_user():
    '''
    Registers one user for password reset and request tests
    '''
    clear()
    auth_register('vickyhu010@gmail.com', 'password123', 'Julian', 'Caesar')
    auth_passwordreset_request('vickyhu010@gmail.com')
    code = get_user_data('user_email', 'vickyhu010@gmail.com', 'verification_code')
    return code
############################# Auth_login #############################

# Test for valid logins
def test_valid_auth_login(register_user):
    '''
    Testing login: Tests the successful logging in of one user
    '''
    user_1 = register_user
    user_1_token = user_1['token']
    assert auth_login('vickyhu010@gmail.com', 'password123') == {'u_id': 0, 'token': user_1_token}

def test_invalid_email_login(register_user):
    '''
    Testing login: Tests invalid email formats for logging into an account
    '''
    with pytest.raises(AccessError):
        #Empty email
        auth_login('', 'bunny4252') 
    with pytest.raises(AccessError):
        #Invalid email
        auth_login('words', 'bunny4252') 
    with pytest.raises(AccessError):
        #Another registered email
        auth_login('vickyhu010@gmail.com', 'bunny4252') 

def test_invalid_pw_login(register_user):
    '''
    Testing login: Tests incorrect password inputs
    '''

    with pytest.raises(AccessError):
        # Empty password
        auth_login('vickyhu010@gmail.com', '')

    with pytest.raises(AccessError):
        # Incorrect password
        auth_login('vickyhu010@gmail.com', 'wrongpw')


def test_invalid_emailpw_login(register_user):
    '''
    Testing login: Tests incorrect password and email combinations
    '''

    with pytest.raises(AccessError):
        # Both email and password are invalid
        auth_login('new@gmail.com', 'unknown')
    with pytest.raises(AccessError):
        # Both email and password are empty
        auth_login('', '')


############################# Auth_logout #############################

def test_logout(register_user):
    '''
    Tests logging out cases: Where you cannot log out if you are already logged out
    and you cannot logout with invalid token
    '''

    user_1 = register_user
    user_1_token = user_1['token']

    # Valid token
    assert auth_logout(user_1_token) == {'is_success':True}
    # Already logged out token
    assert auth_logout(user_1_token) == {'is_success':False}
    # Invalid token
    assert auth_logout('wrong@gmail.com') == {'is_success':False}


############################# Auth_register #############################

def test_valid_auth_register():
    '''
    Testing register function: Registers two new accounts and checks the output token and uid values
    '''

    clear()
    user_1_token = jwt.encode({'user_email': 'vickyhu010@gmail.com'}, SECRET, algorithm='HS256').decode('UTF-8')
    user_2_token = jwt.encode({'user_email': 'simple@gmail.com'}, SECRET, algorithm='HS256').decode('UTF-8')

    assert auth_register('vickyhu010@gmail.com', 'password123', 'Julian', 'Caesar') == {'u_id': 0, 'token': user_1_token}
    assert auth_register('simple@gmail.com', 'bunny4252', 'Bunny', 'Rabbit') == {'u_id': 1, 'token': user_2_token}


def test_invalid_email_register(register_user):
    '''
    Testing register function: Checks invalid inputs of emails for register
    '''

    with pytest.raises(InputError):
    # Invalid email
        auth_register('invalid', 'password', 'Julian', 'Caesar')

    with pytest.raises(InputError):
    # Empty email
        auth_register('', 'bunny4252', 'Bunny', 'Rabbit')

    with pytest.raises(InputError):
    # Already registered email
        auth_register('vickyhu010@gmail.com', 'bunny4252', 'Bunny', 'Rabbit')


def test_invalid_password_register():
    '''
    Testing register function: Checks invalid password inputs for register
    '''
    with pytest.raises(InputError):
    # Short Password
        auth_register('newemail@gmail.com', '123', 'Julian', 'Caesar')

    with pytest.raises(InputError):
    # Empty password
        auth_register('newemail@gmail.com', '', 'Bunny', 'Rabbit')


def test_invalid_name_register():
    '''
    Testing register function: Check invalid name input combinations for register
    '''
    with pytest.raises(InputError):
    # Name > 50 character
        auth_register('newemail@gmail.com', 'pass123', 'a'*100, 'Caesar')

    with pytest.raises(InputError):
    # Empty first name
        auth_register('newemail@gmail.com', 'pass123', '', 'Caesar')

    with pytest.raises(InputError):
    # Last name > 50 characters
        auth_register('newemail@gmail.com', 'bunny4252', 'Bunny', 'a'*100)

    with pytest.raises(InputError):            
    # Empty last name
        auth_register('newemail@gmail.com', 'bunny4252', 'Bunny', '')

    with pytest.raises(InputError):
    # Empty first and last name
        auth_register('newemail@gmail.com', 'bunny4252', '', '')

    with pytest.raises(InputError):
    # Invalid name format
        auth_register('newemail@gmail.com', 'bunny4252', '%Dais y', 'Wa n#')


def test_handle_length():
    '''
    Testing handle generation: Checking that a handle is generated correctly 
    '''
    # Registering a new user that will generate a handle over 20 characters
    clear()
    user_1 = auth_register('simple@gmail.com', 'bunny4252', 'a'*30, 'b'*30)
    user_detail = user_profile(user_1['token'],user_1['u_id'])

    # Assert that the handle is only 20 characters long
    assert user_detail['user']['handle_str'] == 'a'*20

    # Registering a new user with a handle under 20 characters
    user_2 = auth_register('vickyhu010@gmail.com', '1234567', 'Annie', 'Li')
    user_2_detail = user_profile(user_2['token'],user_2['u_id'])

    # Assert that the handle is the correct string
    assert user_2_detail['user']['handle_str'] == 'AnnieLi'


############################# Auth_Passwordreset_Request #############################
def test_request_unregistered_email():
    # Email is unregistered
    clear()
    with pytest.raises(InputError):
        auth_passwordreset_request('vickyhu010@gmail.com')
def test_request_empty_email():
    # Empty string was entered 
    clear()
    with pytest.raises(InputError):
        auth_passwordreset_request(' ')

############################# Auth_Passwordreset_Reset #############################
def test_correct_reset(password_user):
    # Check that the password can be correctly reset
    auth_passwordreset_reset(password_user,'helloworld')
    for user in users_detail:
        if user['user_email'] == 'vickyhu010@gmail.com':
            assert user['password'] == 'helloworld'

    
def test_incorrect_code(password_user):
    # Empty verification code
    with pytest.raises(InputError):
        auth_passwordreset_reset(' ','helloworld')
    # Incorrect input digits
    with pytest.raises(InputError):
        auth_passwordreset_reset('12334','helloworld')
    # Correct code with random trailing values
    with pytest.raises(InputError):
        auth_passwordreset_reset(str(password_user) + 'wrong','helloworld')

def test_invalid_password(password_user):
    # Empty password input
    with pytest.raises(InputError):
        auth_passwordreset_reset(password_user,' ')
    # New password is less than 6 characters
    with pytest.raises(InputError):
        auth_passwordreset_reset(password_user,'123')
