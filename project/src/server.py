import sys
import threading
from datetime import datetime, timezone
from json import dumps
from flask import Flask, request, send_from_directory
from flask_mail import Mail, Message
from flask_cors import CORS
from error import InputError
from user import *
from auth import *
from Global_variables import *
from message import *
from other import *
from channels import *
from channel import *
from standup import *


registeredOnce = True


def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response



APP = Flask(__name__)
# Setting up sender email server
APP.config.update(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'mango1531example@gmail.com',
    MAIL_PASSWORD = "mango1531"
)



CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Example


@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })


@APP.route('/auth/passwordreset/request', methods=['POST'])
def auth_request_reset():
    '''
    Sends an email to the user containing a verification code
    they can use to reset password
    '''
    info = request.get_json()
    auth_passwordreset_request(info['email'])
    code = get_user_data('user_email', info['email'], 'verification_code')
    mail = Mail(APP)
    try:
        msg = Message("Testing mailing verification code",
                      sender="mango1531example@gmail.com",
                      recipients=[info['email']])
        msg.body = f"Hello! {code} is your 6 digit code!"
        mail.send(msg)
        return {}
    except Exception as e:
        return str(e)

@APP.route('/auth/passwordreset/reset', methods=['POST'])
def auth_reset_reset():
    '''
    When given a correct verification code, resets the password to new password
    '''
    info = request.get_json()
    auth_passwordreset_reset(info['reset_code'], info['new_password'])
    return {}


@APP.route("/channel/addowner", methods=["POST"])
def addowner():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    u_id = int(data['u_id'])

    channel_addowner(token, channel_id, u_id)

    return dumps({})


@APP.route("/channel/removeowner", methods=["POST"])
def removeowner():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    u_id = int(data['u_id'])

    channel_removeowner(token, channel_id, u_id)

    return dumps({})


@APP.route("/user/profile/setemail", methods=['PUT'])
def setemail():
    data = request.get_json()
    token_1 = data['token']
    email = data['email']
    user_profile_setemail(token_1, email)
    return {}


@APP.route("/user/profile/sethandle", methods=['PUT'])
def sethandle():
    data = request.get_json()
    token_1 = data['token']
    handle = data['handle_str']
    user_profile_sethandle(token_1, handle)
    return {}


@APP.route("/channel/leave", methods=['POST'])
def channelleave():
    data = request.get_json()
    token_1 = data['token']
    channel_id = int(data['channel_id'])
    channel_leave(token_1, channel_id)
    return {}


@APP.route("/channel/join", methods=['POST'])
def channeljoin():
    data = request.get_json()
    token_1 = data['token']
    channel_id = int(data['channel_id'])
    channel_join(token_1, channel_id)
    return {}


@APP.route("/message/send", methods=['POST'])
def msg_send_http():
    msg = request.get_json()
    token = msg['token']
    channel_id = int(msg['channel_id'])
    message = msg['message']

    new_msg = message_send(token, channel_id, message)

    return dumps({
        'message_id': new_msg['message_id'],
    })


@APP.route("/message/remove", methods=['DELETE'])
def msg_remove_http():
    msg = request.get_json()
    token = msg['token']
    message_id = int(msg['message_id'])

    message_remove(token, message_id)

    return {}


@APP.route("/message/edit", methods=['PUT'])
def msg_edit_http():
    msg = request.get_json()
    token = msg['token']
    message_id = int(msg['message_id'])
    message = msg['message']

    message_edit(token, message_id, message)

    return {}


@APP.route("/admin/userpermission/change", methods=['POST'])
def user_permission_http():
    user = request.get_json()
    token = user['token']
    u_id = int(user['u_id'])
    permission_id = int(user['permission_id'])

    admin_userpermission_change(token, u_id, permission_id)

    return {}


@APP.route("/channel/invite", methods=["POST"])
def channel_invite_http():
    channel = request.get_json()
    token = channel['token']
    channel_id = int(channel['channel_id'])
    u_id = int(channel['u_id'])

    channel_invite(token, channel_id, u_id)

    return dumps({})


@APP.route("/channel/details", methods=["GET"])
def channel_details_http():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))

    return dumps(channel_details(token, channel_id))


@APP.route("/channel/messages", methods=['GET'])
def channel_msg_http():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))

    return dumps(channel_messages(token, channel_id, start))


@APP.route("/channels/list", methods=["GET"])
def channels_list_http():
    token = request.args.get('token')

    channels = channels_list(token)

    return dumps({
        'channels': channels
    })


