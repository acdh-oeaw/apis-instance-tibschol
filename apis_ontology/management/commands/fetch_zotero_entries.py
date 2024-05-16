import logging
import os

import pandas as pd
import requests
from apis_ontology.models import ZoteroEntry
from django.core.management.base import BaseCommand
from tqdm.auto import tqdm

USER = os.environ.get("APIS_BIBSONOMY_USER")
KEY = os.environ.get("APIS_BIBSONOMY_PASSWORD")
GROUP = "4394244"


QUERY_URL = f"https://api.zotero.org/groups/{GROUP}/items"
HEADERS = {"Authorization": f"Bearer {KEY}"}
PARAMS = {"v": 3, "format": "json"}

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--fake", action="store_true", help="Whether to fake or really update"
        )

    def handle(self, *args, **kwargs):
        res = requests.get(QUERY_URL, headers=HEADERS, params=PARAMS)
        res.raise_for_status()
        num_records = res.headers["Total-Results"]
        print(f"Found {len(num_records)} records")
        all_items = []
        for start in tqdm(range(0, int(num_records), 25)):
            PARAMS["start"] = start
            res = requests.get(QUERY_URL, headers=HEADERS, params=PARAMS)

            res.raise_for_status()
            items = res.json()
            print(f"Fetched {len(items)}.")
            all_items.extend(items)

        df = pd.json_normalize(all_items)
        print(f"Fetched {df.shape[0]} items in total")
        print(f"... of which there are {len(df['data.key'].unique())} are unique keys.")
        for i, row in tqdm(df.iterrows(), total=df.shape[0]):
            if "apis" in [tag["tag"].lower() for tag in row["data.tags"]]:
                zotero_entry, _ = ZoteroEntry.objects.get_or_create(
                    zoteroId=row["data.key"]
                )
                zotero_entry.shortTitle = row["data.shortTitle"]
                zotero_entry.fullCitation = row["data.title"]
                zotero_entry.year = row["data.date"]
                zotero_entry.save()

        print(f"Cached {len(ZoteroEntry.objects.all())} zotero entries.")
