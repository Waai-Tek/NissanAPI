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

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.http import require_POST
import json


sys.path.insert(0, '..')
from API.models import Devices, DeviceAnalytics, ActiveObjects, QuickLinks, UserProfile


class LoginView(TemplateView):
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request):
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print('User logged in successfully')
            if request.user.groups.filter(name="Admin").exists():
                return redirect('landing')
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
        if request.user.groups.filter(name="Admin").exists() or request.user.groups.filter(name="SuperAdmin").exists():
            # Get the latest insertion time for each foreign key ID
            latest_insertion_times = DeviceAnalytics.objects.values('DeviceID_id').annotate(
                latest_insertion_time=Max('InsertedOn'))
            formatted_times = []

            for item in latest_insertion_times:
                formatted_time = item['latest_insertion_time'].strftime('%Y-%m-%d %H:%M:%S.%f')
                formatted_times.append({
                    'DeviceID_id': item['DeviceID_id'],
                    'latest_insertion_time': formatted_time
                })

            # print(formatted_times)
            # print(latest_insertion_times)
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
        else:
            return redirect('landing')


class IndividualDeviceAnalyticsView(TemplateView):
    template_name = 'Analytics/Analytics.html'

    def get(self, request, *args, **kwargs):
        if request.user.groups.filter(name="User").exists() or request.user.groups.filter(
                name="Admin").exists() or request.user.groups.filter(name="SuperAdmin").exists():

            device_id = self.kwargs['device_id']
            graph_data = get_range_data(device_id, request)
            graph_data_1 = get_week_data(device_id, request)
            # reset = request.session.get('reset')
            reset = request.session.get('reset', True)
            apply = request.session.get('apply', False)
            # THIS IS FOR THE DATE RANGE

            if apply:
                start_date = request.session.get('date_range_start')
                end_date = request.session.get('date_range_end')
            else:
                start_date = '2024-01-01 00:01'
                end_date = datetime.now().strftime('%Y-%m-%d' + ' 23:59')

            # Fetch analytics data for the selected date range
            cars_clicks = ActiveObjects.objects.filter(DeviceID_id=device_id,
                                                       InsertedOn__range=[start_date, end_date]).order_by('-InsertedOn')
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
                                                 InsertedOn__range=[start_date, end_date]).order_by('-InsertedOn')
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

            # THIS IS FOR THE TOTAL

            cars_clicks_t = ActiveObjects.objects.filter(DeviceID_id=device_id,
                                                       InsertedOn__year=datetime.now().year).order_by('-InsertedOn')
            total_interactions_t = cars_clicks_t.count()
            # Query to annotate the count of occurrences of each value in your_field
            queryset_t = cars_clicks_t.values('Name').annotate(count=Count('Name'))
            # Create a dictionary where each name is mapped to its count of occurrences
            cars_count_t = {}
            for item in queryset_t:
                cars_count_t[item['Name']] = cars_count_t.get(item['Name'], 0) + item['count']

            # Sort the dictionary items based on their values in descending order
            sorted_items_t = sorted(cars_count_t.items(), key=lambda x: x[1], reverse=True)

            # Convert the sorted items back to a dictionary
            cars_count_t = dict(sorted_items_t)



            ql_click_t = QuickLinks.objects.filter(DeviceID_id=device_id,
                                                InsertedOn__year=datetime.now().year).order_by('-InsertedOn')

            total_interactions_t += ql_click_t.count()
            # Query to annotate the count of occurrences of each value in your_field
            ql_queryset_t = ql_click_t.values('Name').annotate(count=Count('Name'))
            # Create a dictionary where each name is mapped to its count of occurrences
            ql_count_t = {}
            for item in ql_queryset_t:
                ql_count_t[item['Name']] = ql_count_t.get(item['Name'], 0) + item['count']
            if 'Finance Calculator' in ql_count_t:
                fc_clicks_t = ql_count_t['Finance Calculator']
            else:
                fc_clicks_t = 0
            if 'Explore Offers' in ql_count_t:
                oc_clicks_t = ql_count_t['Explore Offers']
            else:
                oc_clicks_t = 0
            if 'View Brochure' in ql_count_t:
                bd_clicks_t = ql_count_t['View Brochure']
            else:
                bd_clicks_t = 0
            if 'Service Price' in ql_count_t:
                sc_clicks_t = ql_count_t['Service Price']
            else:
                sc_clicks_t = 0

            device_name = Devices.objects.get(id=device_id).Name

            args = {
                'device_name': device_name,
                'cars_count': cars_count,
                'cars_count_t': cars_count_t,
                'total_interactions': total_interactions,
                'total_interactions_t': total_interactions_t,
                'ql_count': ql_count,
                'ql_count_t': ql_count_t,
                'fc_clicks': fc_clicks,
                'fc_clicks_t': fc_clicks_t,
                'oc_clicks': oc_clicks,
                'oc_clicks_t': oc_clicks_t,
                'bd_clicks': bd_clicks,
                'bd_clicks_t': bd_clicks_t,
                'sc_clicks': sc_clicks,
                'sc_clicks_t': sc_clicks_t,
                'device_id': device_id,
                'data_range_data': graph_data[0],
                'date_list': graph_data[1],
                'this_week_data': graph_data_1[0],
                'last_week_data': graph_data_1[1],
                'today': datetime.now().date().strftime("%d-%m-%Y"),
                'start_date': start_date[:10],
                'end_date': end_date[:10],
                'apply': apply,
                'reset': reset
            }
            return render(request, self.template_name, args)
        else:
            return redirect('landing')




