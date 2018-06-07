# TODO make extra functionality for admins, so that becoming admin actually does something
import codecs
import pickle
import subprocess

from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.forms.models import model_to_dict
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .models import Employee
from . import badxml


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
def profile(request, userid=None):
    # super contrived
    if not userid:
        return redirect(reverse('profile') + '/' + str(request.user.id))
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
    next = request.GET.get('next', '')
    print(request.user)
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
    host = request.POST.get('host')
    result = subprocess.run(
        'whois ' + host,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True
    ).stdout

    result = codecs.decode(result, 'utf-8', 'backslashreplace')
    return render(request, 'vulnerable/shell-injection.html', {'result': result})


@require_http_methods(['POST'])
def injection2(request):
    '''A shoddy blacklisting attempt'''
    blacklist = ['&', ';', '|', '$', '(', ')']
    host = request.POST.get('host')

    if any(filter(lambda x: x in blacklist, host)):
        result = b'Error! Some characters in your query are disallowed.\n'
    else:
        result = subprocess.run(
            'whois ' + host,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True
        ).stdout

    result = codecs.decode(result, 'utf-8', 'backslashreplace')
    return render(request, 'vulnerable/shell-injection.html', {'result': result})


@require_http_methods(['POST'])
def injection3(request):
    '''
    Tokenized! With direct invocation of the executable, not going through
    bash. This would still be unsafe if, say, the attacker controlled the PATH.
    '''
    import shlex
    host = request.POST.get('host')
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


# Broken Authentication
# | there's not a good way to demonstrate this one, probably?
# | maybe go with the cookie idea, but i'm not sure this is all that easy to
# | demonstrate
# | Or just use the slides as an authentication bypass example lol
# | passwords aren't hashed so there you go


# Sensitive Data Exposure TODO
# | there's a lot of ways to go with this; most of the interesting exercises
# | in this app already disclose data, so this may not need its own example


# XXE
# TODO django can serialize models to xml so maybe replace this with a custom
# xml deserializer. make the examples more cohesive and easier to demonstrate
# wait yeah lol, if you just deserialize xml for the backup loader...
@require_http_methods(['POST'])
def xxe(request):
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


# NOTE this exposes a template injection without length restriction,
# so it's a good place to break out the ol sys with import
# def reflected_xss(request, name=''):
#     '''Reflect a URL parameter into the DOM, no protections.
#     This actually contains a more general template injection.
#     '''
#     hello_template = '''
#         {% extends "challenge.html" %}
#         {% block title %}xss{% endblock %}
#         {% block content %}
#         <p>since the pentest found some xss, I'm redoing these to be more
#         illustrative. ''' + name + '</p> {% endblock %}'
#     html = _render_string_with_jinja2(hello_template, request=request)
#     return HttpResponse(html, content_type='text/html')
#
#
# def stored_xss(request, userid=-1):
#     '''Also easy. Also has a template injection.'''
#     # do the same thing but get the name from the db
#     pass


# Insecure Deserialization, Broken Access Control, Broken Authn,...
@require_http_methods(['GET'])
@auth.decorators.login_required  # authn w/o authz
def serialize_user(request, username=None):
    '''Use this for combined broken auth, security misconfiguration,
    and insecure deserialization. Why not.
    '''
    try:
        user = auth.models.User.objects.get(username=username)
        encoded = codecs.encode(pickle.dumps(model_to_dict(user), 0), 'base64')
        return HttpResponse(encoded, content_type='application/octet-stream')
    except auth.models.User.DoesNotExist:
        return Http404()


# Insecure Deserialization
@require_http_methods(['POST'])
@auth.decorators.login_required
def deserialize_user(request):
    try:
        data = pickle.loads(codecs.decode(request.FILES['profile'].read(), 'base64'))
        user = auth.models.User.objects.get(username=data['username'])
    except auth.models.User.DoesNotExist:
        # User has valid backup but we lost their profile! How embarassing!
        user = auth.models.User.create(**data)
    except Exception as e:
        return render(
            request,
            'vulnerable/_error.html',
            {'error': 'Something went wrong.', 'retry_name': 'profile'}
        )

    return render(request, 'vulnerable/profile.html', {'user': user})


# PhantomJS Examples
def report(request):
    user = request.user
    employee = user.employee
    print(employee)
    pass


# Using Components With Known Vulnerabilities
# | no exercise
# | is it low status to use Equifax as the example


# Insufficient Logging and Monitoring
# | no exercise
# | though a flashy option is to add monitoring to the container that you can
# | show at the end as having detected some/all of the attacks
