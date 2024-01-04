'''
User module containing functions that can return a user's
profile while also setting a new name, email and handle
'''

from error import InputError, AccessError
from Global_variables import users_detail
from auth import check_email_exists, check_email_valid, check_first_last_name_valid
import requests
from PIL import Image
from io import BytesIO
import urllib.request
from flask import request

REGEX = '^[a-z0-9]+[\\._]?[a-z0-9]+[@]\\w+[.]\\w{2,3}$'


def is_token_valid(token):
    ''' Checks if the token is valid and if valid, returns a user'''
    for user in users_detail:
        if user['token'] == token:
            return True
    raise AccessError('Token is invalid')


def user_profile(token, u_id):
    '''
    When a valid user profile is searched, return the user profile.
    Gets the data of users who are logged in or logged out
    '''

    global users_detail
    # Checks if the token provided is active
    is_token_valid(token)

    # Loops to find a user in users_detail database with the input u_id
    for user in users_detail:
        if user['u_id'] == u_id:
            # If the correct user is found, return the user profile information
            return {
                'user': {
                    'u_id': user['u_id'],
                    'email': user['user_email'],
                    'name_first': user['first_name'],
                    'name_last': user['last_name'],
                    'handle_str': user['handle'],
                    'profile_img_url': user['profile_img_url']
                },
            }
    # If invalid u_id is inputted, raise an input error
    raise InputError('User with u_id is not a valid user')


def user_profile_setname(token, name_first, name_last):
    '''
    When a user is logged in with a valid token, they can reset their first and last name
    '''
    global users_detail
    # Checks if the token provided is active
    is_token_valid(token)
    # Checks if the first and last name are valid names
    check_first_last_name_valid(name_first, name_last)
    # Checks if the token is matched to a valid user
    for user in users_detail:
        if user['token'] == token:
            user['first_name'] = name_first
            user['last_name'] = name_last

    return {}


def user_profile_setemail(token, email):
    ''' Change the email of the user '''

    # Checks to see if token and email are valid inputs

    is_token_valid(token)

    check_email_valid(email)

    check_email_exists(email)

    # Counter through user details to update the email

    i = 0

    for user in users_detail:
        if user['token'] == token:
            users_detail[i]['user_email'] = email
        i += 1

    return {
    }


def user_profile_sethandle(token, handle_str):
    ''' Change the handle of the user '''

    # Checks to see if token and handle_str are valid inputs

    is_token_valid(token)

    # Removing leading and trailing spaces in handle

    handle_str = handle_str.strip()

    check_sethandle(handle_str)

    # Counter through user details to update the handle

    i = 0

    for user in users_detail:
        if token == user['token']:
            users_detail[i]['handle'] = handle_str
        i += 1

    return {
    }


def check_sethandle(handle_str):
    ''' sethandle check function '''

    if len(handle_str) > 20 or len(handle_str) < 3:
        raise InputError("Handle length must be between 3 and 20 characters")

    for user in users_detail:
        if user['handle'] == handle_str:
            raise InputError("Handle is already used by another user")

    if not all(x.isalnum() or x.isspace() for x in handle_str):
        raise InputError(
            "Handle must only contain the numbers and letters a-z, 0-9")

    return True


def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    '''Upload the profile picture of the user'''

    is_token_valid(token)

    # Requesting url to return a status code, if not 200 then raise Error

    if requests.get(img_url).status_code != 200:
        raise InputError("This is an invalid link")

    # Grab image data via the request of the url with .content

    img_data = requests.get(img_url).content

    # Check whether url uploaded is a jpeg

    if get_image_type(img_url) not in ['jpeg', 'jpg']:
        raise InputError("Image uploaded is not a JPG")

    # Grab width and height of image

    width, height = get_image_size(img_data)

    # Check if user has input within dimensions, raise Error if outside bounding box

    if bounding_box_out_of_range(x_start, y_start, x_end, y_end, width, height) or input_zero_all(x_start, y_start, x_end, y_end) or input_same_start_and_end(x_start, y_start, x_end, y_end):
        raise InputError(
            "Dimensions are out of bounds, x start and y start is located at the top left (0,0)")

    filename = f'{token}.{get_image_type(img_url)}'
    urllib.request.urlretrieve(img_url, filename)
    #crop_image(img_data, x_start, y_start, x_end, y_end).save(filename)
    Image.open(filename).crop((x_start, y_start, x_end, y_end)).save(filename)
    for user in users_detail:
        if user['token'] == token:
            try:
                user['profile_img_url'] = f'{request.url_root}images/{filename}'
            except:
                user['profile_img_url'] = ""

    return {}


def get_image_size(img_data):
    '''Get the image size'''
    return Image.open(BytesIO(img_data)).size


def get_image_type(img_url):
    '''Get the image type'''
    # return imghdr.what(BytesIO(img_data))
    return img_url.rsplit('.', 1)[1].lower()


def input_zero_all(x_start, y_start, x_end, y_end):
    return x_start == 0 and x_end == 0 and y_start == 0 and y_end == 0


def input_same_start_and_end(x_start, y_start, x_end, y_end):
    return x_start == x_end or y_start == y_end


def bounding_box_out_of_range(x_start, y_start, x_end, y_end, width, height):
    '''Check if the input is out of the dimensions of the image'''
    return x_start < 0 or x_end < 0 or y_start < 0 or y_end < 0 or x_start > width or x_end > width or y_start > height or y_end > height
