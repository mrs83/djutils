"""
From http://www.djangosnippets.org/snippets/382/
"""

from django.db import transaction
from django.db.models import get_models
from django.contrib.contenttypes.generic import GenericForeignKey

@transaction.commit_manually
def merge_model_objects(primary_object, *alias_objects):
    """
    Use this function to merge model objects (i.e. Users, Organizations, Polls, Etc.) and migrate all of the related fields from the alias objects the primary object.
    
    Usage:
    from django.contrib.auth.models import User
    primary_user = User.objects.get(email='good_email@example.com')
    duplicate_user = User.objects.get(email='good_email+duplicate@example.com')
    merge_model_objects(primary_user, duplicate_user)
    """
    # Get a list of all GenericForeignKeys in all models
    # TODO: this is a bit of a hack, since the generics framework should provide a similar
    # method to the ForeignKey field for accessing the generic related fields.
    generic_fields = []
    for model in get_models():
        for field_name, field in filter(lambda x: isinstance(x[1], GenericForeignKey), model.__dict__.iteritems()):
            generic_fields.append(field)
    
    # Loop through all alias objects and migrate their data to the primary object.
    for alias_object in alias_objects:
        try:
            # Migrate all foreign key references from alias object to primary object.
            for related_object in alias_object._meta.get_all_related_objects():
                # The variable name on the alias_object model.
                alias_varname = related_object.get_accessor_name()
                # The variable name on the related model.
                obj_varname = related_object.field.name
                related_objects = getattr(alias_object, alias_varname)
                for obj in related_objects.all():
                    try:
                        setattr(obj, obj_varname, primary_object)
                        obj.save()
                    except Exception, e:
                        print 'Exception: %s' % str(e)
                        while True:
                            user_response = raw_input("Do you wish to continue the migration of this object (y/[n])? ")
                            if user_response == '' or user_response == 'n':
                                raise Exception('User Aborted Merge.')
                            elif user_response == 'y':
                                break
                            else:
                                print "Error: you must choose 'y' or 'n'."
                        print ""

            # Migrate all many to many references from alias object to primary object.
            for related_many_object in alias_object._meta.get_all_related_many_to_many_objects():
                alias_varname = related_many_object.get_accessor_name()
                obj_varname = related_many_object.field.name
                related_many_objects = getattr(alias_object, alias_varname)
                for obj in related_many_objects.all():
                    try:
                        getattr(obj, obj_varname).remove(alias_object)
                        getattr(obj, obj_varname).add(primary_object)
                    except:
                        print 'Exception: %s' % str(e)
                        while True:
                            user_response = raw_input("Do you wish to continue the migration of this object (y/[n])? ")
                            if user_response == '' or user_response == 'n':
                                raise Exception('User Aborted Merge.')
                            elif user_response == 'y':
                                break
                            else:
                                print "Error: you must choose 'y' or 'n'."
                        print ""

            # Migrate all generic foreign key references from alias object to primary object.
            for field in generic_fields:
                filter_kwargs = {}
                filter_kwargs[field.fk_field] = alias_object._get_pk_val()
                filter_kwargs[field.ct_field] = field.get_content_type(alias_object)
                for generic_related_object in field.model.objects.filter(**filter_kwargs):
                    setattr(generic_related_object, field.name, primary_object)
                    generic_related_object.save()
            
            while True:
                user_response = raw_input("Do you wish to keep, delete, or abort the object (%s) %s (k/d/a)? " % (alias_object._get_pk_val(), str(alias_object)))
                if user_response == 'a':
                    raise Exception('User Aborted Merge.')
                elif user_response == 'd':
                    alias_object.delete()
                    break
                elif user_response == 'k':
                    break
                else:
                    print "Error: you must enter a valid value (k, d, a)."
        except:
            transaction.rollback()
        else:
            transaction.commit()
    return primary_object
