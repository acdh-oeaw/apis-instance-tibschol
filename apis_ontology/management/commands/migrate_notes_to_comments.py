import logging
import pandas as pd
from django.core.management.base import BaseCommand
from apis_ontology.models import Person, Place, Work, Instance

logger = logging.getLogger(__name__)
pd.set_option("display.max_colwidth", None)


class Command(BaseCommand):
    """
    Migrates values from Legacy Notes field to Comments
    for Person, Place, Instance and Work objects
    """

    def handle(self, *args, **kwargs):
        """
        copies values from Notes to Comments
        """

        def copy_to_comments(obj):
            if not obj.notes:
                return

            logging.debug("Copying notes for obj [%s]: %s", obj.pk, obj.notes)

            if not obj.comments:
                obj.comments = ""
            else:
                obj.comments += "\n"
                logging.debug("Existing comments: %s", obj.comments)

            obj.comments += obj.notes
            obj.notes = ""
            obj.save()
            logging.debug("Saved obj %s", obj.pk)

        for obj in Person.objects.all():
            copy_to_comments(obj)

        for obj in Place.objects.all():
            copy_to_comments(obj)

        for obj in Work.objects.all():
            copy_to_comments(obj)

        for obj in Instance.objects.all():
            copy_to_comments(obj)
