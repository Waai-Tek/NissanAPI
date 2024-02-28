import sys
from collections import Counter
from datetime import datetime, timedelta

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
        graph_data = get_week_data_all()
        args = {
            'devices_list': devices_list,
            'this_week_data': graph_data[0],
            'last_week_data': graph_data[1],
        }
        return render(request, self.template_name, args)


class IndividualDeviceAnalyticsView(TemplateView):
    template_name = 'Analytics/Analytics.html'

    def get(self, request, *args, **kwargs):
        args = {}

        device_id = self.kwargs['device_id']
        graph_data = get_week_data(device_id)
        cars_clicks = ActiveObjects.objects.filter(DeviceID_id=device_id, InsertedOn__year=datetime.now().year).order_by('-InsertedOn')
        total_interactions = cars_clicks.count()
        # Query to annotate the count of occurrences of each value in your_field
        queryset = cars_clicks.values('Name').annotate(count=Count('Name'))
        # Create a dictionary where each name is mapped to its count of occurrences
        cars_count = {}
        for item in queryset:
            cars_count[item['Name']] = cars_count.get(item['Name'], 0) + item['count']

        # Sort the dictionary items based on their values in descending order
        sorted_items = sorted(cars_count.items(), key=lambda x: x[1], reverse=True)

        # Convert the sorted items back to a dictionary
        cars_count = dict(sorted_items)

        ql_click = QuickLinks.objects.filter(DeviceID_id=device_id,
                                                   InsertedOn__year=datetime.now().year).order_by('-InsertedOn')
        total_interactions += ql_click.count()
        # Query to annotate the count of occurrences of each value in your_field
        ql_queryset = ql_click.values('Name').annotate(count=Count('Name'))
        # Create a dictionary where each name is mapped to its count of occurrences
        ql_count = {}
        for item in ql_queryset:
            ql_count[item['Name']] = ql_count.get(item['Name'], 0) + item['count']
        if 'Finance Calculator' in ql_count:
            fc_clicks = ql_count['Finance Calculator']
        else:
            fc_clicks = 0
        if 'Explore Offers' in ql_count:
            oc_clicks = ql_count['Explore Offers']
        else:
            oc_clicks = 0
        if 'View Brochure' in ql_count:
            bd_clicks = ql_count['View Brochure']
        else:
            bd_clicks = 0
        if 'Service Price' in ql_count:
            sc_clicks = ql_count['Service Price']
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
            'device_id': device_id,
            'this_week_data': graph_data[0],
            'last_week_data': graph_data[1],
            'today': datetime.now().date().strftime("%d-%m-%Y")
        }
        return render(request, self.template_name, args)


def get_clicks(request):
    device_id = request.GET.get('device_id')
    car_name = request.GET.get('car_name')
    car_clicks = ActiveObjects.objects.filter(DeviceID_id=device_id, Name=car_name, InsertedOn__year=datetime.now().year).order_by(
        '-InsertedOn')
    ao_queryset = car_clicks.values('Keyword').annotate(count=Count('Keyword'))
    # Create a dictionary where each name is mapped to its count of occurrences
    ao_count = {}
    for item in ao_queryset:
        ao_count[item['Keyword']] = ao_count.get(item['Keyword'], 0) + item['count']

    # Sort the dictionary items based on their values in descending order
    sorted_items = sorted(ao_count.items(), key=lambda x: x[1], reverse=True)

    # Convert the sorted items back to a dictionary
    ao_count = dict(sorted_items)

    keywords = [key for key, _ in ao_count.items()]
    counts = [value for _, value in ao_count.items()]
    args = {
        'ao_count': ao_count,
        'keywords': keywords,
        'counts': counts
    }
    return JsonResponse(args)


