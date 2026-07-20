from django import template

register = template.Library()


def prefers_tibetan_script(request):
    if not request:
        return False

    if (
        hasattr(request, "user")
        and request.user.is_authenticated
        and request.user.is_staff
    ):
        return getattr(
            getattr(request.user, "script_preference", None),
            "prefers_tibetan_script",
            False,
        )

    return request.session.get("script_preference", {}).get(
        "prefers_tibetan_script", False
    )


def display_entity_name(obj, request=None):
    id = getattr(obj, "pk", None)
    translit = getattr(obj, "tibetan_transliteration", None)

    if prefers_tibetan_script(request) and translit:
        return f"{translit} ({id})"

    return str(obj)


@register.simple_tag(takes_context=True)
def entity_display_name(context, obj):
    request = context.get("request", None)
    return display_entity_name(obj, request)
