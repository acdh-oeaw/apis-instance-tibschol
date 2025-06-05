from apis_core.relations.models import Relation
import logging

logger = logging.getLogger(__name__)


class TibScholDataExport:
    @staticmethod
    def all_relations():
        """
        Export relations data in JSON format.
        This method should be implemented to gather the necessary data.
        """

        def get_label(entity):
            try:
                return entity.name
            except AttributeError:
                try:
                    return entity.label
                except AttributeError:
                    pass

            return str(entity)

        relation_data = []
        qs = Relation.objects.select_subclasses().order_by("id")

        for rel in Relation.objects.select_subclasses():
            try:
                relation_data.append(
                    {
                        "source_type": rel.subj.__class__.__name__.lower(),
                        "source": rel.subj.id,
                        "source_label": get_label(rel.subj),
                        "target_type": rel.obj.__class__.__name__.lower(),
                        "target": rel.obj.id,
                        "target_label": get_label(rel.obj),
                        "forward": rel.name(),
                        "reverse": rel.reverse_name(),
                        "confidence": rel.confidence,
                        "start": rel.start,
                        "end": rel.end,
                        "topic": rel.topic if hasattr(rel, "topic") else "",
                    }
                )
            except Exception as e:
                logger.error(
                    "Error processing relation %s: %s",
                    rel.id,
                    e,
                    exc_info=True,
                )

        print(f"Exported {len(relation_data)} relations")
        return relation_data
