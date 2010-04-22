import Captcha
import cStringIO
from Captcha.Visual.Tests import PseudoGimpy

from django.http import HttpResponse

def captcha(request):
    '''
    Visualizza un immagine captcha utilizzando PyCaptcha
    '''
    g = PseudoGimpy()
    s = cStringIO.StringIO()
    i = g.render()
    i.save(s, 'JPEG')
    request.session['captcha'] = g.solutions[0]
    return HttpResponse(s.getvalue(), 'image/jpeg')
