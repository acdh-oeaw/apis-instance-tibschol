from apis_core.apis_entities.filtersets import AbstractEntityFilterSet
from django.db import models
import django_filters


class LegacyStuffMixinFilterSet(AbstractEntityFilterSet):
    class Meta(AbstractEntityFilterSet.Meta):
        filter_overrides = {
            models.CharField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
            models.TextField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
        }


class TibScholEntityMixinFilterSet(AbstractEntityFilterSet):
    class Meta(AbstractEntityFilterSet.Meta):
        filter_overrides = {
            models.TextField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
        }


class InstanceMixinFilterSet(AbstractEntityFilterSet):
    class Meta(AbstractEntityFilterSet.Meta):
        filter_overrides = {
            models.TextField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
        }
