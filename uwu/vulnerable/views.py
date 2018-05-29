import codecs
import pickle
import subprocess

from django.db import connection
from django.http import HttpResponse  # , Http404
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from . import badxml


# todo
# - [x] injection - did some contrived shell injection
# - [ ] broken auth <- shitty PBKDF2 tuning doesn't count, eh
# - [ ] sensitive data exposure <- maybe expose .git?
# - [x] xxe
# - [-] broken access control
# - [x] security misconfiguration
#   - be nice to serve this behind a webserver with directory listing enabled
#   - then you could grab .git, and have sensitive data exposure while you're at it
#   - or really, don't even bother with that. just have nginx set to try_files
#   - in some sort of webroot, and .git could be found with any number of tools
# - [x] xss
#   - [x] reflected
#   - [x] stored
# - [x] insecure deserialization
# - [ ] using components with known vulnerabilities <- dude, idk
# - insufficient logging & monitoring


def _render_string_with_jinja2(s, request=None, context=None):
    '''django.template.Template doesn't respect the BACKENDS settings
    but we want to use Jinja. I just really want to demonstrate template
    injection.
    '''
    # XXX so yeah, this can die
    from django.template import engines
    engines.all()  # this instantiates all the backends...
    return engines._engines['jinja2'].from_string(s).render(request=request, context=context)


# Injection
@require_http_methods(['POST'])
def injection1(request):
    '''A softball to get us started.'''
    host = request.POST.get('host')
    result = subprocess.run(
        'host ' + host,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True
    ).stdout

    result = codecs.decode(result, 'utf-8')
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
            'host ' + host,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True
        ).stdout

    result = codecs.decode(result, 'utf-8')
    return render(request, 'vulnerable/shell-injection.html', {'result': result})


# Broken Authentication TODO
# | there's not a good way to demonstrate this one, probably?
# | maybe go with the cookie idea, but i'm not sure this is all that easy to
# | demonstrate

# Sensitive Data Exposure TODO
# | there's a lot of ways to go with this; most of the interesting exercises
# | in this app already disclose data, so this may not need its own example


# XXE
# TODO django can serialize models to xml so maybe replace this with a custom
# xml deserializer. make the examples more cohesive and easier to demonstrate
@require_http_methods(['POST'])
def xxe(request):
    # TODO frontend needs to name the file form field 'file'
    if not request.FILES:
        return render(
            request,
            'vulnerable/_error.html',
            {'error': 'Hm, couldn\'t upload that one.', 'retry_name': 'xxe'}
        )
    try:
        props = badxml.xlsx_attributes(request.FILES['file'])
        return render(request, 'vulnerable/_xlsx_info.html', props)
    except Exception as e:
        return render(
            request,
            'vulnerable/_error.html',
            {'error': 'Not a valid XLSX file.', 'retry_name': 'xxe'}
        )


# Broken Access Control TODO
# | probably ahh do the thing where you can;;uh;;hm... access other people's
# | profiles, idk
# | TODO actually we'll just leave this as not-implemented because lol
def user_profile(request):
    # TODO need to do user sessions man
    pass


# Security Misconfiguration
def exception(request):
    # TODO eh, if somebody decides to run this with DEBUG = False,
    # maybe this should render a page with general info about security config
    raise Exception('Hm')


# NOTE this exposes a template injection without length restriction,
# so it's a good place to break out the ol sys with import
def reflected_xss(request, name=''):
    '''Reflect a URL parameter into the DOM, no protections.
    This actually contains a more general template injection.
    '''
    hello_template = '''
        {% extends "challenge.html" %}
        {% block title %}xss{% endblock %}
        {% block content %}
        <p>since the pentest found some xss, I'm redoing these to be more
        illustrative. ''' + name + '</p> {% endblock %}'
    html = _render_string_with_jinja2(hello_template, request=request)
    return HttpResponse(html, content_type='text/html')


def stored_xss(request, userid=-1):
    '''Also easy. Also has a template injection.'''
    # do the same thing but get the name from the db
    pass


def _get_all_users():
    from django.contrib.auth.models import User
    return [u.email for u in User.models.all()]


# Insecure Deserialization, Broken Auth, Injection
@require_http_methods(['POST'])
def serialize_user(request):
    '''Use this for combined broken auth, security misconfiguration,
    and insecure deserialization. Might as well add a SQLi example here too.
    Why not.
    '''
    email = request.POST.get('email')

    with connection.cursor() as cursor:
        cursor.execute(
            "select username, email, is_superuser from auth_user where email = '%s'",
            [email])
        row = cursor.fetchone()

    if not row:
        # TODO return a 404 or render a 404 page
        pass

    encoded = codecs.encode(pickle.dumps(row), 'base64')
    return HttpResponse(encoded, content_type='text/plain')
    # return render(request, 'some url', {'user': encoded})


# Insecure Deserialization
@require_http_methods(['POST'])
def insecure_deserialization(request):
    # you can download a user profile then post here to check integrity
    try:
        user = pickle.loads(codecs.decode(request.body, 'base64'))

        # print(user)
        return HttpResponse(str(user), content_type='text/plain')
        # return render(request, 'vulnerable/owasp2017/pickle.html', user)
    except Exception as e:
        # need to handle this one since it's supposed be exploited
        # print str(e)
        return HttpResponse(b"decode error", content_type='text/plain')
        # return render(request, 'vulnerable/owasp2017/spoiled.html')


# Using Components With Known Vulnerabilities TODO
# | probably just show some examples


# Insufficient Logging and Monitoring TODO
# | I'm. I don't know.
