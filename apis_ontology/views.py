from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from .models import Excerpts, Instance


class ExcerptsView(View):

    def get(self, request, xml_id, render_style, *args, **kwargs):
        def get_instances_from_tibschol_refs(tibschol_refs):
            instances = []
            for tibschol_ref in tibschol_refs.split("\n"):
                try:
                    instance = Instance.objects.get(
                        tibschol_ref__iregex=rf"(?m)(^|\W){tibschol_ref}(\W|$)"
                    )
                    instances.append(
                        f"<a href='{instance.get_absolute_url()}' target=_BLANK> {str(instance)} </a>"
                    )
                except Instance.DoesNotExist:
                    pass

            return list(set(instances))

        record = get_object_or_404(Excerpts, xml_id=xml_id)
        instances = get_instances_from_tibschol_refs(record.tibschol_refs)
        data = {
            "xml_content": record.xml_content,
            "xml_id": record.xml_id,
            "status": f"[{record.status}]" if record.status else "[unknown]",
            "tibschol_refs": record.tibschol_refs,
            "instances": ", ".join(instances),
        }

        return JsonResponse(data)  # Return the data as JSON response
