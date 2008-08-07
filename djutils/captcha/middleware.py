from djutils.middleware.threadlocals import _thread_locals

def get_current_captcha():
    return getattr(_thread_locals, 'captcha', None)

class CaptchaMiddleware(object):
    def process_request(self, request):
        captcha = None
        session = getattr(request, 'session', None)
        if session: captcha = session.get('captcha')
        _thread_locals.captcha = captcha
