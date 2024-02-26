from django.utils import timezone

from rest_framework import serializers

from .models import Devices, DeviceAnalytics, QuickLinks, ActiveObjects


class DevicesSerializer(serializers.ModelSerializer):
    CreatedOn = serializers.DateTimeField(read_only=True)
    ModifiedOn = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Devices
        fields = (
            'id', 'Name', 'Location', 'CreatedOn', 'ModifiedOn'
        )

    def create(self, validated_data):
        #         # , ** validated_data
        device = Devices.objects.create(CreatedOn=timezone.now(), **validated_data)
        return device


class DevicesAnalyticsSerializer(serializers.ModelSerializer):
    Name = serializers.CharField(source='DeviceID.Name', read_only=True)
    DeviceId = serializers.CharField(write_only=True)
    InsertedOn = serializers.DateTimeField(read_only=True)

    class Meta:
        model = DeviceAnalytics
        fields = (
            'id', 'Name', 'InsertedOn', 'DeviceId', 'NetworkStatus', 'Status'
        )

    def create(self, validated_data):
        #         # , ** validated_data
        device = Devices.objects.get(id=validated_data.pop('DeviceId'))
        device_analytics = DeviceAnalytics.objects.create(DeviceID=device, InsertedOn=timezone.now(), **validated_data)
        return device_analytics


class ActiveObjectsSerializer(serializers.ModelSerializer):
    DeviceName = serializers.CharField(source='DeviceID.Name', read_only=True)
    DeviceId = serializers.CharField(write_only=True)
    InsertedOn = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ActiveObjects
        fields = (
            'id', 'Name', 'DeviceName', 'Keyword', 'InsertedOn', 'DeviceId'
        )

    def create(self, validated_data):
        #         # , ** validated_data
        device = Devices.objects.get(id=validated_data.pop('DeviceId'))
        active_object = ActiveObjects.objects.create(DeviceID=device, InsertedOn=timezone.now(), **validated_data)
        return active_object


class QuickLinksSerializer(serializers.ModelSerializer):
    DeviceName = serializers.CharField(source='DeviceID.Name', read_only=True)
    DeviceId = serializers.CharField(write_only=True)
    InsertedOn = serializers.DateTimeField(read_only=True)

    class Meta:
        model = QuickLinks
        fields = (
            'id', 'Name', 'DeviceName', 'InsertedOn', 'DeviceId'
        )

    def create(self, validated_data):
        #         # , ** validated_data
        device = Devices.objects.get(id=validated_data.pop('DeviceId'))
        quick_links = QuickLinks.objects.create(DeviceID=device, InsertedOn=timezone.now(), **validated_data)
        return quick_links