@APP.route("/channels/listall", methods=["GET"])
def channels_listall_http():
    token = request.args.get('token')

    channels = channels_listall(token)

    return dumps({
        'channels': channels
    })


@APP.route("/channels/create", methods=['POST'])
def channels_create_http():
    channel = request.get_json()
    token = channel['token']
    is_pub = channel['is_public']
    name = channel['name']

    new_channel = channels_create(token, name, is_pub)
    return dumps({
        'channel_id': new_channel['channel_id'],
    })


@APP.route("/auth/login", methods=['POST'])
def login():
    '''
    Flask: Logs a user in when taking user email and password
    '''
    info = request.get_json()
    user = auth_login(info['email'], info['password'])
    return dumps({
        'u_id': user['u_id'],
        'token': user['token'],
    })


@APP.route("/auth/logout", methods=['POST'])
def logout():
    '''
    Flask: Logs a user out by deactivating their active token
    '''
    info = request.get_json()
    user = auth_logout(info['token'])
    return dumps({
        'is_success': user['is_success']
    })


@APP.route("/auth/register", methods=['POST'])
def register():
    '''
    Flask: Registers a new user
    '''
    info = request.get_json()
    user = auth_register(info['email'], info['password'],
                         info['name_first'], info['name_last'])
    return dumps({
        'u_id': user['u_id'],
        'token': user['token'],
    })


@APP.route('/user/profile', methods=['GET'])
def profile():
    '''
    Flask: returns the user details
    '''
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    user = user_profile(token, u_id)
    return dumps(
        user
    )


@APP.route("/user/profile/setname", methods=['PUT'])
def setname():
    '''
    Flask: Sets new name for a user
    '''
    info = request.get_json()
    user_profile_setname(info['token'], info['name_first'], info['name_last'])
    return {}


@APP.route("/search", methods=["GET"])
def search_http():
    token = request.args.get('token')
    query_str = request.args.get('query_str')

    msg = search(token, query_str)

    return dumps({
        'messages': msg
    })


@APP.route("/users/all", methods=['GET'])
def users_all_http():
    token = request.args.get('token')
    user_details = users_all(token)

    return dumps({
        'users': user_details
    })


@APP.route('/user/profile/uploadphoto', methods=['POST'])
def user_profile_uploadphoto_http():
    '''
    Flask: Upload the user photo
    '''
    info = request.get_json()
    token_1 = info['token']
    img_url = info['img_url']
    x_start = int(info['x_start'])
    x_end = int(info['x_end'])
    y_start = int(info['y_start'])
    y_end = int(info['y_end'])
    return(user_profile_uploadphoto(token_1, img_url, x_start, y_start, x_end, y_end))


@APP.route('/images/<filename>', methods=["GET"])
def send_photo(filename):
    return send_from_directory('../', filename)


@APP.route("/standup/start", methods=["POST"])
def start_a_standup():
    data = request.get_json()

    return dumps(standup_start(data['token'], int(data['channel_id']), int(data['length'])))


@APP.route("/standup/active", methods=['GET'])
def is_standup_active():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))

    return dumps(standup_active(token, channel_id))


@APP.route("/message/sendlater", methods=['POST'])
def sendlater():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    message = data['message']
    time_sent = int(data['time_sent'])

    return dumps(message_sendlater(token, channel_id, message, time_sent))


@APP.route("/message/react", methods=['POST'])
def react():
    data = request.get_json()
    token = data['token']
    message_id = int(data['message_id'])
    react_id = int(data['react_id'])
    return dumps(message_react(token, message_id, react_id))


@APP.route("/message/unreact", methods=['POST'])
def unreact():
    data = request.get_json()
    token = data['token']
    message_id = int(data['message_id'])
    react_id = int(data['react_id'])
    return dumps(message_unreact(token, message_id, react_id))


@APP.route("/message/pin", methods=["POST"])
def pin():
    data = request.get_json()
    return dumps(message_pin(data['token'], int(data['message_id'])))


@APP.route("/message/unpin", methods=['POST'])
def unpin():
    data = request.get_json()
    return dumps(message_unpin(data['token'], int(data['message_id'])))


@APP.route("/standup/send", methods=["POST"])
def standup_send_msg():
    '''
    Flask: Standup send message
    '''
    data = request.get_json()
    return dumps(standup_send(data['token'], int(data['channel_id']), data['message']))


if __name__ == "__main__":
    APP.run(port=0)  # Do not edit this port