def get_clicks(request):
    device_id = request.GET.get('device_id')
    car_name = request.GET.get('car_name')

    reset = request.session.get('reset', True)
    apply = request.session.get('apply', False)
    # THIS IS FOR THE DATE RANGE

    if apply:
        start_date = request.session.get('date_range_start')
        end_date = request.session.get('date_range_end')
    else:
        start_date = '2024-01-01 00:01'
        end_date = datetime.now().strftime('%Y-%m-%d' + ' 23:59')


    # If the date range is not available in the session, use the current year
    if apply:
        car_clicks = ActiveObjects.objects.filter(
            DeviceID_id=device_id,
            Name=car_name,
            InsertedOn__range=[start_date, end_date]
        ).order_by('-InsertedOn')
    else:
        start_date = '2024-01-01 00:01'
        car_clicks = ActiveObjects.objects.filter(
            DeviceID_id=device_id,
            Name=car_name,
            # InsertedOn__year=datetime.now().year
            InsertedOn__range=[start_date, end_date]
        ).order_by('-InsertedOn')

    ao_queryset = car_clicks.values('Keyword').annotate(count=Count('Keyword'))

    ao_count = {}
    for item in ao_queryset:
        ao_count[item['Keyword']] = ao_count.get(item['Keyword'], 0) + item['count']

    sorted_items = sorted(ao_count.items(), key=lambda x: x[1], reverse=True)
    ao_count = dict(sorted_items)

    keywords = [key for key, _ in ao_count.items()]
    counts = [value for _, value in ao_count.items()]
    args = {
        'ao_count': ao_count,
        'keywords': keywords,
        'counts': counts
    }
    return JsonResponse(args)


def get_range_data(device_id, request):

    reset = request.session.get('reset', True)
    apply = request.session.get('apply', False)
    # THIS IS FOR THE DATE RANGE

    if apply:
        start_date = request.session.get('date_range_start')
        end_date = request.session.get('date_range_end')
    else:
        start_date = '2024-01-01 00:01'
        end_date = datetime.now().strftime('%Y-%m-%d' + ' 23:59')

    start_date_1 = datetime.strptime(start_date[:10], '%Y-%m-%d')
    end_date_1 = datetime.strptime(end_date[:10], '%Y-%m-%d')
    num_days = (end_date_1 - start_date_1).days + 1

    date_range_count = [0] * num_days
    date_list = [""] * num_days

    # Get counts for Table1 for this week
    table1_date_range_data = get_week_counts(device_id, ActiveObjects.objects, start_date, end_date)
    for item in table1_date_range_data:
        day_index = (item['InsertedOn'] - start_date_1).days
        date_range_count[day_index] += item['count']

    for day_index in range(num_days):
        date_list[day_index] = (start_date_1 + timedelta(days=day_index)).strftime('%m/%d')

    # Get counts for Table2 for this week
    table2_date_range_data = get_week_counts(device_id, QuickLinks.objects, start_date, end_date)
    for item in table2_date_range_data:
        day_index = (item['InsertedOn'] - start_date_1).days
        date_range_count[day_index] += item['count']

    args = {
        'date_range_counts': date_range_count,
        'date_range': date_list
    }

    # return JsonResponse(args)
    return date_range_count, date_list


