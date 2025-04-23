from collections import defaultdict
from apis_core.apis_entities.utils import get_entity_content_types
from apis_core.relations.utils import relation_content_types


class DataModel:
    entities: list = []
    relations: list = []
    matrix = defaultdict(dict)

    def __init__(self):
        self.entities = get_entity_content_types()
        self.relations = relation_content_types()
        self.matrix = defaultdict(dict)

        for rel in self.relations:
            rel_model = rel.model_class()
            if (
                str(rel_model.subj_model.__name__)
                in self.matrix[str(rel_model.obj_model.__name__)]
            ):
                self.matrix[str(rel_model.subj_model.__name__)][
                    str(rel_model.obj_model.__name__)
                ].append(rel_model.name())

                self.matrix[str(rel_model.obj_model.__name__)][
                    str(rel_model.subj_model.__name__)
                ].append(rel_model.reverse_name())

            else:
                self.matrix[str(rel_model.subj_model.__name__)][
                    str(rel_model.obj_model.__name__)
                ] = [rel_model.name()]
                self.matrix[str(rel_model.obj_model.__name__)][
                    str(rel_model.subj_model.__name__)
                ] = [rel_model.reverse_name()]

        # sort the relations
        for row in self.matrix:
            for col in self.matrix[row]:
                self.matrix[row][col] = sorted(list(set(self.matrix[row][col])))
