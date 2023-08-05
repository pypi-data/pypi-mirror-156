from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework.settings import api_settings

from expressmoney_service import exceptions


class GenericServiceSerializer(ModelSerializer):
    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except exceptions.ClientError as e:
            raise ValidationError({api_settings.NON_FIELD_ERRORS_KEY: [e]})
