from django.core.management.base import BaseCommand
from apis_ontology.models import TibScholRelationMixin
from tqdm.auto import tqdm
import re
from pprint import pprint


class Command(BaseCommand):
    help = "Get a list of TEI Refs in use in APIS"

    def handle(self, *args, **options):
        def get_tei_id(xml_id):
            true_id = xml_id.replace('"', "").replace("xml:id=", "").strip().rstrip(".")
            return true_id

        def get_all_tei_ids(value):
            lines = value.split("\n")
            tei_ids = []
            for l in lines:
                words = l.split()
                for w in words:
                    if w.startswith("xml:id=") or bool(re.search(r"\bex\d\w*", w)):
                        tei_ids.append(get_tei_id(w))
            return tei_ids

        models = TibScholRelationMixin.__subclasses__()
        unique_refs = []
        for m in tqdm(models):
            if not hasattr(m, "tei_refs"):
                break
            for obj in m.objects.all():
                if obj.tei_refs:
                    unique_refs.extend(get_all_tei_ids(obj.tei_refs))

        unique_refs = set(list(unique_refs))
        pprint(unique_refs)

        self.stdout.write(self.style.SUCCESS("Done."))
