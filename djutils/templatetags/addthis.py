from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import Site

register = template.Library()

def add_this(title, url):
    if not hasattr(settings, 'ADD_THIS_USERNAME'):
        raise ImproperlyConfigured, 'You need to set ADD_THIS_USERNAME '\
                                    'into your own settings.py file'
    username = settings.ADD_THIS_USERNAME
    site = Site.objects.get_current()
    return {'title': title, 'url': url, 'username': username, 'site': site}

register.inclusion_tag('tags/add_this.html')(add_this)
