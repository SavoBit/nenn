from django.contrib.auth.hashers import PBKDF2PasswordHasher


class CrapHasher(PBKDF2PasswordHasher):
    iterations = 10
