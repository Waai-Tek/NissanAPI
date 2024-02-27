import sys
from collections import Counter
from datetime import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites import requests
from django.db.models import Max, Subquery, Count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

sys.path.insert(0, '..')
from API.models import Devices, DeviceAnalytics, ActiveObjects, QuickLinks


class LoginView(TemplateView):
    template_name = 'registration/login.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request):
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            if request.user.groups.filter(name="Admin").exists():
                return redirect('settings')
            else:
                return redirect('landing')
        else:
            # messages.error(request, 'Username or Password is incorrect')
            print('Username or Password is incorrect')
            # return render(request, 'registration/login.html', context={'messages': messages})
            return redirect('landing')


# Create your views here.
class AllDeviceAnalyticsView(TemplateView):
    template_name = 'Analytics/DeviceAnalytics.html'

    def get(self, request, *args, **kwargs):

        # Get the latest insertion time for each foreign key ID
        latest_insertion_times = DeviceAnalytics.objects.values('DeviceID_id').annotate(
            latest_insertion_time=Max('InsertedOn'))
        # Subquery to filter DeviceAnalytics instances by the latest insertion time for each foreign key ID
        latest_main_models = DeviceAnalytics.objects.filter(
            InsertedOn__in=Subquery(latest_insertion_times.values('latest_insertion_time')))
        # Get the related objects for the latest DeviceAnalytics instances
        devices_list = DeviceAnalytics.objects.filter(id__in=latest_main_models).order_by('-InsertedOn')
        print(devices_list)
        device_name = devices_list[0].DeviceID.Name
        args = {
            'devices_list': devices_list,
            'device_name': device_name
        }
        return render(request, self.template_name, args)


class IndividualDeviceAnalyticsView(TemplateView):
    template_name = 'Analytics/Analytics.html'

    def get(self, request, *args, **kwargs):
        args = {}
        device_id = self.kwargs['device_id']
        cars_clicks = ActiveObjects.objects.filter(DeviceID_id=device_id, InsertedOn__year=datetime.now().year).order_by('-InsertedOn')
        total_interactions = cars_clicks.count()
        # Query to annotate the count of occurrences of each value in your_field
        queryset = cars_clicks.values('Name').annotate(count=Count('Name'))
        # Create a dictionary where each name is mapped to its count of occurrences
        cars_count = {}
        for item in queryset:
            cars_count[item['Name']] = cars_count.get(item['Name'], 0) + item['count']
        print(cars_count)

        ql_click = QuickLinks.objects.filter(DeviceID_id=device_id,
                                                   InsertedOn__year=datetime.now().year).order_by('-InsertedOn')
        total_interactions += ql_click.count()
        # Query to annotate the count of occurrences of each value in your_field
        ql_queryset = ql_click.values('Name').annotate(count=Count('Name'))
        # Create a dictionary where each name is mapped to its count of occurrences
        ql_count = {}
        for item in ql_queryset:

            ql_count[item['Name']] = ql_count.get(item['Name'], 0) + item['count']
        print(ql_count)
        if 'Finance click' in ql_count:
            fc_clicks = ql_count['Finance click']
        else:
            fc_clicks = 0
        if 'Offers click' in ql_count:
            oc_clicks = ql_count['Offers click']
        else:
            oc_clicks = 0
        if 'Brochure Downloads' in ql_count:
            bd_clicks = ql_count['Brochure Downloads']
        else:
            bd_clicks = 0
        if 'Service click' in ql_count:
            sc_clicks = ql_count['Service click']
        else:
            sc_clicks = 0
        device_name = cars_clicks[0].DeviceID.Name

        args = {
            'device_name': device_name,
            'cars_count': cars_count,
            'total_interactions': total_interactions,
            'ql_count': ql_count,
            'fc_clicks': fc_clicks,
            'oc_clicks': oc_clicks,
            'bd_clicks': bd_clicks,
            'sc_clicks': sc_clicks,
            'device_id': device_id
        }
        return render(request, self.template_name, args)


def get_clicks(request):
    device_id = request.GET.get('device_id')
    car_name = request.GET.get('car_name')
    # device_id = '1'
    keywords = []
    counts = []
    # car_name = 'Sunny'
    car_clicks = ActiveObjects.objects.filter(DeviceID_id=device_id, Name=car_name, InsertedOn__year=datetime.now().year).order_by(
        '-InsertedOn')
    ao_queryset = car_clicks.values('Keyword').annotate(count=Count('Keyword'))
    # Create a dictionary where each name is mapped to its count of occurrences
    ao_count = {}
    for item in ao_queryset:
        ao_count[item['Keyword']] = ao_count.get(item['Keyword'], 0) + item['count']
    print('-------------------------------',ao_count)
    for item in ao_count:
        keyword = item['Keyword']
        count = item['count']

        # Append keyword and count to respective lists
        keywords.append(keyword)
        counts.append(count)
    args = {
        'ao_count': ao_count,
        'keywords': keywords,
        'counts': counts
    }
    return JsonResponse(args)
