try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()

def get_current_captcha():
    return getattr(_thread_locals, 'captcha', None)

class CaptchaMiddleware(object):
    def process_request(self, request):
        captcha = None
        session = getattr(request, 'session', None)
        if session: captcha = session.get('captcha')
        _thread_locals.captcha = captcha
