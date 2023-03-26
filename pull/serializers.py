from rest_framework import serializers
from .models import Pull

class CreatePullSerializer(serializers.Serializer):
    pull_name = serializers.CharField(max_length=250)
    answers = serializers.DictField()
    anonimouse = serializers.BooleanField()
    more_answers = serializers.BooleanField()

    class Meta:
        model = Pull


class AnswerSerializer(serializers.Serializer):
    answer = serializers.ListField()