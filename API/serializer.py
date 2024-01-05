from rest_framework import serializers

from .models import BaseJourney


class JourneySerializer(serializers.ModelSerializer):
    CreatedOn = serializers.DateTimeField()

    class Meta:
        model = BaseJourney
        fields = (
            'id', 'Name', 'JourneyDescription', 'CreatedOn'
        )