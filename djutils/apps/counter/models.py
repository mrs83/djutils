from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from djutils.apps.counter.managers import ObjectCounterManager

class ObjectCounter(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    visited = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, blank=True, null=True)
  
    objects = ObjectCounterManager()

    def __unicode__(self):
        return u'%s: %d' % (self.content_type.name, self.object_id)
