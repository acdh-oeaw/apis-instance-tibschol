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

        def get_subject_vocab(rel):
            subjects = None
            if hasattr(rel, "subject_vocab"):
                subjects = rel.subject_vocab.all()
            elif hasattr(rel, "subject_of_teaching_vocab"):
                subjects = rel.subject_of_teaching_vocab.all()

            return [sub.name for sub in subjects] if subjects else []

        relation_data = []
        qs = Relation.objects.select_subclasses()

        for rel in qs:
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
                        "start_date_from": rel.start_date_from,
                        "start_date_to": rel.start_date_to,
                        "start_date_sort": rel.start_date_sort,
                        "end_date_to": rel.end_date_from,
                        "end_date_from": rel.end_date_to,
                        "end_date_sort": rel.end_date_sort,
                        "topics": get_subject_vocab(rel),
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
