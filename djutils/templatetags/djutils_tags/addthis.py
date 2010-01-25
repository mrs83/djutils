from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

register = template.Library()

def add_this(title, url):
    if not hasattr(settings, 'ADD_THIS_USERNAME'):
        raise ImproperlyConfigured, 'You need to set ADD_THIS_USERNAME '\
                                    'into your own settings.py file'
    return {'url': url, 'title': title, 'username': username}

register.inclusion_tag('tags/add_this.html')(add_this)
