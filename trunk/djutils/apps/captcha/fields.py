from django import forms
from django.newforms.util import flatatt
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from djutils.apps.captcha.middleware import get_current_captcha

CAPTCHA_IMAGE = """
<div class="captcha">
<img src="%s" alt="captcha" />
</div>
"""

class CaptchaWidget(forms.TextInput):
    def render(self, name, value, attrs=None):
        captcha_url = reverse('captcha')
        image = CAPTCHA_IMAGE % captcha_url
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        attrs = flatatt(final_attrs)
        if value != '':
            final_attrs['value'] = force_unicode(value)
        return mark_safe(u'%s<input%s />' % (image, attrs))

class CaptchaField(forms.CharField):
    widget = CaptchaWidget

    def clean(self, value):
        captcha = get_current_captcha()
        if not captcha:
            raise forms.ValidationError(_('You must enable cookies.'))
        if value != captcha:
            raise forms.ValidationError(_('Incorrect! Try again.'))
        return value
