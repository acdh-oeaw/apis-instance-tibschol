from collections import defaultdict
from django.core.management.base import BaseCommand
from apis_ontology.models import TibScholRelationMixin
from tqdm.auto import tqdm
import re
from pprint import pprint
from apis_ontology.models import Excerpts
from datetime import datetime


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
        unique_refs = defaultdict(list)
        for m in tqdm(models):
            model_name = str(m).split("'")[1].split(".")[-1]
            if not hasattr(m, "tei_refs"):
                break
            for rel in m.objects.all():
                if rel.tei_refs:
                    all_tei_refs = get_all_tei_ids(rel.tei_refs)
                    for ref in all_tei_refs:
                        unique_refs[ref].append(
                            f"{rel.pk}|{model_name}|{rel.subj.pk}|{rel.obj.pk}"
                        )

        missing_refs = []
        for ref in unique_refs.keys():
            try:
                Excerpts.objects.get(xml_id=ref)
            except Excerpts.DoesNotExist as e:
                for support in unique_refs[ref]:
                    missing_refs.append(f"|{ref}|{support}|")

        with open(f"missing_refs_{datetime.now():%Y%m%d_%H%M%S}.md", "w") as f:
            f.writelines(
                "|TEI ID|RELATION PK|Relation|Subject PK|Object PK|\n|--|--|--|--|--|\n"
            )
            f.writelines("\n".join(missing_refs))

        self.stdout.write(self.style.SUCCESS("Done."))
