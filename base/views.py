from datetime import datetime, timedelta

from django.shortcuts import render, get_object_or_404

# Create your views here.
from base.models import TimeRange, Type, Length, Location, Accuracy


COLORS = ['#4A6491', '#E74C3C', '#5C832F']


def index(request):

    req_year = int(request.GET.get('year', -1))
    req_month = int(request.GET.get('month', -1))
    req_day = int(request.GET.get('day', -1))
    req_hour = int(request.GET.get('hour', -1))
    req_type_id = request.GET.get('type')
    req_locations_ids = request.GET.getlist('locations')

    time_range_id = None

    # get time range
    time_ranges = TimeRange.objects.all()
    if req_year > 0:
        start_datetime = datetime(
            req_year,
            req_month if req_month > 0 else 1,
            req_day if req_day > 0 else 1,
            req_hour if req_hour >= 0 else 0)
        if req_hour >= 0:
            range_delta = timedelta(hours=3)
        elif req_day > 0:
            range_delta = timedelta(days=1)
        elif req_month > 0:
            range_delta = timedelta(months=1)
        else:
            range_delta = timedelta(year=1)
        end_datetime = start_datetime + range_delta
        time_range = time_ranges.get(start=start_datetime, end=end_datetime)
    else:
        time_range = time_ranges.get(parent=None)  # top range

    # get forecast type
    types = Type.objects.all()
    if req_type_id:
        type = get_object_or_404(Type, id=req_type_id)
    else:
        type = types.order_by('?').first()

    # get locations
    locations = Location.objects.order_by('name')
    if req_locations_ids:
        req_locations = []
        for id in req_locations_ids:
            location = get_object_or_404(Location, id=id)
            req_locations.append(location)
    else:
        req_locations = locations

    # collect values for graph
    table = []
    lens = Length.objects.order_by('length').all()
    for i, location in enumerate(req_locations):
        row = []
        for _l in lens:
            row.append(
                Accuracy.objects.filter(
                    time_range=time_range, length=_l, location=location,
                    type=type
                ).order_by('length__length')[0].value * 100)

        table.append((location.name, COLORS[i], row))

    return render(request, "basic_view.html", locals())
