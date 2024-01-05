from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

from .models import BaseJourney
from .serializer import JourneySerializer


# Create your views here.
class BaseJourneyViewSet(generics.ListCreateAPIView):
    queryset = BaseJourney.objects.all()
    serializer_class = JourneySerializer
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['Name']

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)