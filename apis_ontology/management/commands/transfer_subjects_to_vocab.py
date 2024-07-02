from django.core.management.base import BaseCommand

from apis_ontology.models import Subject, Work
import re

DELIMITERS = [",", ";", "+", "/"]
PATTERN = "|".join(map(re.escape, DELIMITERS))


class Command(BaseCommand):
    help = "Populate subject vocabulary from works and apply it to Works"

    def handle(self, *args, **options):
        def split_subjects(old_subject_field):
            return [
                si.strip().capitalize() for si in re.split(PATTERN, old_subject_field)
            ]

        for w in Work.objects.all():
            if w.subject:
                subject_list = split_subjects(w.subject)
                for si in subject_list:
                    new_sub, _ = Subject.objects.get_or_create(name=si)
                    w.skip_history_when_saving = True
                    w.subject_vocab.add(new_sub)

        self.stdout.write(
            self.style.SUCCESS(
                f"Subject vocabulary now contains {len(Subject.objects.all())} subjects."
            )
        )
