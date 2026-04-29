from django.http import JsonResponse

class APIVersionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/'):
            version = request.headers.get('X-API-Version')
            if version != '1': 
                return JsonResponse({
                    "status": "error",
                    "message": "API version header required"
                }, status=400) 
        return self.get_response(request)