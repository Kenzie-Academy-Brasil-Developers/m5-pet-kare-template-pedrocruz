from rest_framework import serializers
from groups.serializers import GroupSerializer


from pets.models import Sex
from traits.serializers import TraitSerializer


class PetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    age = serializers.IntegerField()
    weight = serializers.FloatField()
    sex = serializers.ChoiceField(
        choices=Sex.choices,
        default=Sex.DEFAULT
    )

    traits = TraitSerializer(many=True)
    group = GroupSerializer()


