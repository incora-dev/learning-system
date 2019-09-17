def jwt_response_payload_handler(token, user=None, request=None):

    ctx = {'token': token}
    if user:
        ctx.update({'username': user.username, 'user_is_manager': user.get_manager_permission()})
    return ctx