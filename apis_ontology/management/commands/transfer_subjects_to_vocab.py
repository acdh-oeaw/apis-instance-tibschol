from django.core.management.base import BaseCommand

from apis_ontology.models import Subject, Work
import re
from tqdm.auto import tqdm
from django.apps import apps

DELIMITERS = [",", ";", "+", "/"]
PATTERN = "|".join(map(re.escape, DELIMITERS))


class Command(BaseCommand):
    help = "Populate subject vocabulary from works and apply it to Works"

    def handle(self, *args, **options):
        def split_subjects(old_subject_field):
            return [
                si.strip().capitalize() for si in re.split(PATTERN, old_subject_field)
            ]

        for w in tqdm(Work.objects.all()):
            if w.subject:
                subject_list = split_subjects(w.subject)
                for si in subject_list:
                    new_sub, _ = Subject.objects.get_or_create(name=si)
                    w.skip_history_when_saving = True
                    w.subject_vocab.add(new_sub)

        rels_updated = 0
        relation_models = [
            "PersonDirectPredecessorInLineageOfPerson",
            "PersonDiscipleOfPerson",
            "PersonRefersWithNameToTheViewsOfPerson",
            "PersonRefersWithoutNameToTheViewsOfPerson",
            "PersonRequestorOfPerson",
            "PersonStudentOfPerson",
        ]
        for rel_model in relation_models:
            model_class = apps.get_model("apis_ontology", rel_model)
            for rel in model_class.objects.all():
                if hasattr(rel, "subject_of_teaching"):
                    if rel.subject_of_teaching:
                        subject_list = split_subjects(rel.subject_of_teaching)
                        for si in subject_list:
                            new_sub, _ = Subject.objects.get_or_create(name=si)
                            rel.skip_history_when_saving = True
                            rel.subject_of_teaching_vocab.add(new_sub)
                            rels_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Subject vocabulary now contains {len(Subject.objects.all())} subjects."
            )
        )
        print(f"{rels_updated} relations were updated with subject as a vocabulary")
