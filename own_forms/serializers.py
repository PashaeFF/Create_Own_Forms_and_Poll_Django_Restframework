from rest_framework import serializers

class FilledFormsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    filled_form = serializers.JSONField()
    created_at = serializers.DateTimeField()
    counter = serializers.IntegerField()

class FormSerializer(serializers.Serializer):
    form_name = serializers.CharField()
    url = serializers.URLField()

class CreateValuesSerializer(serializers.Serializer):
    question_field_1 = serializers.DictField()

class FillFormSerializer(serializers.Serializer):
    question_field_1 = serializers.ListField()