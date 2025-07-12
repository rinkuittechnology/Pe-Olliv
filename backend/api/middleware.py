from django.utils.functional import SimpleLazyObject
from django.contrib.auth.middleware import get_user
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.deprecation import MiddlewareMixin



class JWTCookieAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.user = SimpleLazyObject(lambda: self.__class__.get_jwt_user(request))

    @staticmethod
    def get_jwt_user(request):
        user = get_user(request)
        if user.is_authenticated:
            return user
        
        try:
            access_token = request.COOKIES.get('access_token')
            if access_token:
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(access_token)
                return jwt_auth.get_user(validated_token)
        except:
            pass
        
        return user