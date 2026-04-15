from django.core.management.base import BaseCommand
from apis_ontology.models import Person, Place, Instance, Work
from apis_ontology.utils import latin_to_tibetan

class Command(BaseCommand):
    help = 'Transliterates the name or label of Person, Place, Instance, and Work to Tibetan in the tibetan_transliteration field, with logic for language/nationality.'

    def handle(self, *args, **options):
        updated = 0

        # Work: only if original_language == 'Tibetan'
        for obj in Work.objects.all():
            value = getattr(obj, 'name', None)
            if obj.original_language == 'Tibetan' and value:
                tibetan = latin_to_tibetan(value)
            else:
                tibetan = ''
            if getattr(obj, 'tibetan_transliteration', None) != tibetan:
                obj.tibetan_transliteration = tibetan
                obj.save(update_fields=['tibetan_transliteration'])
                updated += 1
                self.stdout.write(f"Updated Work id={obj.pk}")

        # Instance: only if it is an instance of a work whose language is Tibetan
        from apis_ontology.models import WorkHasAsAnInstanceInstance
        work_instance_map = {}
        for rel in WorkHasAsAnInstanceInstance.objects.all():
            work_instance_map[rel.obj_object_id] = rel.subj_object_id

        for obj in Instance.objects.all():
            value = getattr(obj, 'name', None)
            work_id = work_instance_map.get(obj.id)
            work = Work.objects.filter(id=work_id).first() if work_id else None
            if work and work.original_language == 'Tibetan' and value:
                tibetan = latin_to_tibetan(value)
            else:
                tibetan = ''
            if getattr(obj, 'tibetan_transliteration', None) != tibetan:
                obj.tibetan_transliteration = tibetan
                obj.save(update_fields=['tibetan_transliteration'])
                updated += 1
                self.stdout.write(f"Updated Instance id={obj.pk}")

        # Person: only if nationality == 'Tibetan'
        for obj in Person.objects.all():
            value = getattr(obj, 'name', None)
            if obj.nationality == 'Tibetan' and value:
                tibetan = latin_to_tibetan(value)
            else:
                tibetan = ''
            if getattr(obj, 'tibetan_transliteration', None) != tibetan:
                obj.tibetan_transliteration = tibetan
                obj.save(update_fields=['tibetan_transliteration'])
                updated += 1
                self.stdout.write(f"Updated Person id={obj.pk}")

        # Place: always transliterate label
        for obj in Place.objects.all():
            value = getattr(obj, 'label', None)
            if value:
                tibetan = latin_to_tibetan(value)
            else:
                tibetan = ''
            if getattr(obj, 'tibetan_transliteration', None) != tibetan:
                obj.tibetan_transliteration = tibetan
                obj.save(update_fields=['tibetan_transliteration'])
                updated += 1
                self.stdout.write(f"Updated Place id={obj.pk}")

        self.stdout.write(self.style.SUCCESS(f"Transliteration complete. {updated} objects updated."))
