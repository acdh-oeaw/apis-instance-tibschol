import pyewts
from django.core.management.base import BaseCommand
from tqdm.auto import tqdm
from apis_ontology.models import Person
from tqdm.auto import tqdm

TIBETAN = "es"


class Command(BaseCommand):
    help = "add Tibetan transliterations for Person - names"

    def handle(self, *args, **options):
        converter = pyewts.pyewts()

        for p in tqdm(Person.objects.all()):
            tibetan_name = converter.toUnicode(p.name_latin)
            p.set_current_language(TIBETAN)
            p.name = tibetan_name
            p.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"{len(Person.objects.all())} names were successfully transliterated into Tibetan."
            )
        )
