def user_exists(users, user_id: str):
    '''
    Checks if the user exists, and if not creates it.
    '''
    if user_id not in users:
        users[user_id] = {}
        users[user_id]['experience'] = 0
        users[user_id]['level'] = 0
