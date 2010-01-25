'''
From http://www.djangosnippets.org/snippets/1104/

These field and widget are util for to those fields where you can put a star and end values.

It supports most of field types and widgets (tested with IntegerField, CharField and DateField / TextInput and a customized DateInput).

Example of use::

    class FormSearch(forms.Form):
        q = forms.CharField(max_length=50, label=_('Search for'))
        price_range = RangeField(forms.IntegerField, required=False)

Example of use (with forced widget)::

    class FormSearch(forms.Form):
        q = forms.CharField(max_length=50, label=_('Search for'))
        price_range = RangeField(forms.IntegerField, widget=MyWidget)
'''

from django import forms
from django.template.loader import render_to_string
from django.forms.fields import EMPTY_VALUES
from django.utils.translation import ugettext as _

class RangeWidget(forms.MultiWidget):
    def __init__(self, widget, *args, **kwargs):
        widgets = (widget, widget)
        super(RangeWidget, self).__init__(widgets=widgets, *args, **kwargs)

    def decompress(self, value):
        return value

    def format_output(self, rendered_widgets):
        widget_context = {
            'min': rendered_widgets[0], 
            'max': rendered_widgets[1],
        }
        return render_to_string('widgets/range_widget.html', widget_context)

class RangeField(forms.MultiValueField):
    default_error_messages = {
        'invalid_start': _(u'Enter a valid start value.'),
        'invalid_end': _(u'Enter a valid end value.'),
    }

    def __init__(self, field_class, widget=forms.TextInput, *args, **kwargs):
        if not 'initial' in kwargs:
            kwargs['initial'] = ['', '']

        fields = (field_class(), field_class())

        super(RangeField, self).__init__(
            fields=fields,
            widget=RangeWidget(widget),
            *args, **kwargs
        )

    def compress(self, data_list):
        if data_list:
            return [
                self.fields[0].clean(data_list[0]), 
                self.fields[1].clean(data_list[1])
            ]
        return None
