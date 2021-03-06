from django.http import JsonResponse
from django.shortcuts import render

from base.models import TimeRange, Type, Length, Location, Accuracy


COLORS = ['#4A6491', '#E74C3C', '#5C832F']
DEFAULT_FORECAST_TYPE = 'Temperature'


def index(request):
    types = _available_forecasts()
    locations = _available_locations()
    years = _available_years()
    return render(request, "view.html",
                  {'types': types, 'locations': locations, 'years': years})


def _available_forecasts():
    forecasts_db = Type.objects.order_by('name')
    forecasts = [{'id': forecast.id, 'name': forecast.name,
                  'default': forecast.name == DEFAULT_FORECAST_TYPE}
                 for forecast in forecasts_db]
    return forecasts


def _available_locations():
    locations_db = Location.objects.order_by('name')
    locations = [{'id': location.id, 'name': location.name}
                 for location in locations_db]
    return locations


def _available_years():
    time_range = _time_range()
    years = [child.start.year for child in time_range.children.all()]
    return years


def weatherlyzer_js(request):
    return render(request, "weatherlyzer.js")


def graph_data(request):
    req_year = _minus_one_is_none(int(request.POST.get('year')))
    req_month = _minus_one_is_none(int(request.POST.get('month')))
    req_day = _minus_one_is_none(int(request.POST.get('day')))
    req_hour = _minus_one_is_none(int(request.POST.get('hour')))
    req_type_id = request.POST.get('type')
    req_locations_ids = request.POST.getlist('locations[]')

    lens = Length.objects.order_by('length').all()
    req_locations = Location.objects.filter(id__in=req_locations_ids)
    time_range = _time_range(req_year, req_month, req_day, req_hour)
    type = Type.objects.get(id=req_type_id)

    table = []
    for i, location in enumerate(req_locations):
        accuracies = [
            Accuracy.objects.get(time_range=time_range, length=len,
                                 location=location, type=type).value * 100
            for len in lens
        ]
        table.append({'label': location.name, 'color': COLORS[i],
                      'accuracies': list(reversed(accuracies))})

    deltas = ['-{}'.format(len.length) for len in lens]

    return JsonResponse({'table': table, 'deltas': deltas})


def _minus_one_is_none(number):
    return None if number == -1 else number


def available_months(request):
    req_year = int(request.POST.get('year'))

    time_range = _time_range(req_year)
    months = [{'id': child.start.month, 'name': child.start.strftime('%B')}
              for child in time_range.children.all()]

    return JsonResponse({'months': months})


def available_days(request):
    req_year = int(request.POST.get('year'))
    req_month = int(request.POST.get('month'))

    time_range = _time_range(req_year, req_month)
    days = [{'id': child.start.day, 'name': child.start.day}
            for child in time_range.children.all()]

    return JsonResponse({'days': days})


def available_hours(request):
    req_year = int(request.POST.get('year'))
    req_month = int(request.POST.get('month'))
    req_day = int(request.POST.get('day'))

    time_range = _time_range(req_year, req_month, req_day)
    hours = [{'id': child.start.hour,
              'name': '{}.00 - {}.00'.format(child.start.hour, child.end.hour)}
             for child in time_range.children.all()]

    return JsonResponse({'hours': hours})


def _time_range(year=None, month=None, day=None, hour=None):
    """Recursively find TimeRange starting on given moment"""

    time_ranges = TimeRange.objects.all()
    top_time_range = time_ranges.get(parent=None)

    if not year:
        return top_time_range

    year_time_range = next(
        (time_range for time_range in top_time_range.children.all()
         if time_range.start.year == year),
        None)

    if not month:
        return year_time_range

    month_time_range = next(
        (time_range for time_range in year_time_range.children.all()
         if time_range.start.month == month),
        None)

    if not day:
        return month_time_range

    day_time_range = next(
        (time_range for time_range in month_time_range.children.all()
         if time_range.start.day == day),
        None)

    if not hour:
        return day_time_range

    hour_time_range = next(
        (time_range for time_range in day_time_range.children.all()
         if time_range.start.hour == hour),
        None)

    return hour_time_range
