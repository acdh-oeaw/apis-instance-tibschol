from apis_core.generic.serializers import (
    GenericHyperlinkedModelSerializer,
    SimpleObjectSerializer,
    serializer_factory,
)
from apis_core.relations.models import Relation
from drf_spectacular.utils import extend_schema_field
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer


class TibScholRelationMixinSerializer(ModelSerializer):
    label = SerializerMethodField()
    subj = SerializerMethodField()
    obj = SerializerMethodField()

    def get_label(self, obj) -> str:
        return str(obj)

    @extend_schema_field(SimpleObjectSerializer())
    def get_subj(self, obj):
        if obj.subj:
            serializer = serializer_factory(type(obj.subj), SimpleObjectSerializer)
            return serializer(
                obj.subj, context={"request": self.context["request"]}
            ).data

    @extend_schema_field(SimpleObjectSerializer())
    def get_obj(self, obj):
        if obj.obj:
            serializer = serializer_factory(type(obj.obj), SimpleObjectSerializer)
            return serializer(
                obj.obj, context={"request": self.context["request"]}
            ).data

    class Meta:
        exclude = (
            "subj_content_type",
            "subj_object_id",
            "obj_content_type",
            "obj_object_id",
        )


class TibScholEntityMixinSerializer(GenericHyperlinkedModelSerializer):
    relations = SerializerMethodField()

    @extend_schema_field(SimpleObjectSerializer())
    def get_relations(self, obj):
        subj_rels = Relation.objects.filter(subj_object_id=obj.pk).select_subclasses()
        obj_rels = Relation.objects.filter(obj_object_id=obj.pk).select_subclasses()
        combined = list(subj_rels) + list(obj_rels)
        serialized = []
        request = self.context.get("request")

        for rel in combined:
            # Pick serializer based on subclass
            serializer_class = serializer_factory(
                rel.__class__, serializer=TibScholRelationMixinSerializer
            )
            serialized.append(serializer_class(rel, context={"request": request}).data)

        return serialized
