import logging

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

    def handle(self, *args, **kwargs):
        """
        parses the data dump from the old schema and imports it into the current schema
        """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.df = pd.read_json(self.import_file)
        self.df = self.df[self.df.model != "apis_metainfo.uri"]
        logger.debug("Columns: %s", self.df.columns)
        logger.debug("Number of rows: %d", self.df.shape[0])
        logger.debug("Models: %s", self.df.model.unique())

        def get_relations_data(model_name):

            entity_rows = self.df[self.df.model == f"apis_ontology.{model_name}"]
            logging.debug("Found %d rows of type %s", entity_rows.shape[0], model_name)
            other_fields = {}
            for _, row in tqdm(entity_rows.iterrows(), total=entity_rows.shape[0]):
                # get data from root object
                other_object_info = self.df[
                    (self.df.pk == row.pk) & (self.df.model != row.model)
                ]
                for _, extra_fields in other_object_info.iterrows():
                    if extra_fields.model.startswith("apis_ontology"):
                        continue

                    other_fields = {**other_fields, **extra_fields.fields}

                field_values = {
                    "id": row.pk,
                    **row.fields,
                    **other_fields,
                }

                field_values.pop("self_contenttype")
                field_values.pop("collection")
                field_values.pop("status")
                field_values.pop("source")
                field_values.pop("references")
                field_values["external_links"] = field_values["external_link"]
                field_values.pop("external_link")

                # pprint(field_values)
                model_class = apps.get_model(f"apis_ontology.{model_name}")

                model_object = model_class(**field_values)
                model_object.save()

        for i, row in self.df.iterrows():
            if not row.model.startswith("apis_ontology"):
                continue

            entity_model_names = [f"apis_ontology.{m}" for m in ENTITY_MODELS]
            if row.model in entity_model_names:
                continue

            field_values = {"id": row.pk, **row.fields}
            model_class = apps.get_model(row.model)
            model_object = model_class(**field_values)
            model_object.save()
