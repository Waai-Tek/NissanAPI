import sys
from urllib import request

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import path, include, re_path


from .views import AllDeviceAnalyticsView, IndividualDeviceAnalyticsView, get_clicks


urlpatterns = [
    path('', AllDeviceAnalyticsView.as_view(), name='AllDeviceAnalytics'),
    path('IndividualDeviceAnalytics/<int:device_id>', IndividualDeviceAnalyticsView.as_view(), name='IndividualDeviceAnalytics'),
    path('get_clicks', get_clicks, name='get_clicks'),
]
