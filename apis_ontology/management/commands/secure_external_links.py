from django.core.management.base import BaseCommand
from django.db import connection

from apis_ontology.models import Person, Place, Work, Instance


class Command(BaseCommand):
    help = "Change http links in External links to https"

    def handle(self, *args, **options):
        def convert_to_https(qs, entity_type=""):
            for obj in qs:
                obj.external_links = obj.external_links.replace("http://", "https://")
                obj.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"{len(qs)} {entity_type if entity_type else 'entities'} updated"
                )
            )

        http_persons = Person.objects.filter(external_links__contains="http://")
        convert_to_https(http_persons, "persons")
        http_places = Place.objects.filter(external_links__contains="http://")
        convert_to_https(http_places, "places")
        http_works = Work.objects.filter(external_links__contains="http://")
        convert_to_https(http_works, "works")
        http_instances = Instance.objects.filter(external_links__contains="http://")
        convert_to_https(http_instances, "instances")