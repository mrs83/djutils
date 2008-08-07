from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import Library

register = Library()

def urchin():
    if not getattr(settings, 'GOOGLE_ANALYTICS_KEY'):
        raise ImproperlyConfigured, 'GOOGLE_ANALYTICS_KEY setting is required'
    return """
<script src="http://www.google-analytics.com/urchin.js" type="text/javascript">
</script>
<script type="text/javascript">
_uacct = "%s";
urchinTracker();
</script>
""" % settings.GOOGLE_ANALYTICS_KEY

register.simple_tag(urchin)
