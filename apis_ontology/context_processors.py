# context_processors.py
from apis_ontology.templatetags.entity_display import prefers_tibetan_script


def script_preferences(request):
    return {
        "prefers_tibetan_script": prefers_tibetan_script(request),
    }
