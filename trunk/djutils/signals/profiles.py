from django.conf import settings
from django.db.models import get_model
from django.core.exceptions import ImproperlyConfigured

if not hasattr(settings, 'AUTH_PROFILE_MODULE'):
    raise ImproperlyConfigured

def create_profile(sender, instance, signal, *args, **kwargs):
    Profile = get_model(*settings.AUTH_PROFILE_MODULE)
    if kwargs.get('created'):
        try:
            instance.get_profile()
        except Profile.DoesNotExist:
            profile = Profile(user=instance)
            profile.save()
