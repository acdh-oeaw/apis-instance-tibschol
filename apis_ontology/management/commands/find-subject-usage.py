from django.core.management.base import BaseCommand
from apis_ontology.models import Subject, TibScholRelationMixin, TibScholEntityMixin


class Command(BaseCommand):
    help = "Get a list entities and subjects that have a FK to a particular subject"

    def add_arguments(self, parser):
        parser.add_argument(
            "subject_ids", nargs="+", type=int, help="list of subject IDs"
        )

    def handle(self, *args, **kwargs):
        subject_ids = kwargs["subject_ids"]
        if not subject_ids:
            print("No subject IDs to investigate")

        models = [
            m
            for m in (
                TibScholRelationMixin.__subclasses__()
                + TibScholEntityMixin.__subclasses__()
            )
            if hasattr(m, "subject_vocab") or hasattr(m, "subject_of_teaching_vocab")
        ]
        for subject_id in subject_ids:
            try:
                subject = Subject.objects.get(id=subject_id)
                print(f"Subject: {subject_id}, {subject}")
                for m in models:
                    field_name = (
                        "subject_vocab"
                        if hasattr(m, "subject_vocab")
                        else "subject_of_teaching_vocab"
                    )
                    # find instances of models that have subject in the "field_name" field
                    instances = m.objects.filter(**{field_name: subject})
                    for instance in instances:
                        print("\t", instance.pk, type(instance), instance)
            except Subject.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Cannot find subject with ID - {subject_id}")
                )
