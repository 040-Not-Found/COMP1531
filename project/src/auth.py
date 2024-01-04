'''
This file contains all the authorisation functions (auth_login, auth_logout, auth_register)
'''
from random import randint
from Global_variables import users_detail
from error import InputError, AccessError
from random import randint
from helper import change_user_data, check_user_data_exists
import re
import jwt
from helper import *
from flask_mail import Mail, Message

owners = 1
members = 2


# Valid email formula
regex = '^[a-z0-9]+[\\._]?[a-z0-9]+[@]\\w+[.]\\w{2,3}$'
SECRET = 'flock'


def auth_login(email, password):
    '''
    Function which when provided a valid registered email and corresponding password, logs a user in and generates a token
    '''
    global users_detail

    # For loop goes through all users in 'user detail' and checks if the email and password are the same
    for user in users_detail:

        # Valid email
        if user['user_email'] == email:

            if user['password'] == password:
                # Valid email and valid password returns the u_id and token
                user['token'] = jwt.encode(
                    {'user_email': email}, SECRET, algorithm='HS256').decode('UTF-8')
                return {'u_id': user['u_id'], 'token': user['token']}

    # Return error if there is invalid email/ invalid email and password
    raise AccessError('Invalid login, please check your email and password')


def auth_logout(token):
    '''
    When provided with an active token, deletes this token
    '''
    if change_user_data('token', token, 'token', '') == True:
        return {'is_success': True}
    # If token doesn't exist or they are already logged out then return false
    return {'is_success': False}


def auth_register(email, password, first_name, last_name):
    '''
    Registers a new user with a unique email and adds them to the users_detail database.
    Ensures password and name are in correct format.
    '''
    # Check if the email exists in database
    if check_user_data_exists('user_email', email):
        raise InputError('Email already exists')
    # Check if the email or password are in the right format
    check_email_valid(email)
    check_password_valid(password)
    # Check if the first and last name are valid
    check_first_last_name_valid(first_name, last_name)
    global users_detail
    # Token generated
    token = jwt.encode({'user_email': email}, SECRET,
                       algorithm='HS256').decode('UTF-8')
    # If no errors returned then append user details to end of list
    user_id = len(users_detail)
    users_detail.append(
        {
            'u_id': user_id,
            'handle': create_handle(first_name, last_name),
            'user_email': email,
            'first_name': first_name,
            'last_name': last_name,
            'token': token,
            'verification_code': "",
            'permission': owners if user_id == 0 else members,
            'password': password,
            'profile_img_url': "",

        }
    )
    return {'u_id': user_id, 'token': token}

'''
def auth_passwordreset_request(email):
    
        When a user requests for their password to be sent, this function sends
        and email with a verification code to check if they're the right person
    
    print(email)
    print(users_detail)
    # if check_user_data_exists('user_email', email):
    for user in users_detail:
        if user['user_email'] == email:
            code = str(randint(100000, 999999))
            #change_user_data('user_email', email, 'verification_code', code)
            user['verification_code'] = code
            return code

    raise InputError("Invalid Email")


def auth_passwordreset_reset(verification_code, new_password):
    
        Function to change a person's password as long as the
        correct verification code has been provided.
        Their new password must also be in the standard format
    
    check_password_valid(new_password)

    # Find user using verification_code
    global users_detail
    i = 0
    for user in users_detail:
        # Loop through user list until the verification code is matched
        if user['verification_code'] == verification_code:
            # Set verification_code to None
            users_detail[i]['verification_code'] = ''
            # Set password to new password
            users_detail[i]['password'] = new_password
            return {}
        i += 1
    raise InputError('You are an idiot')'''



def auth_passwordreset_request(email):
    '''
        When a user requests for their password to be sent, this function sends
        and email with a verification code to check if they're the right person
    '''

    if check_user_data_exists('user_email', email):
        code = str(randint(100000, 999999))
        change_user_data('user_email', email, 'verification_code', code)
        return {}
    
    raise InputError("Invalid Email")

def auth_passwordreset_reset(code, new_password):
    '''
        Function to change a person's password as long as the
        correct verification code has been provided.
        Their new password must also be in the standard format
    '''

    check_password_valid(new_password)

    # Find user using verification_code
    global users_detail
    i = 0
    for user in users_detail:
        # Loop through user list until the verification code is matched
        if user['verification_code'] == code:
            # Set verification_code to None
            users_detail[i]['verification_code'] = None
            # Set password to new password
            users_detail[i]['password'] = new_password
            return {}
        i += 1
    raise InputError('Could not reset password')




def check_email_exists(email):
    '''
        Function to change a person's password as long as the
        correct verification code has been provided.
        Their new password must also be in the standard format
    '''
    for user in users_detail:
        # Valid email
        if user['user_email'] == email:
            raise InputError(
                'This email already exists! Please enter another email')
    return False


def check_email_valid(email):
    '''
    Helper function that checks that an email is in the correct format
    and is a valid email
    '''
    if not(re.search(regex, email)):
        raise InputError('This is not an email! Please enter another email')
    return True


def check_password_valid(password):
    '''
    Helper function that checks the password is over 6 characters long
    '''
    if len(password) < 6:
        raise InputError(
            'This password is too short! Please enter another password')
    return True


def check_first_last_name_valid(first_name, last_name):
    '''
    Helper function that checks the first and last name
    are the right format and length
    '''
    # Checks that the first and last name are both between 1-50 characters of the alphabet
    if not(0 < len(first_name) < 51) or not(first_name.isalpha()):
        raise InputError('Invalid first name!')
    if not(0 < len(last_name) < 51) or not(last_name.isalpha()):
        raise InputError('Invalid last name!')


def create_handle(first_name, last_name):
    '''
    Helper Function that generates a handle with a maximum length of 20
    from the users first and last name
    '''
    handle = first_name + last_name
    # If the handle is greater than 20 characters long, then subtract the extra characters from the end
    if len(handle) > 20:
        handle = handle[:-(len(handle) - 20)]
    return handle
