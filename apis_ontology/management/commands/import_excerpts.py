import logging
from apis_ontology.models import Excerpts
import pandas as pd
from django.apps import apps
from django.core.management.base import BaseCommand
from tqdm.auto import tqdm

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Imports excerpts from data/excerpts.csv
    """

    def add_arguments(self, parser):
        parser.add_argument("dump", type=str, help="dump file name")

    def handle(self, *args, **kwargs):
        def create_record(row):
            record, _ = Excerpts.objects.get_or_create(xml_id=row.xml_id)
            record.__dict__.update(row.to_dict())
            record.save()

        # define an input parameter for import_file

        print(f"Found {len(Excerpts.objects.all())} excerpts in the database")
        import_file = kwargs["dump"]

        df = pd.read_csv(import_file).fillna("")
        print(f"Importing {df.shape[0]} excerpts from {import_file}")

        for _, row in tqdm(df.iterrows(), total=df.shape[0]):
            create_record(row)

        self.stdout.write(self.style.SUCCESS(f"Processed {df.shape[0]} excerpts."))
        print(f"There are {len(Excerpts.objects.all())} in the database now.")
