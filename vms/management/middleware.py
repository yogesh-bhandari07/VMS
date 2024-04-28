import threading
from rest_framework_simplejwt.tokens import UntypedToken
from django.utils.functional import SimpleLazyObject

def get_user_from_token(token):
    try:
        token_obj = UntypedToken(token)
        user_id = token_obj['user_id']
        if user_id is not None:
            return user_id
    except Exception as e:
        pass
    return None

_request_local = threading.local()

class UserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ["POST", "PUT", "PATCH"]:
            authorization_header = request.META.get('HTTP_AUTHORIZATION', '')
            if authorization_header.startswith('Bearer '):
                token = authorization_header.split('Bearer ')[1].strip()
                user_id = get_user_from_token(token)
                if user_id is not None:
                    setattr(request, 'updated_by', user_id)
                else:
                    setattr(request, 'updated_by', None)
            else:
                setattr(request, 'updated_by', None)
        else:
            setattr(request, 'updated_by', None)
        response = self.get_response(request)
        return response
