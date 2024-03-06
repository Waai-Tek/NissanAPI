import sys
from urllib import request

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import path, include, re_path

from django.contrib.auth import views
from .views import AllDeviceAnalyticsView, IndividualDeviceAnalyticsView, get_clicks, LoginView, landing_redirection, change_password


urlpatterns = [
    path('', landing_redirection, name='landing'),

    path('login/', LoginView.as_view(), name='login'),
    path('change-password/', change_password, name='change_password'),
    path('accounts/logout/', views.LogoutView.as_view(), name='logout'),
    path('AllDeviceAnalytics/', AllDeviceAnalyticsView.as_view(), name='AllDeviceAnalytics'),

    path('IndividualDeviceAnalytics/<int:device_id>', IndividualDeviceAnalyticsView.as_view(), name='IndividualDeviceAnalytics'),
    path('get_clicks', get_clicks, name='get_clicks'),
]
