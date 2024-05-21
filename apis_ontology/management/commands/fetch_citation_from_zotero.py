import json
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


QUERY_URL = f"https://api.zotero.org/groups/{GROUP}/items/"
HEADERS = {"Authorization": f"Bearer {KEY}"}
PARAMS = {
    "v": 3,
    "format": "json",
    # "itemKey": "Z5AUD7GQ,UJDXNMGD,KUYBGM7V,5DSBYG9K"
}

logger = logging.getLogger(__name__)

KEYS = ["Z5AUD7GQ", "UJDXNMGD", "KUYBGM7V", "5DSBYG9K"]


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        destination = "apis_ontology/static/citations.json"
        citations = {}
        for k in KEYS:
            res = requests.get(QUERY_URL, headers=HEADERS, params=PARAMS)
            res.raise_for_status()
            citations[k] = res.json()

        with open(destination, "w") as f:
            f.write(json.dumps(citations))
        self.stdout.write(self.style.SUCCESS(f"Processed {df.shape[0]} excerpts."))
