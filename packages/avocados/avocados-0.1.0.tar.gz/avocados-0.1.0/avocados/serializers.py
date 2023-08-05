from rest_framework import serializers
from django.conf import settings

class AvocadoSerializer(serializers.Serializer):
    date = serializers.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    average_price = serializers.FloatField(required=False)
    total_volume = serializers.FloatField()
    small_hass = serializers.FloatField()
    large_hass = serializers.FloatField()
    xlarge_hass = serializers.FloatField()
    total_bags = serializers.FloatField()
    small_bags = serializers.FloatField()
    large_bags = serializers.FloatField()
    xlarge_bags = serializers.FloatField()
    avocado_type = serializers.CharField()
    year = serializers.IntegerField()
    region = serializers.CharField()