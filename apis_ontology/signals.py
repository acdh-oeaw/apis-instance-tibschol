import os
from django.contrib.auth.signals import user_logged_in
from django.db.models.base import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.db.models.signals import pre_delete
from apis_core.apis_entities.models import RootObject
from apis_core.relations.models import Relation

from apis_ontology.models import Person, PersonTranslation
from parler.signals import post_translation_save
from django.dispatch import receiver
import pyewts

converter = pyewts.pyewts()
TIBETAN = "es"


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


@receiver(post_save, sender=Person)
def fill_missing_translations(sender, instance, created, **kwargs):

    if not created:
        # Only add translations when a new entity is created
        return

    current_language = instance.get_current_language()
    target_language = "en" if current_language == TIBETAN else TIBETAN

    # Assumption here is that  object is created at first in one language

    def generate_translation(base_instance, base_language, target_language):
        # Replace with your translation logic
        fields_with_translations = ["name"]
        translations = {}
        instance.set_current_language(current_language)

        for f in fields_with_translations:
            base_lang_val = getattr(base_instance, f)
            if target_language == TIBETAN:
                translations[f] = {
                    current_language: base_lang_val,
                    target_language: converter.toUnicode(base_lang_val),
                }
            else:
                translations[f] = {
                    current_language: base_lang_val,
                    target_language: converter.toWylie(base_lang_val),
                }

        return translations

    translations = generate_translation(instance, current_language, target_language)
    instance.set_current_language(target_language)
    for f, tr in translations.items():
        setattr(instance, f, tr[target_language])

    instance.save()


# post save signal to update translations for person.name
@receiver(post_save, sender=Person)
def update_person_translations(sender, instance, **kwargs):
    pass
    # TODO: Depending on which language is used while creating objects
    # we should create the translation object using pyewts
    # if instance.name:
    #     PersonTranslation.objects.update_or_create(
    #         master=instance,
    #         language_code="bo",
    #         defaults={"name": instance.name},
    #     )
