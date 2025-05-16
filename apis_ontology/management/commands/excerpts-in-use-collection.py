from apis_ontology.models import Excerpts, TibScholRelationMixin

from django.core.management.base import BaseCommand
from apis_core.collections.models import SkosCollection
from tqdm import tqdm


class Command(BaseCommand):
    """
    Checks which excerpts are used as references
    in relations and adds them to excerpts-in-use collection
    """

    def handle(self, *args, **options):
        excerpt_collection, _ = SkosCollection.objects.get_or_create(
            name="excerpts-in-use"
        )

        for excerpt in tqdm(Excerpts.objects.all()):
            # check in xml_id is present in the tei_refs column
            # of Relation or in any of its subclasses at least once
            in_use = False
            for rel_subclass in TibScholRelationMixin.__subclasses__():
                if rel_subclass.objects.filter(
                    tei_refs__contains=excerpt.xml_id
                ).exists():
                    excerpt_collection.add(excerpt)
                    in_use = True
                    break
            if not in_use:
                try:
                    excerpt_collection.remove(excerpt)
                except Exception as e:
                    pass
        self.stdout.write(
            self.style.SUCCESS(
                "Excerpts used as references have been successfully added to experts-in-use collection."
            )
        )
