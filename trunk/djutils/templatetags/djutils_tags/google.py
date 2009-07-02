from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import Library

register = Library()

def urchin():
    if not getattr(settings, 'GOOGLE_ANALYTICS_KEY'):
        raise ImproperlyConfigured, 'GOOGLE_ANALYTICS_KEY setting is required'
    return """<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%%3E%%3C/script%%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("%s");
pageTracker._trackPageview();
} catch(err) {}</script>""" % settings.GOOGLE_ANALYTICS_KEY

register.simple_tag(urchin)