def get_week_data(device_id, request):

    today = datetime.now()

    # Calculate the start and end of this week (Monday to Sunday)
    start_of_this_week = today - timedelta(days=today.weekday())
    start_of_this_week = start_of_this_week.replace(hour=0, minute=1, second=0, microsecond=0)

    # print(f'Start of this week: {start_of_this_week}')
    # Calculate the start of last week
    start_of_last_week = start_of_this_week - timedelta(weeks=1)
    start_of_last_week = start_of_last_week.replace(hour=23, minute=59, second=59, microsecond=0)
    # print(f'Start of last week: {start_of_last_week}')

    # Calculate the end of last week (Sunday)
    end_of_last_week = start_of_this_week - timedelta(days=1)
    end_of_last_week = end_of_last_week.replace(hour=23, minute=59, second=59, microsecond=0)
    # print(f'End of last week: {end_of_last_week}')
    # end_of_this_week = start_of_this_week + timedelta(days=6)

    # Initialize lists to store counts for each day of the current week and last week
    this_week_counts = [0, 0, 0, 0, 0, 0, 0]
    last_week_counts = [0, 0, 0, 0, 0, 0, 0]

    # # Filter your queryset for this week's data
    # this_week_data_ao = ActiveObjects.objects.filter(DeviceID_id=device_id, InsertedOn__range=[start_of_this_week, end_of_this_week])

    # Get counts for Table1 for this week
    table1_this_week_data = get_week_counts(device_id, ActiveObjects.objects, start_of_this_week, today)
    for item in table1_this_week_data:
        day_index = (item['InsertedOn'].weekday()) % 7  # Monday=0, Sunday=6
        this_week_counts[day_index] += item['count']
        # print(this_week_counts[day_index])

    # Get counts for Table1 for last week
    table1_last_week_data = get_week_counts(device_id, ActiveObjects.objects, start_of_last_week, end_of_last_week)
    # table1_last_week_data = get_week_counts(device_id, ActiveObjects.objects, start_of_last_week, end_of_last_week)
    for item in table1_last_week_data:
        day_index = (item['InsertedOn'].weekday()) % 7  # Monday=0, Sunday=6
        last_week_counts[day_index] += item['count']

    # Get counts for Table2 for this week
    table2_this_week_data = get_week_counts(device_id, QuickLinks.objects, start_of_this_week, today)
    # table2_this_week_data = get_week_counts(device_id, QuickLinks.objects, start_of_this_week, today)
    for item in table2_this_week_data:
        day_index = (item['InsertedOn'].weekday()) % 7  # Monday=0, Sunday=6
        this_week_counts[day_index] += item['count']

    # Get counts for Table2 for last week
    table2_last_week_data = get_week_counts(device_id, QuickLinks.objects, start_of_last_week, end_of_last_week)
    # table2_last_week_data = get_week_counts(device_id, QuickLinks.objects, start_of_last_week, end_of_last_week)
    for item in table2_last_week_data:
        day_index = (item['InsertedOn'].weekday()) % 7  # Monday=0, Sunday=6
        last_week_counts[day_index] += item['count']

    # print(this_week_counts)

    args = {
        'this_week_counts': this_week_counts,
        'last_week_counts': last_week_counts
    }

    # return JsonResponse(args)
    return this_week_counts, last_week_counts


def get_week_counts(device_id, queryset, start_date, end_date):
    return queryset.filter(DeviceID_id=device_id, InsertedOn__range=[start_date, end_date]).values(
        'InsertedOn').annotate(count=Count('id'))


