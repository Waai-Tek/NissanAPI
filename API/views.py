from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

from .models import Devices, DeviceAnalytics, ActiveObjects, QuickLinks
from .serializer import DevicesSerializer, DevicesAnalyticsSerializer, ActiveObjectsSerializer, QuickLinksSerializer


# Create your views here.
class DevicesViewSet(generics.ListCreateAPIView):
    queryset = Devices.objects.all()
    serializer_class = DevicesSerializer

    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['Name']

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DevicesAnalyticsViewSet(generics.ListCreateAPIView):
    queryset = DeviceAnalytics.objects.all()
    serializer_class = DevicesAnalyticsSerializer

    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['Name']

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ActiveObjectsViewSet(generics.ListCreateAPIView):
    queryset = ActiveObjects.objects.all()
    serializer_class = ActiveObjectsSerializer

    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['Name']

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class QuickLinksViewSet(generics.ListCreateAPIView):
    queryset = QuickLinks.objects.all()
    serializer_class = QuickLinksSerializer

    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['Name']

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
