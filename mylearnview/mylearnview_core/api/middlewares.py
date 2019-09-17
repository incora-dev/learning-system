import json


class RequestAPIMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.process_response(request)

    def is_api_request(self, request):
        path_info = request.META['PATH_INFO']
        # print(path_info, content_type)
        return path_info.startswith('/api/') and not 'docs' in path_info

    def process_response(self, request):
        response = self.get_response(request)
        if self.is_api_request(request) and request.method == 'GET' and request.user.is_authenticated:
            response.data['user_is_manager'] = request.user.get_manager_permission()
            response.content = json.dumps(response.data)
        return response