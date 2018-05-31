from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class CrapAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            query = "select * from auth_user where username = '{}' and password = '{}'"
            return User.objects.raw(query.format(username, password))[0]
        except Exception:
            pass
