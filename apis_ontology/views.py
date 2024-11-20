from django.shortcuts import redirect
from django.utils.translation import activate
from django.http import HttpResponse
from django.views import View
from django.shortcuts import get_object_or_404
from .models import Excerpts
import parler


class ExcerptsView(View):
    def get(self, request, xml_id, render_style, *args, **kwargs):
        record = get_object_or_404(Excerpts, xml_id=xml_id)

        return HttpResponse(record.xml_content)