def get_week_data(device_id):
    # device_id = request.GET.get('device_id')
    # device_id = 1
    # Get the current date
    today = datetime.now()

    # Calculate the start and end of this week (Monday to Sunday)
    start_of_this_week = today - timedelta(days=today.weekday())
    # Calculate the start of last week
    start_of_last_week = start_of_this_week - timedelta(weeks=1)

    # Calculate the end of last week (Sunday)
    end_of_last_week = start_of_this_week - timedelta(days=1)
    # end_of_this_week = start_of_this_week + timedelta(days=6)

    # Initialize lists to store counts for each day of the current week and last week
    this_week_counts = [0, 0, 0, 0, 0, 0, 0]
    last_week_counts = [0, 0, 0, 0, 0, 0, 0]

    # # Filter your queryset for this week's data
    # this_week_data_ao = ActiveObjects.objects.filter(DeviceID_id=device_id, InsertedOn__range=[start_of_this_week, end_of_this_week])

    # Get counts for Table1 for this week
    table1_this_week_data = get_week_counts(device_id, ActiveObjects.objects, start_of_this_week, today)
    for item in table1_this_week_data:
        day_index = (item['InsertedOn'].weekday() + 1) % 7  # Monday=0, Sunday=6
        this_week_counts[day_index] += item['count']

    # Get counts for Table1 for last week
    table1_last_week_data = get_week_counts(device_id, ActiveObjects.objects, start_of_last_week, end_of_last_week)
    for item in table1_last_week_data:
        day_index = (item['InsertedOn'].weekday() + 1) % 7  # Monday=0, Sunday=6
        last_week_counts[day_index] += item['count']

    # Get counts for Table2 for this week
    table2_this_week_data = get_week_counts(device_id, QuickLinks.objects, start_of_this_week, today)
    for item in table2_this_week_data:
        day_index = (item['InsertedOn'].weekday() + 1) % 7  # Monday=0, Sunday=6
        this_week_counts[day_index] += item['count']

    # Get counts for Table2 for last week
    table2_last_week_data = get_week_counts(device_id, QuickLinks.objects, start_of_last_week, end_of_last_week)
    for item in table2_last_week_data:
        day_index = (item['InsertedOn'].weekday() + 1) % 7  # Monday=0, Sunday=6
        last_week_counts[day_index] += item['count']

    args = {
        'this_week_counts': this_week_counts,
        'last_week_counts': last_week_counts
    }
    # return JsonResponse(args)
    return this_week_counts, last_week_counts


def get_week_counts(device_id, queryset, start_date, end_date):
    return queryset.filter(DeviceID_id=device_id, InsertedOn__range=[start_date, end_date]).values('InsertedOn').annotate(count=Count('id'))


def get_week_data_all():
    # device_id = request.GET.get('device_id')
    # device_id = 1
    # Get the current date
    today = datetime.now()

    # Calculate the start and end of this week (Monday to Sunday)
    start_of_this_week = today - timedelta(days=today.weekday())
    # Calculate the start of last week
    start_of_last_week = start_of_this_week - timedelta(weeks=1)

    # Calculate the end of last week (Sunday)
    end_of_last_week = start_of_this_week - timedelta(days=1)
    # end_of_this_week = start_of_this_week + timedelta(days=6)

    # Initialize lists to store counts for each day of the current week and last week
    this_week_counts = [0, 0, 0, 0, 0, 0, 0]
    last_week_counts = [0, 0, 0, 0, 0, 0, 0]

    # # Filter your queryset for this week's data
    # this_week_data_ao = ActiveObjects.objects.filter(DeviceID_id=device_id, InsertedOn__range=[start_of_this_week, end_of_this_week])

    # Get counts for Table1 for this week
    table1_this_week_data = get_week_counts_all(ActiveObjects.objects, start_of_this_week, today)
    for item in table1_this_week_data:
        day_index = (item['InsertedOn'].weekday() + 1) % 7  # Monday=0, Sunday=6
        this_week_counts[day_index] += item['count']

    # Get counts for Table1 for last week
    table1_last_week_data = get_week_counts_all(ActiveObjects.objects, start_of_last_week, end_of_last_week)
    for item in table1_last_week_data:
        day_index = (item['InsertedOn'].weekday() + 1) % 7  # Monday=0, Sunday=6
        last_week_counts[day_index] += item['count']

    # Get counts for Table2 for this week
    table2_this_week_data = get_week_counts_all(QuickLinks.objects, start_of_this_week, today)
    for item in table2_this_week_data:
        day_index = (item['InsertedOn'].weekday() + 1) % 7  # Monday=0, Sunday=6
        this_week_counts[day_index] += item['count']

    # Get counts for Table2 for last week
    table2_last_week_data = get_week_counts_all(QuickLinks.objects, start_of_last_week, end_of_last_week)
    for item in table2_last_week_data:
        day_index = (item['InsertedOn'].weekday() + 1) % 7  # Monday=0, Sunday=6
        last_week_counts[day_index] += item['count']

    args = {
        'this_week_counts': this_week_counts,
        'last_week_counts': last_week_counts
    }
    # return JsonResponse(args)
    return this_week_counts, last_week_counts


def get_week_counts_all(queryset, start_date, end_date):
    return queryset.filter(InsertedOn__range=[start_date, end_date]).values('InsertedOn').annotate(count=Count('id'))

