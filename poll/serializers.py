from rest_framework import serializers
from .models import Poll

class CreatePollSerializer(serializers.Serializer):
    poll_name = serializers.CharField(max_length=250)
    answers = serializers.DictField()
    anonimouse = serializers.BooleanField()
    more_answers = serializers.BooleanField()

    class Meta:
        model = Poll


class AnswerSerializer(serializers.Serializer):
    answer = serializers.ListField()

class ViewAnswerSerializer(serializers.Serializer):
    answers = serializers.ListField()