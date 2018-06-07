import datetime
import random
import time

from django.contrib.auth.models import User
from uwu.vulnerable.models import Employee


NAMES = [n.strip() for n in open('/usr/share/dict/propernames').readlines()]
EMAILS = ['gmail.com', 'yahoo.com', 'hotmail.com', 'sbcglobal.net']
WORDS = [n.strip() for n in open('/usr/share/dict/words').readlines()]


def _random_date(start, end, fmt, percent):
    s_date = time.mktime(time.strptime(start, fmt))
    e_date = time.mktime(time.strptime(end, fmt))

    d = s_date + (percent * (e_date - s_date))
    return time.strftime(fmt, time.localtime(d))


def random_date(start, end, fmt='%Y-%m-%d'):
    percent = random.random()
    return _random_date(start, end, fmt, percent)


def random_ssn():
    numbers = ''.join(str(i) for i in [random.randint(0, 10) for _ in range(9)])
    return '{}-{}-{}'.format(numbers[:3], numbers[3:6], numbers[6:])


def random_phone():
    numbers = ''.join(str(i) for i in [random.randint(0, 10) for _ in range(10)])
    return numbers


def make_user():
    admin = random.random() < 0.01
    first_name = random.choice(NAMES)
    last_name = random.choice(NAMES)
    username = (first_name + last_name).lower()
    has_email = random.random() < 0.7

    user = {
        'is_superuser': admin,
        'username': username,
        'email': username + random.choice(EMAILS) if has_email else None,
        'password': random.choice(WORDS) + random.choice(WORDS),
    }
    u = User.objects.create_user(**user)
    if admin:
        print('is admin', user)
    else:
        print(u)

    is_employee = random.random() < 0.25
    if is_employee:
        dob = datetime.date(*(int(i) for i in random_date('1970-01-01', '2002-01-01').split('-')))
        e = Employee.objects.create(user=u, ssn=random_ssn(), dob=dob, phone=random_phone())
        print(e)


def do_all():
    for _ in range(7):
        make_user()
    a = User.objects.create_user(username='admin', is_superuser=True, email='admin@lol.com', password=random.choice(WORDS) + random.choice(WORDS))
    print('made admin', a)
    for _ in range(60):
        make_user()
