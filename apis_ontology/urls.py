from apis_ontology.views import DataModelView, ExcerptsView
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from apis_core.apis_entities.api_views import GetEntityGeneric
from django.conf import settings


urlpatterns = [
    path("admin/", admin.site.urls),
    path("apis/", include("apis_core.urls", namespace="apis")),
    path("apis/collections/", include("apis_core.collections.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("entity/<int:pk>/", GetEntityGeneric.as_view(), name="GetEntityGenericRoot"),
    path("", TemplateView.as_view(template_name="base.html")),
    path(
        "apis/excerpts/<str:xml_id>/<str:render_style>/",
        ExcerptsView.as_view(),
        name="excerpts_view",
    ),
    path(
        "apis/datamodel/",
        DataModelView.as_view(),
        name="datamodel",
    ),
]

urlpatterns += staticfiles_urlpatterns()

urlpatterns += [
    path("select2/", include("django_select2.urls")),
]

urlpatterns += [path("", include("django_interval.urls"))]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
