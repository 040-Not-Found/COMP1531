Assumptions


Auth_login:

User isn't currently logged in
User details have been registered
Auth_logout:
User is logged in


Auth_register:

Name, email, password cannot be empty, cannot have empty spaces
Details aren't already registered
Registering will automatically log you in for a session


channels_list:

Assume the input tokens are user emails, which are all strings
The input token cannot be empty
Assume an authorised user who is logged out will have no access to channels_listl function.


channels_listall:

Token cannot be empty
Unauthorised user cannot view the list of all channels
Assume an authorised user who is logged out will have no access to channels_list_all function.


channels_create:

Unregistered user cannot create a channel


channel_invite:

If user cannot be invited to a channel if they exist in the channel already.
If the channel is private, then only owner can invite others


channel_details:

assume that if input token does not refer to any user, we still raise an AccessError
assume that if both token and channel_id does not exist, we raise an InputError


channel_messages:

assume that if the start value is greater than the size of the messages, and
the token is not the member of the channel, it will raise an Input Error
assume that if the channel does not exist and the token is not the member
of the channel, it will raise an Input Error


channel_addowner:

Channel ID is a valid channel
The user cannot already be an owner of the channel
Both authorising user and user with u_id must be logged in


channel_removeowner:

Owners can remove himself
The owner cannot remove other owners
The channel must have at least one owner (the creator)
Both authorising user and user with u_id must be logged in


channel_leave:

A user must be logged in to leave


channel_join:

User has to be authorised (invited by an owner) to join a private channel
User token must exist in the user database
Channel must exist in order for the user to join the channel
A user must be logged in to join

search:

The authorising user can only see the channel's messages that he in

Return the details both logged in and logged out users
Do not show the user's password

message_pin:
only the owner of the channel can pin the message

message_unpin:
If remove the owner of the user who pins the message 
or the user leave the channel, his message will be unpin
All owner can unpin messages