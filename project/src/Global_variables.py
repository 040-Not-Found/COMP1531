users_detail = []
channels = []
total_message = 0

'''
prototype for global variables


users_detail = [
    {
        'u_id' : ,
        'handle' : ,
        'user_email : ,
        'first_name' : ,
        'last_name' : ,
        'token' : ,
        'permission’ : ,
    },
    {

    },
]

channels = [
    {
        'channel_id' : ,
        'channel_name' : ,
        'is_public' : ,
        'owner_id': [],
        'all_mem' : [],
        'messages' : [
            {
                'message_id' : ,
                'u_id' : ,
                'message' : ,
                'time_create' : ,
                'reacts' : {
                    'react_id' : 1,
                    'u_ids' : [],
                    'is_this_user_created' : ,
                }
                'is_pinned' : , 
            },
            {

            },
        ],
        'time_finish' : ,
        'standup_user_token' : , (optional)
        'stand_up_send' : , (string) (optional)
        'standup_thread_started' : , (boolean) (optional) 
    },
    {

    },
]
'''
