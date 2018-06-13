# TODO make extra functionality for admins, so that becoming admin actually does something
import codecs
import pickle
import subprocess

from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.forms.models import model_to_dict
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .models import Employee
from . import badxml


def _flag_hack(flag, dir='.'):
    # TODO remove this soon ;(  8 Jun 18
    import os
    secret = 'secret.txt{' + flag + '}'
    with open(os.path.join(dir, 'secret.txt'), 'w') as f:
        f.write(secret)


# XXX unused
def _render_string_with_jinja2(s, request=None, context=None):
    '''django.template.Template doesn't respect the BACKENDS settings
    but we want to use Jinja. I just really want to demonstrate template
    injection.
    '''
    # see, this shoulda been flask so I wouldn't have to take these byantine measures
    # to circumvent django's normal behavior
    from django.template import engines
    engines.all()  # this instantiates all the backends...
    return engines._engines['jinja2'].from_string(s).render(request=request, context=context)


@auth.decorators.login_required  # authn w/o authz edit: actually, I'm keeping authz here
def profile(request):
    # super contrived
    userid = request.GET.get('id', 0)
    if not userid:
        return redirect(reverse('profile') + '?id=' + str(request.user.id))
    user = auth.models.User.objects.get(id=userid)
    if request.user.id != user.id:
        raise PermissionDenied
    try:
        employee = Employee.objects.get(user_id=userid)
        print(employee)
    except Employee.DoesNotExist:
        employee = None
    return render(request, 'vulnerable/profile.html', {'user': user, 'employee': employee})


def login_check(request):
    '''just redir to the destination if already auth'd'''
    next = request.GET.get('next', '')
    if request.user.is_authenticated:
        return redirect(next)
    else:
        return redirect(reverse('login') + '?next=' + next)


def signup(request):
    next = request.GET.get('next')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = auth.authenticate(username=username, password=raw_password)
            auth.login(request, user)
            return redirect(next or 'home')
    else:
        form = UserCreationForm()
    return render(request, 'vulnerable/signup.html', {'form': form, 'next': next})


# Command Injection
@require_http_methods(['POST'])
def injection1(request):
    '''A softball to get us started.'''
    _flag_hack('bec83aa6d4e830802192bacde5554591')
    host = request.POST.get('domain')
    cmd = 'whois ' + host

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True
    ).stdout

    result = codecs.decode(result, 'utf-8', 'backslashreplace')
    return render(request, 'vulnerable/shell-injection.html', {'result': result, 'cmd': cmd})


@require_http_methods(['POST'])
def injection2(request):
    '''A shoddy blacklisting attempt'''
    _flag_hack('4fcdbd8e252069fecec41fc70f7f337e')
    blacklist = ['&', ';', '|', '$', '(', ')']
    host = request.POST.get('domain')
    cmd = 'whois ' + host

    if any(filter(lambda x: x in blacklist, cmd)):
        result = b'Error! Some characters in your query are disallowed.\n'
    else:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True
        ).stdout

    result = codecs.decode(result, 'utf-8', 'backslashreplace')
    return render(request, 'vulnerable/shell-injection2.html', {'result': result, 'cmd': cmd})


@require_http_methods(['POST'])
def injection3(request):
    '''Let's see you inject /bin/cat now!'''
    _flag_hack('1e0bd79de326aec57a91057da034c295')

    blacklist = ['cat', 'secret']
    host = request.POST.get('domain')
    cmd = 'whois ' + host

    if any(filter(lambda x: x in host.lower(), blacklist)):
        result = b'Aha! No cats allowed!\n'
    else:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True
        ).stdout

    result = codecs.decode(result, 'utf-8', 'backslashreplace')
    return render(request, 'vulnerable/shell-injection3.html', {'result': result, 'cmd': cmd})


@require_http_methods(['POST'])
def injection4(request):
    '''
    Tokenized! With direct invocation of the executable, not going through
    a shell. This should actually be safe, if the attacker controls only this input.
    '''
    import shlex
    host = request.POST.get('domain')
    cmd = 'whois ' + host

    result = subprocess.run(
        shlex.split(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).stdout

    result = codecs.decode(result, 'utf-8', 'backslashreplace')
    return render(request, 'vulnerable/shell-injection.html', {'result': result})


# SQL Injection
@auth.decorators.login_required
def admin(request):
    if not request.user.is_superuser:
        return redirect(reverse('login') + '?next=' + reverse('admin'))
    users = []
    for u in auth.models.User.objects.all():
        try:
            e = Employee.objects.get(user_id=u.id)
        except Employee.DoesNotExist:
            e = None
        u_dict = model_to_dict(u)
        u_dict['employee'] = e
        users.append(u_dict)
    users.sort(key=lambda u: u['id'])
    return render(request, 'vulnerable/admin.html', {'users': users})


# XXE
@require_http_methods(['POST'])
def xxe(request):
    _flag_hack('6b08358ba7b88b7c15da09eb8d5511db', '/')  # make it easier
    try:
        props = badxml.xlsx_attributes(request.FILES['file'])
        return render(request, 'vulnerable/_xlsx_info.html', props)
    except Exception as e:
        return render(
            request,
            'vulnerable/_error.html',
            {'error': 'Something went wrong.', 'retry_name': 'xxe'}
        )


# Security Misconfiguration
def exception(request):
    raise Exception('Hm')


# Insecure Deserialization, Broken Access Control, Broken Authn,...
@require_http_methods(['GET'])
@auth.decorators.login_required
def serialize_user(request):
    '''Use this for combined broken auth, security misconfiguration,
    and insecure deserialization. Why not.
    '''
    userid = request.GET.get('id', 0)
    try:
        user = auth.models.User.objects.get(id=userid)
        if user.is_superuser and not request.user.is_superuser:
            raise PermissionDenied
        user_dict = model_to_dict(user)
        if request.user.id != user.id:
            # XXX hack to get some feedback in last minute
            # NOTE flag hardcoded
            user_dict['username'] = 'secret{43ab154d4788d1409fec5fcc7c632e69}'
            user_dict['pwned'] = True  # XXX hack
        encoded = codecs.encode(pickle.dumps(user_dict, 0), 'base64')
        encoded = ''.join(codecs.decode(encoded, 'ascii').split('\n'))
        return render(request, 'vulnerable/backup.html', {'backup': encoded})
    except auth.models.User.DoesNotExist:
        return Http404()


# Insecure Deserialization
@require_http_methods(['POST'])
def deserialize_user(request):
    _flag_hack('783d31df5059c0918f1480c24cb21f71')
    try:
        profile = codecs.encode(request.POST.get('profile'), 'ascii')
        data = pickle.loads(codecs.decode(profile, 'base64'))
        user = auth.models.User.objects.get(username=data['username'])
        # TODO in the future add employee
    except auth.models.User.DoesNotExist:
        # Oops, lost the data lol
        # doing this manually and not *really* restoring data because
        # create(**dict) doesn't work once you have a one-to-one link
        # XXX refactor
        email = data.get('pwned') and 'Good@job.my.dude' or None
        user = auth.models.User.objects.create_user(
            username=data['username'],
            password=data['password'],
            email=email
        )
    except Exception as e:
        return render(
            request,
            'vulnerable/_error.html',
            {'error': 'Something went wrong.', 'retry_name': 'profile'}
        )

    if data.get('pwned'):
        # XXX a hack to fix later...
        return render(request, 'vulnerable/profile.html', {'user': user})

    return redirect(reverse('profile'))


# PhantomJS Examples
def report(request):
    user = request.user
    employee = user.employee
    print(employee)
    pass
