from django import newforms as forms
from django.newforms.util import flatatt
from django.utils.html import escape
from django.utils.encoding import force_unicode
from django.utils.simplejson import JSONEncoder
from django.core.urlresolvers import reverse, NoReverseMatch

class Autocomplete(forms.TextInput):
    def __init__(self, source, options={}, attrs={}):
        """
        source should be a list containing autocomplete values, an
        urlpattern name or full url to autocomplete view that will 
        be used for the XHR request.
        
        options are available at autocomplete sample page::
        http://jquery.bassistance.de/autocomplete/
        """
        
        self.options = None
        self.attrs = {'autocomplete': 'off'}
        self.source = source
        if len(options) > 0:
            self.options = JSONEncoder().encode(options)
        self.attrs.update(attrs)
    
    def render_js(self, field_id):
        if isinstance(self.source, list):
            source = JSONEncoder().encode(self.source)
        elif isinstance(self.source, basestring):
            try:
                source = reverse(self.source)
            except NoReverseMatch:
                source = escape(self.source)
            source = "'%s'" % source
        else:
            raise ValueError, source
        
        options = ''
        if self.options: options += ',%s' % self.options

        return u"$('#%s').autocomplete(%s%s);" % (field_id, source, options)

    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        if value:
            final_attrs['value'] = escape(force_unicode(value))

        if not self.attrs.has_key('id'):
            final_attrs['id'] = 'id_%s' % name
        
        return u'''<input type="text" %(attrs)s/>
        <script type="text/javascript"><!--//
        %(js)s//--></script>
        ''' % {
            'attrs' : flatatt(final_attrs),
            'js' : self.render_js(final_attrs['id']),
        }
