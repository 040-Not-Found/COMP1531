
message_remove:
    message_id is unique
    The error order is 
    1st: user is not exist -------- AccessError
    2nd: not owner and not send the message ------- AccessError
    3rd: message not exist ------- InputError

Assumptions for admin_userpermission_change:
1. A global owner can change his own permission if in a channel
2. A global owner will automatically become an owner of the channel once joined
3. A global member who is not the owner of a channel cannot change everyone's permission
4. Owners of a channel can change everyone's permission
5. There is only one global owner who is the very first person to sign up (whose user_id is 0)
6. If owners of a channel are changed to members, they are still in the channel
7. There are only two valid permission_id 1(owners) and 2(members)

message_react/unreact:
1. when the input token doesn't refer to a valid user, it will raise an InputError

