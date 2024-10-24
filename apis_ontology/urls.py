from apis_ontology.views import ExcerptsView
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from apis_core.apis_entities.api_views import GetEntityGeneric


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
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += [
    path("", include("django_acdhch_functions.urls")),
]

urlpatterns += [
    path("select2/", include("django_select2.urls")),
]
