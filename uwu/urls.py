# TODO they're not really challenges, maybe call em examples...
from django.conf.urls import url
# from django.urls import path
from django.views.generic.base import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import uwu.vulnerable.views as challenges


urlpatterns = [
    # TODO an index that links to exercises and slides separately
    url(r'^$', TemplateView.as_view(template_name='index.html'), name="home"),

    # Broken Auth

    # Sensitive Data Exposure

    # XXE
    # TODO may be worth rewriting this one to deal with django's model [de]serialization
    # keep the examples more cohesive?
    url(r'^xxe/?$', TemplateView.as_view(template_name='vulnerable/xxe.html'), name='xxe'),
    url(r'^xlsx-info/?$', challenges.xxe, name='xlsx-info'),

    # Broken Access Control
    url(r'^broken-access-control/?$',
        TemplateView.as_view(template_name='vulnerable/broken-access-control.html'),
        name='broken-access-control'),

    # Security Misconfiguration
    # FIXME boring example
    url(r'^misconfiguration/?$',
        TemplateView.as_view(template_name='vulnerable/misconfiguration.html'),
        name='misconfiguration'),
    url(r'^exception/?$', challenges.exception, name='exception'),

    # Injection
    url(r'^shell-injection/?$',
        TemplateView.as_view(template_name='vulnerable/shell-injection.html'),
        name='shell-injection'),
    url(r'^injection1/?$', challenges.injection1, name='injection1'),
    url(r'^injection2/?$', challenges.injection2, name='injection2'),

    url(r'^sql-injection/?$',
        TemplateView.as_view(template_name='vulnerable/sql-injection.html'),
        name='sql-injection'),

    # XSS
    url(r'^hello-xss/?(?P<name>.*)?/?$', challenges.reflected_xss, name='xss1'),
    # other exercises external; I don't see any point writing worse examples than exist

    # Insecure Deserialization
    url(r'^insecure-deserialization/?$',
        TemplateView.as_view(template_name='vulnerable/insecure-deserialization.html'),
        name='insecure-deserialization'),
    url(r'^serialize/?$', challenges.serialize_user,
        name='serialize-user'),
    url(r'^deserialize/?$', challenges.insecure_deserialization,
        name='deserialize-user'),
] + staticfiles_urlpatterns()
