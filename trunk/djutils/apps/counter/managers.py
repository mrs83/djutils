from django.db import models, connection
from django.contrib.contenttypes.models import ContentType

class ObjectCounterManager(models.Manager):
    def count_object(self, obj, user=None):
        counter = self.model()
        counter.content_object = obj
        if user: counter.user = user
        counter.save()

    def most_visited_for_model(self, model, num=10):
        '''Inspired by http://www.djangosnippets.org/snippets/108/''' 
        content_type = ContentType.objects.get_for_model(model)
        primary_table = model._meta.db_table
        secondary_table = self.model()._meta.db_table
        query = """
        SELECT p.id AS obj_id, COUNT(*) AS score
        FROM %s p 
        INNER JOIN %s s ON (p.id = s.object_id) 
        WHERE s.content_type_id = %%s 
        GROUP BY obj_id 
        ORDER BY score DESC
        """ % (primary_table, secondary_table)
        cursor = connection.cursor()
        cursor.execute(query, [content_type.id])
        object_ids = [row[0] for row in cursor.fetchall()[:num]]
        object_dict = model._default_manager.in_bulk(object_ids)
        return [object_dict[object_id] for object_id in object_ids]
