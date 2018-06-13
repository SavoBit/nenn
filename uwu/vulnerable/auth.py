from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class CrapAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            query = "select * from auth_user where username = '{}' and password = '{}'".format(
                username,
                password
            )
            print()
            print('   \033[93mauth query:  \033[0m', query)
            user = User.objects.raw(query)
            print('   \033[93mquery result:\033[0m', list(user))  # because there's just one, right?
            print()
            return user[0]
        except Exception as e:
            pass
