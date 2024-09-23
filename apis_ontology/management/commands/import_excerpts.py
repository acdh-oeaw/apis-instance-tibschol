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

    def handle(self, *args, **kwargs):
        def create_record(row):
            record, _ = Excerpts.objects.get_or_create(xml_id=row.xml_id)
            record.xml_content = row.xml_content
            record.source = row.source
            record.save()

        print(len(Excerpts.objects.all()))
        import_file = "data/excerpts.csv"
        df = pd.read_csv(import_file)
        for _, row in tqdm(df.iterrows(), total=df.shape[0]):
            create_record(row)

        self.stdout.write(self.style.SUCCESS(f"Processed {df.shape[0]} excerpts."))
        print("There are f{len(Excerpts.objects.all())} in the database now.")
