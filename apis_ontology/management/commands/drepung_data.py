from django.core.management.base import BaseCommand

from apis_ontology.models import Work, Instance, WorkHasAsAnInstanceInstance
import re
from tqdm.auto import tqdm
from django.apps import apps
import os, logging
import django
from collections import defaultdict
from django.apps import apps

from django.db.models import Q

import pandas as pd

DREPUNG_COMMENT = "#drepungimport"


class Command(BaseCommand):
    help = "Import data from Drepung catalog"

    def handle(self, *args, **options):
        def find_matching_instance(tibschol_ref=None, drepung_cat=None):
            if not (tibschol_ref or drepung_cat):
                return

            if tibschol_ref:
                try:
                    match = Instance.objects.filter(
                        Q(tibschol_ref__regex=rf"(^|\b){tibschol_ref}(\b|$)")
                    )
                    return match
                except Instance.DoesNotExist:
                    logging.debug(
                        "No matching isntance for tibschol ref %s", tibschol_ref
                    )

            if drepung_cat:
                try:
                    match = Instance.objects.filter(drepung_number=drepung_cat)
                    return match

                except Instance.DoesNotExist:
                    logging.debug(
                        "No matching isntance for drepubg catalog number %s",
                        dreppung_cat,
                    )

        df_topics = (
            pd.read_csv("data/topics.csv").fillna("").replace("-", "", regex=False)
        )

        df_drepung = (
            pd.read_csv("data/Drepung_Catalogue.csv")
            .fillna("")
            .replace("-", "", regex=False)
        )

        # COLLECTION, _ = Collection.objects.get_or_create(name="Drepung Catalog")
        columns_map = {chr(65 + i): col for i, col in enumerate(df_drepung.columns)}
        inserts = []

        for i, row in tqdm(df_drepung.iterrows(), total=df_drepung.shape[0]):
            instance = find_matching_instance(
                drepung_cat=row[columns_map["G"]], tibschol_ref=row[columns_map["F"]]
            )
            if instance:
                if len(instance) != 1:
                    logging.debug("Found %s match(es) for row %s", len(instance), i)
                    continue
                work = Work.objects.get(
                    pk=WorkHasAsAnInstanceInstance.objects.filter(
                        obj_id=instance[0].pk
                    )[0].subj_id
                )
                instance[0].dimension = row[columns_map["S"]]

                if (
                    instance[0].comments and DREPUNG_COMMENT not in instance[0].comments
                ) or not instance[0].comments:
                    instance[0].comments = (
                        (instance[0].comments or "")
                        + "\n#drepungimport. This item is listed in [8H6M69W4]"
                    ).strip()

                if (
                    work.comments and DREPUNG_COMMENT not in work.comments
                ) or not work.comments:
                    work.comments = (
                        (work.comments or "")
                        + "\n#drepungimport. Author according to [8H6M69W4]: "
                        + row[columns_map["J"]]
                    ).strip()

                instance[0].num_folios = row[columns_map["E"]]

                if (
                    instance[0].alternative_names
                    and row[columns_map["C"]].strip()
                    not in instance[0].alternative_names
                ) or not instance[0].alternative_names:
                    instance[0].alternative_names = (
                        (instance[0].alternative_names or "")
                        + "\n"
                        + row[columns_map["C"]]
                    ).strip()

                if (
                    work.alternative_names
                    and row[columns_map["C"]].strip() not in work.alternative_names
                ) or not work.alternative_names:
                    work.alternative_names = (
                        (work.alternative_names or "") + "\n" + row[columns_map["C"]]
                    ).strip()

                instance[0].save()
                work.save()
            else:
                # Create instance
                # Create work
                # Link work and instance
                # Add signature letter to instance
                # Add subject to work

                inserts.append(i)

        df_drepung.iloc[inserts].to_csv("Drepung_new.csv", index=False)
        self.stdout.write(self.style.SUCCESS(f"Drepung catalog import complete"))
