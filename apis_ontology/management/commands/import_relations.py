import logging
from apis_core.apis_metainfo.models import RootObject
from apis_core.relations.models import Relation

import pandas as pd
from django.apps import apps
from django.core.management.base import BaseCommand
from tqdm.auto import tqdm

logger = logging.getLogger(__name__)
pd.set_option("display.max_colwidth", None)

ENTITY_MODELS = ["person", "place", "instance", "work"]


class Command(BaseCommand):
    """
    Imports data from the old schema into the new schema INCLUDING the primary keys
    """

    import_file = "data/dump_test.json"
    import_base_rels = "data/relations_dump.json"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clean",
            action="store_true",
            dest="clean",
            default=False,
            help="Delete all existing relations. Default: False)",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.df = pd.read_json(self.import_file)
        self.df = self.df[
            (
                (self.df.model.str.startswith("apis_ontology"))
                & (self.df.model != "apis_ontology.zoteroentry")
                & (self.df.model != "apis_ontology.place")
                & (self.df.model != "apis_ontology.person")
                & (self.df.model != "apis_ontology.work")
                & (self.df.model != "apis_ontology.instance")
            )
        ]

        self.base_rels = pd.read_json(self.import_base_rels)

        logger.debug("Columns: %s", self.df.columns)
        logger.debug("Number of rows: %d", self.df.shape[0])
        logger.debug("Models: %s", self.df.model.unique())

    def handle(self, *args, **kwargs):
        """
        parses the data dump from the old schema and imports it into the current schema
        """
        if kwargs["clean"]:
            Relation.objects.all().delete()

        def get_subj_obj_data(pk):
            base_rel_match = self.base_rels[self.base_rels.pk == pk].iloc[0]
            try:
                subj = RootObject.objects_inheritance.get_subclass(
                    pk=base_rel_match.fields["subj"]
                )
                obj = RootObject.objects_inheritance.get_subclass(
                    pk=base_rel_match.fields["obj"]
                )
            except Exception as e:
                logging.error(
                    "Cannot find subject and object for relation [%s], %s",
                    pk,
                    base_rel_match,
                )
                return None, None
            return subj, obj

        for _, row in tqdm(self.df.iterrows(), total=self.df.shape[0]):

            field_values = {**row.fields}  # "id": row.pk,
            subj_obj_data = get_subj_obj_data(row.pk)
            field_values["subj"], field_values["obj"] = subj_obj_data
            if not (field_values["subj"] and field_values["obj"]):
                logging.error(
                    "SKIPPING relation %s with values: %s", row.model, field_values
                )
                continue

            try:
                if "notes" in field_values:
                    if (
                        not field_values["notes"]
                        or field_values.get("notes", "").strip()
                    ):
                        field_values.pop("notes")
            except Exception as e:
                print(field_values, repr(e))
                break

            model_class = apps.get_model(row.model)
            model_object = model_class(**field_values)
            model_object.save()
