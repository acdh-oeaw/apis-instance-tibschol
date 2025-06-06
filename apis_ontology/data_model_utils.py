from collections import defaultdict
from apis_core.apis_entities.utils import get_entity_content_types
from apis_core.relations.utils import relation_content_types


from collections import defaultdict


class DataModel:
    def __init__(self):
        self.entities = get_entity_content_types()
        self.relations = relation_content_types()
        self.matrix = defaultdict(dict)

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
                    self.matrix[subj][obj].append(name)
                    continue

                self.matrix[subj][obj].append(
                    f"{name}<span class='material-symbols-outlined align-middle text-secondary'>arrows_outward</span>{rev_name}"
                )
                continue

            self.matrix[subj][obj].append(name)
            self.matrix[obj][subj].append(rev_name)

        # sort the relations
        for row in self.matrix:
            for col in self.matrix[row]:
                self.matrix[row][col] = sorted(set(self.matrix[row][col]))
