import base64

try:
    import cPickle as pickle
except ImportError:
    import pickle

from django.db import models

class PickleDescriptor(property):
    def __init__(self, field):
        self.field = field

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if self.field.name not in instance.__dict__:
            # The object hasn't been created yet so unpickle the data
            raw_data = getattr(instance, self.field.attname)
            value = self.field.unpickle(base64.b64decode(raw_data))
            instance.__dict__[self.field.name] = value

        return instance.__dict__[self.field.name]

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = value
        pickled = base64.b64encode(self.field.pickle(value))
        setattr(instance, self.field.attname, pickled)

class PickleField(models.TextField):
    def pickle(self, obj):
        return pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)

    def unpickle(self, data):
        return pickle.loads(data)

    def get_attname(self):
        return '%s_pickled' % self.name

    def get_db_prep_lookup(self, lookup_type, value):
        raise ValueError("Can't make comparisons against pickled data.")

    def contribute_to_class(self, cls, name):
        super(PickleField, self).contribute_to_class(cls, name)
        setattr(cls, name, PickleDescriptor(self))
