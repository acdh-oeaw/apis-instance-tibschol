from collections import defaultdict
from apis_core.apis_entities.utils import get_entity_content_types
from apis_core.relations.utils import relation_content_types


from collections import defaultdict
from json import loads


class DataModel:
    def __init__(self):
        self.entities = get_entity_content_types()
        self.relations = relation_content_types()
        self.matrix = defaultdict(dict)
        with open("apis_ontology/static/glossary-models.json", "r") as f:
            self.glossary = loads(f.read())

        with open("apis_ontology/static/glossary-terms.json", "r") as f:
            self.glossary_terms = loads(f.read())

        for rel in self.relations:
            rel_model = rel.model_class()
            subj = str(rel_model.subj_model.__name__)
            obj = str(rel_model.obj_model.__name__)
            name = rel_model.name()
            rev_name = rel_model.reverse_name()

            # initialisethe matrix if not already done
            if subj not in self.matrix:
                self.matrix[subj] = {}
            if obj not in self.matrix[subj]:
                self.matrix[subj][obj] = []

            if obj not in self.matrix:
                self.matrix[obj] = {}
            if subj not in self.matrix[obj]:
                self.matrix[obj][subj] = []

            # if subj and obj are the same then add name and reverse in the same row
            if subj == obj:
                if name == rev_name:
                    self.matrix[subj][obj].append(
                        {"class": rel.model_class().__name__, "display": name}
                    )
                    continue

                self.matrix[subj][obj].append(
                    {
                        "class": rel.model_class().__name__,
                        "display": f"{name}<span class='material-symbols-outlined align-middle text-secondary'>arrows_outward</span>{rev_name}",
                    }
                )
                continue

            self.matrix[subj][obj].append(
                {"class": rel.model_class().__name__, "display": name}
            )
            self.matrix[obj][subj].append(
                {"class": rel.model_class().__name__, "display": rev_name}
            )

        # sort the relations
        for subj in self.matrix:
            for obj in self.matrix[subj]:
                self.matrix[subj][obj].sort(key=lambda x: x["display"])
