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

    import_file = "data/20240513_entities.json"

    def add_arguments(self, parser):
        parser.add_argument("args", nargs="*", type=str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.df = pd.read_json(self.import_file)
        self.df = self.df[self.df.model != "apis_metainfo.uri"]
        logger.debug("Columns: %s", self.df.columns)
        logger.debug("Number of rows: %d", self.df.shape[0])
        logger.debug("Models: %s", self.df.model.unique())

    def handle(self, *args, **kwargs):
        """
        parses the data dump from the old schema and imports it into the current schema
        """
        if not args:
            logging.error("Please enter the names of entity models to import")
            return

        def get_entity_data(model_name):
            if model_name not in ENTITY_MODELS:
                logging.error(
                    "%s is unknown. Expecting one of %s", model_name, ENTITY_MODELS
                )
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
                if model_name == "place":
                    field_values["label"] = field_values["name"]
                    field_values.pop("name")

                # pprint(field_values)
                model_class = apps.get_model(f"apis_ontology.{model_name}")

                model_object = model_class(**field_values)
                model_object.save()

        for arg in args:
            if arg not in ENTITY_MODELS:
                logging.error("Unrecognised entity type %s for import", arg)
                break

            get_entity_data(arg)
