from apis_ontology.views import ExcerptsView
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.i18n import i18n_patterns

from apis_core.apis_entities.api_views import GetEntityGeneric
from django.conf.urls.i18n import set_language

urlpatterns = [
    path("admin/", admin.site.urls),
]

# I18N patterns
urlpatterns += i18n_patterns(
    path("accounts/", include("django.contrib.auth.urls")),
    path("apis/", include("apis_core.urls")),
    path("apis/collections/", include("apis_core.collections.urls")),
    path("entity/<int:pk>/", GetEntityGeneric.as_view(), name="GetEntityGenericRoot"),
    path("", TemplateView.as_view(template_name="base.html")),
    path(
        "apis/excerpts/<str:xml_id>/<str:render_style>/",
        ExcerptsView.as_view(),
        name="excerpts_view",
    ),
    prefix_default_language=True,
)

# Static files and other patterns
urlpatterns += staticfiles_urlpatterns()

# Additional URLs
urlpatterns += [
    path("", include("django_acdhch_functions.urls")),
    path("select2/", include("django_select2.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("set-language/", set_language, name="set_language"),
]
