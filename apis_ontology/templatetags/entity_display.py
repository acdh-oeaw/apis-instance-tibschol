from django import template

register = template.Library()


def display_entity_name(obj, request=None):
    # Person, Work, Instance: use name; Place: use label
    name = getattr(obj, "name", None) or getattr(obj, "label", None)
    id = getattr(obj, "pk", None)
    translit = getattr(obj, "tibetan_transliteration", None)
    # Try to get user preference from request
    if (
        request
        and hasattr(request, "user")
        and getattr(request.user, "is_authenticated", False)
    ):
        script_pref = getattr(
            getattr(request.user, "script_preference", None),
            "prefers_tibetan_script",
            False,
        )
        if script_pref and translit:
            return f"{translit} ({id})"
    return str(obj)


@register.simple_tag(takes_context=True)
def entity_display_name(context, obj):
    request = context.get("request", None)
    return display_entity_name(obj, request)
