from django.http import HttpResponse
from django.views import View
from django.shortcuts import get_object_or_404
from .models import Excerpts


class ExcerptsView(View):
    def get(self, request, xml_id, render_style, *args, **kwargs):
        print("You are here!")
        record = get_object_or_404(Excerpts, xml_id=xml_id)

        # Generate dynamic content based on link_type
        if render_style == "tei":
            # TODO: render correctly with xslt
            content = f"{record.xml_content}"
        else:
            content = f"{record.xml_content}"

        return HttpResponse(content)
