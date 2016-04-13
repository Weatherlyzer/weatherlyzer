from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from base.models import TimeRange, Type, Length, Location, Forecast, Accuracy


def index(request):
    top_time_range = TimeRange.objects.get(parent=None)
    first_type = Type.objects.first()

    return redirect('accuracy', time_range_id=top_time_range.id, type_id=first_type.id)


def accuracy(request, time_range_id, type_id=None):
    if not type_id:
        type_id = Type.objects.first().id  # but better do avg or so...

    time_range = get_object_or_404(TimeRange, id=time_range_id)
    type = get_object_or_404(Type, id=type_id)

    table = []
    table.append([])
    table[0].append('x')
    lens = Length.objects.order_by('length')
    for l in lens:
        table[0].append(l.length)

    for l in Location.objects.all():
        row = []
        row.append(l.name)
        i = 0
        for a in Accuracy.objects.filter(time_range=time_range, length=lens[i], location=l, type=type).order_by('length__length'):
            row.append(a.value * 100)
            i += 1

        table.append(row)

    return render(request, "basic_view.html", locals())

