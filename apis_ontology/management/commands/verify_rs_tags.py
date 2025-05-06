"""
This is a management command to validate RS tags in excerpts
that point to entities in the database
"""
import logging
from xml.etree import ElementTree as ET

from apis_ontology.models import Excerpts
from django.apps import apps
from django.core.management.base import BaseCommand
from tqdm import tqdm

ns = {"tei": "http://www.tei-c.org/ns/1.0"}


class Command(BaseCommand):
    help = "Verify the presence of RS tags in the database"

    def handle(self, *args, **options):
        errors = []
        for ex in tqdm(Excerpts.objects.all()):
            error_template = {"source": ex.source, "xml_id": ex.xml_id}
            rs_tags = ex.xml_content.count("<rs")
            if rs_tags == 0:
                continue
            try:
                root = ET.fromstring(ex.xml_content)
                rs_tags = root.findall(".//tei:rs", namespaces=ns)
                for rs in rs_tags:
                    if "ref" not in rs.attrib:
                        continue
                    if not rs.attrib.get("ref").startswith("db:"):
                        continue

                    try:
                        model_name = rs.attrib.get("type", "")
                        if model_name.lower() not in (
                            "person",
                            "place",
                            "work",
                            "instance",
                        ):
                            continue
                        pk = rs.attrib.get("ref", "").lstrip("db:")
                        if model_name and not pk:
                            errors.append(
                                {
                                    **error_template,
                                    "model": model_name,
                                    "error": "no database reference",
                                }
                            )
                            continue

                        model = apps.get_model("apis_ontology", model_name.capitalize())
                        try:
                            model.objects.get(pk=pk)
                        except model.DoesNotExist:
                            errors.append(
                                {
                                    **error_template,
                                    "model": model_name,
                                    "error": f"db:{pk} not found",
                                }
                            )
                    except Exception as e:
                        logging.error(
                            "Error processing rs tag in excerpt %s, %s", ex.xml_id, e
                        )
                        continue
            except ET.ParseError:
                logging.error(f"Parse error in excerpt {ex.xml_id}")
                continue

        if errors:
            logging.info(f"%s Errors found", len(errors))

            import pandas as pd

            error_filename = "excerpts_rs_errors.md"
            pd.DataFrame(errors).sort_values("source").to_markdown(
                error_filename, index=False
            )
            logging.info("Errors saved to %s", error_filename)