def get_week_data_all():
    today = datetime.now()

    # Calculate the start and end of this week (Monday to Sunday)
    start_of_this_week = today - timedelta(days=today.weekday())
    start_of_this_week = start_of_this_week.replace(hour=0, minute=1, second=0, microsecond=0)

    # print(f'Start of this week: {start_of_this_week}')
    # Calculate the start of last week
    start_of_last_week = start_of_this_week - timedelta(weeks=1)
    start_of_last_week = start_of_last_week.replace(hour=23, minute=59, second=59, microsecond=0)
    # print(f'Start of last week: {start_of_last_week}')

    # Calculate the end of last week (Sunday)
    end_of_last_week = start_of_this_week - timedelta(days=1)
    end_of_last_week = end_of_last_week.replace(hour=23, minute=59, second=59, microsecond=0)
    # print(f'End of last week: {end_of_last_week}')
    # end_of_this_week = start_of_this_week + timedelta(days=6)E

    # Initialize lists to store counts for each day of the current week and last week
    this_week_counts = [0, 0, 0, 0, 0, 0, 0]
    last_week_counts = [0, 0, 0, 0, 0, 0, 0]
    # # Filter your queryset for this week's data
    # this_week_data_ao = ActiveObjects.objects.filter(DeviceID_id=device_id, InsertedOn__range=[start_of_this_week, end_of_this_week])

    # Get counts for Table1 for this week
    table1_this_week_data = get_week_counts_all(ActiveObjects.objects, start_of_this_week, today)
    for item in table1_this_week_data:
        day_index = (item['InsertedOn'].weekday()) % 7  # Monday=0, Sunday=6
        this_week_counts[day_index] += item['count']

    # Get counts for Table1 for last week
    table1_last_week_data = get_week_counts_all(ActiveObjects.objects, start_of_last_week, end_of_last_week)
    for item in table1_last_week_data:
        day_index = (item['InsertedOn'].weekday()) % 7  # Monday=0, Sunday=6
        last_week_counts[day_index] += item['count']

    # Get counts for Table2 for this week
    table2_this_week_data = get_week_counts_all(QuickLinks.objects, start_of_this_week, today)
    for item in table2_this_week_data:
        day_index = (item['InsertedOn'].weekday()) % 7  # Monday=0, Sunday=6
        this_week_counts[day_index] += item['count']

    # Get counts for Table2 for last week
    table2_last_week_data = get_week_counts_all(QuickLinks.objects, start_of_last_week, end_of_last_week)
    for item in table2_last_week_data:
        day_index = (item['InsertedOn'].weekday()) % 7  # Monday=0, Sunday=6
        last_week_counts[day_index] += item['count']

    args = {
        'this_week_counts': this_week_counts,
        'last_week_counts': last_week_counts
    }
    # return JsonResponse(args)
    return this_week_counts, last_week_counts


def get_week_counts_all(queryset, start_date, end_date):
    return queryset.filter(InsertedOn__range=[start_date, end_date]).values('InsertedOn').annotate(count=Count('id'))


def landing_redirection(request):
    if request.user.groups.filter(name="Admin").exists() or request.user.groups.filter(name="SuperAdmin").exists():
        return redirect('AllDeviceAnalytics')
    elif request.user.groups.filter(name="User").exists():
        device_id = UserProfile.objects.get(user=request.user).DeviceID_id
        return redirect('IndividualDeviceAnalytics', device_id=device_id)
    # update_data()
    else:
        return redirect('login')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update session to reflect the new password
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('landing')  # Redirect to profile or any other page
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})



# Actually work
@require_POST
def date_apply(request):
    try:
        data = json.loads(request.body)
        start = data.get('start')
        end = data.get('end')
        print(f"Start Date: {start}, End Date: {end}")
        print('Apply CLICKED')

        # Store the date range in session
        request.session['apply'] = True
        request.session['reset'] = False
        request.session['date_range_start'] = start
        request.session['date_range_end'] = end

        device_id = request.session.get('device_id')
        print(f"Device ID: {device_id}")
        return JsonResponse({'message': 'Date range applied successfully'})
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return JsonResponse({'error': 'An error occurred'}, status=500)


def reset_trigger(request):
    if request.method == 'POST':
        # Perform any reset logic here, such as updating session data
        request.session['reset'] = True  # Example of setting a session variable
        print('Reset CLICKED')
        request.session['apply'] = False
        get_clicks(request)

        # Return a JSON response
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'invalid request'}, status=400)