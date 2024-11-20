from django.contrib import admin
from parler.admin import TranslatableAdmin

from .models import Person


@admin.register(Person)
class PersonAdmin(TranslatableAdmin):
    # TODO: allow editing the translations here?
    list_display = ["name", "all_languages_column"]
    pass
