from collections import OrderedDict
from django.contrib.auth.hashers import BasePasswordHasher


class CrapHasher(BasePasswordHasher):
    '''Extremely high performance hasher'''
    algorithm = "high_performance"

    def encode(self, password, salt, iterations=None):
        assert password is not None
        return password

    def verify(self, password, encoded):
        return password == encoded

    def safe_summary(self, encoded):
        return OrderedDict([
            ('algorithm', None),
            ('iterations', 0),
            ('salt', ''),
            ('hash', ''),
        ])

    def must_update(self, encoded):
        return False

    def harden_runtime(self, password, encoded):
        return
