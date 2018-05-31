# TODO hm, if we use PickleSerializer...
from django.conf.urls import url
# from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.base import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import uwu.vulnerable.views as challenges


urlpatterns = [
    # TODO an index that links to exercises and slides separately
    url(r'^$', TemplateView.as_view(template_name='index.html'), name="home"),
    url(r'^slides/?$', TemplateView.as_view(template_name='slides.html'), name="slides"),
    url(r'^exercises/?$', TemplateView.as_view(template_name='exercises.html'), name="exercises"),
    url(r'^login/?$', LoginView.as_view(template_name='login.html'), name="login"),
    url(r'^logout/?$', LogoutView.as_view(template_name='index.html'), name="logout"),

    # Injection
    url(r'^shell-injection/?$',
        TemplateView.as_view(template_name='vulnerable/shell-injection.html'),
        name='shell-injection'),
    url(r'^injection1/?$', challenges.injection1, name='injection1'),
    url(r'^injection2/?$', challenges.injection2, name='injection2'),

    # wrapped sqli into the profile page
    # url(r'^sql-injection/?$',
    #     TemplateView.as_view(template_name='vulnerable/sql-injection.html'),
    #     name='sql-injection'),

    # Broken Auth
    # no exercise

    # Broken Access Control,... a lot of things
    url(r'^profile/?$',
        TemplateView.as_view(template_name='vulnerable/profile.html'),
        name='profile'),

    # Sensitive Data Exposure
    # let's expose .git? or the exception one does this too, or really most of the others

    # XXE
    # TODO may be worth rewriting this one to deal with django's model [de]serialization
    # keep the examples more cohesive?
    url(r'^xxe/?$', TemplateView.as_view(template_name='vulnerable/xxe.html'), name='xxe'),
    url(r'^xlsx-info/?$', challenges.xxe, name='xlsx-info'),


    # Security Misconfiguration
    # FIXME boring example
    # maybe turn on directory listings? but then I'd need a real server on this thing
    url(r'^misconfiguration/?$',
        TemplateView.as_view(template_name='vulnerable/misconfiguration.html'),
        name='misconfiguration'),
    url(r'^exception/?$', challenges.exception, name='exception'),

    # XSS
    # just using external

    # Insecure Deserialization
    url(r'^restore-backup/?$',
        TemplateView.as_view(template_name='vulnerable/restore-backup.html'),
        name='restore-backup'),
    url(r'^profile/(?P<username>.*)/?$', challenges.serialize_user, name='serialize-user'),
    url(r'^deserialize/?$', challenges.deserialize_user, name='deserialize-user'),
] + staticfiles_urlpatterns()
