from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder 

__all__ = ['JsonResponse', 'XmlResponse', 'YamlResponse']

class SerializedResponse(HttpResponse):
    def __init__(self, object):
        content = self._serialize(self.format, object)
        mimetype = getattr(self, 'mimetype', 'application/%s' % self.format)
        super(SerializedResponse, self).__init__(content, mimetype)
        
    def _serialize(self, object):
        return serialize(self.format, object)

class JsonResponse(SerializedResponse):
    format = 'json'

    def _serialize(self, object):
        if isinstance(object, QuerySet):
            return super(JsonResponse, self)._serialize(object)
        return simplejson.dumps(object, cls=DjangoJSONEncoder)

class XmlResponse(SerializedResponse):
    format = 'xml'

class YamlResponse(SerializedResponse):
    format = 'yaml'
    mimetype = 'application/x-yaml'
