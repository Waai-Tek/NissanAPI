import sys
from datetime import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Max, Subquery, Count
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
        print(cars_clicks)

        # Query to annotate the count of occurrences of each value in your_field
        queryset = cars_clicks.values('Name').annotate(count=Count('Name'))
        for item in queryset:
            print(item['Name'], item['count'])

        # Create a dictionary from the queryset
        result_dict = {item['Name']: item['count'] for item in queryset}

        print(result_dict)
        device_name = cars_clicks[0].DeviceID.Name

        # # Get the latest insertion time for each foreign key ID
        # latest_insertion_times = DeviceAnalytics.objects.values('DeviceID_id').annotate(
        #     latest_insertion_time=Max('InsertedOn'))
        # # Subquery to filter DeviceAnalytics instances by the latest insertion time for each foreign key ID
        # latest_main_models = DeviceAnalytics.objects.filter(
        #     InsertedOn__in=Subquery(latest_insertion_times.values('latest_insertion_time')))
        # # Get the related objects for the latest DeviceAnalytics instances
        # devices_list = DeviceAnalytics.objects.filter(id__in=latest_main_models).order_by('-InsertedOn')
        # print(devices_list)
        # device_name = devices_list[0].DeviceID.Name
        args = {
            'device_name': device_name
        }
        return render(request, self.template_name, args)
