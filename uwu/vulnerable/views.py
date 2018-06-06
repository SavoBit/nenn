# TODO make extra functionality for admins, so that becoming admin actually does something
import codecs
import pickle
import subprocess

from django.contrib import auth
from django.forms.models import model_to_dict
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from . import badxml


def _render_string_with_jinja2(s, request=None, context=None):
    '''django.template.Template doesn't respect the BACKENDS settings
    but we want to use Jinja. I just really want to demonstrate template
    injection.
    '''
    from django.template import engines
    engines.all()  # this instantiates all the backends...
    return engines._engines['jinja2'].from_string(s).render(request=request, context=context)


def profile(request):
    return render(request, 'vulnerable/profile.html', {'user': request.user})


# Injection
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

    result = codecs.decode(result, 'utf-8')  # can error if you're cheeky
    return render(request, 'vulnerable/shell-injection.html', {'result': result})


@require_http_methods(['POST'])
def injection2(request):
    '''A shoddy blacklisting attempt'''
    blacklist = ['&', ';', '|']
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

    result = codecs.decode(result, 'utf-8')  # can error if you're cheeky
    return render(request, 'vulnerable/shell-injection.html', {'result': result})


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
