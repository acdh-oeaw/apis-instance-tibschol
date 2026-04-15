from django.db.models.signals import post_save
from apis_ontology.models import Person, Place, Work, Instance
from apis_ontology.utils import latin_to_tibetan

# Helper to determine if transliteration should be updated
def get_tibetan_transliteration(obj):
    # Work: only if original_language == 'Tibetan'
    if hasattr(obj, 'original_language'):
        if getattr(obj, 'original_language', None) == 'Tibetan' and getattr(obj, 'name', None):
            return latin_to_tibetan(obj.name)
        return ''
    # Instance: only if it is an instance of a work whose language is Tibetan
    if obj.__class__.__name__ == 'Instance':
        from apis_ontology.models import WorkHasAsAnInstanceInstance, Work
        rel = WorkHasAsAnInstanceInstance.objects.filter(obj_object_id=obj.pk).first()
        work = Work.objects.filter(pk=rel.subj_object_id).first() if rel else None
        if work and work.original_language == 'Tibetan' and getattr(obj, 'name', None):
            return latin_to_tibetan(obj.name)
        return ''
    # Person: only if nationality == 'Tibetan'
    if hasattr(obj, 'nationality'):
        if getattr(obj, 'nationality', None) == 'Tibetan' and getattr(obj, 'name', None):
            return latin_to_tibetan(obj.name)
        return ''
    # Place: always transliterate label
    if hasattr(obj, 'label') and getattr(obj, 'label', None):
        return latin_to_tibetan(obj.label)
    return ''


from django.db import transaction

def update_transliteration(sender, instance, **kwargs):
    # If the instance was just created, always set transliteration
    if kwargs.get('created', False):
        new_translit = get_tibetan_transliteration(instance)
        if instance.tibetan_transliteration != new_translit:
            instance.tibetan_transliteration = new_translit
            instance.save(update_fields=['tibetan_transliteration'])
        return

    # For updates, only auto-update if the field was not changed by the user
    # This requires checking the previous value in the DB
    model = type(instance)
    try:
        old = model.objects.get(pk=instance.pk)
    except model.DoesNotExist:
        old = None


    # If the transliteration field was changed by the user, always persist it as-is (do nothing)
    if old and old.tibetan_transliteration != instance.tibetan_transliteration:
        # User changed the field, so just persist their value and do not auto-update
        return

    # Otherwise, update if needed
    new_translit = get_tibetan_transliteration(instance)
    if instance.tibetan_transliteration != new_translit:
        # Use transaction.on_commit to avoid recursion
        def do_update():
            model.objects.filter(pk=instance.pk).update(tibetan_transliteration=new_translit)
        transaction.on_commit(do_update)

for model in [Person, Place, Work, Instance]:
    post_save.connect(update_transliteration, sender=model)
import os
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.db.models.signals import pre_delete
from apis_core.apis_entities.models import RootObject
from apis_core.relations.models import Relation


@receiver(user_logged_in)
def add_to_group(sender, user, request, **kwargs):
    user_list = os.environ.get("AUTH_LDAP_USER_LIST", "").split(",")
    g1, _ = Group.objects.get_or_create(name="redaktion")
    if user.username in user_list:
        g1.user_set.add(user)


@receiver(pre_delete, sender=RootObject)
def cascade_delete_related(sender, instance, **kwargs):
    Relation.objects.filter(subj_object_id=instance.pk).delete()
    Relation.objects.filter(obj_object_id=instance.pk).delete()
