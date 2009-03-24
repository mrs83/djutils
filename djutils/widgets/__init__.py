"""
From sorl-curator project (http://code.google.com/p/sorl-curator/)
"""
import os

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

class AdminFileWidget(forms.FileInput):
    """
    A FileField Widget that shows its current value if it has one.
    """
    def __init__(self, attrs={}):
        super(AdminFileWidget, self).__init__(attrs)
        
    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "url"):
            output.append('%s <a target="_blank" href="%s">%s</a> <br />%s ' %
                (_('Currently:'), value.url, os.path.basename(value.path), _('Change:')))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))

class AdminImageWidget(forms.FileInput):
    """
    An ImageField Widget that shows its current image if it has one.
    """
    def __init__(self, attrs={}):
        super(AdminImageWidget, self).__init__(attrs)
        
    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "url"):
            try:
                from sorl.thumbnail.main import DjangoThumbnail
                thumb = '<img src="%s">' % DjangoThumbnail(value.name, (100,100), ['crop']).absolute_url
            except:
                # just act like a normal file
                output.append('%s <a target="_blank" href="%s">%s</a> <br />%s ' %
                    (_('Currently:'), value.url, os.path.basename(value.path), _('Change:')))
            else:
                output.append('<a class="thumb" target="_blank" href="%s">%s</a> <br />%s ' %
                    (value.url, thumb, _('Change:')))
        output.append(super(AdminImageWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))
