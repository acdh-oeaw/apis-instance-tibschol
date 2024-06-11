from django.contrib.contenttypes.models import ContentType
from django.db import models


def is_relavent_relation_model(relation_model, entity_model):
    if hasattr(relation_model, "subj_model") and hasattr(relation_model, "obj_model"):
        return (
            relation_model.obj_model == entity_model
            or relation_model.subj_model == entity_model
        )


def get_relavent_relations(any_model):
    relavent_rels = []
    for ct in ContentType.objects.filter(models.Q(app_label="apis_ontology")):
        rel_model = ct.model_class()
        if hasattr(rel_model, "subj_model") and hasattr(rel_model, "obj_model"):
            if rel_model.subj_model == any_model and rel_model.obj_model == any_model:
                relavent_rels.append(
                    (
                        f"{rel_model.__name__}",
                        f"{rel_model.name}/{rel_model.reverse_name}",
                    )
                )

            elif rel_model.subj_model == any_model:
                relavent_rels.append((f"{rel_model.__name__}", rel_model.name))
            elif rel_model.obj_model == any_model:
                relavent_rels.append((f"{rel_model.__name__}", rel_model.reverse_name))

    return relavent_rels
