from django.core.management.base import BaseCommand
from tqdm.auto import tqdm
from django.contrib.contenttypes.models import ContentType
from apis_core.apis_metainfo.models import RootObject
from apis_ontology.models import TibScholRelationMixin


class Command(BaseCommand):
    help = "add subj and obj content type and object_id to relations"

    def handle(self, *args, **kwargs):
        for c in tqdm(TibScholRelationMixin.__subclasses__()):
            # set progress bar message with "Updating c"
            with tqdm(total=c.objects.all().count(), desc=f"Updating {c}") as pbar:
                for rel in c.objects.all():
                    rel.subj_object_id = rel.subj.pk
                    subj_content_type = ContentType.objects.get_for_model(
                        RootObject.objects_inheritance.get_subclass(pk=rel.subj.pk)
                    )
                    rel.subj_content_type = subj_content_type

                    rel.obj_object_id = rel.obj.pk
                    obj_content_type = ContentType.objects.get_for_model(
                        RootObject.objects_inheritance.get_subclass(pk=rel.obj.pk)
                    )
                    rel.obj_content_type = obj_content_type
                    rel.save()
                    pbar.update(1)
