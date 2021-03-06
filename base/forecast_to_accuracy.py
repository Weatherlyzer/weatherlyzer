from base.models import Forecast, Statistics, Length, TimeRange, Accuracy


def get_accuracy(dist, dim):
    min, avg, max = dim

    if dist <= min: return 1.0
    if dist >= max: return 0.0

    accuracy = 1.0
    percents = 0.5

    ratio = 1.0 * (avg - min) / (max - min)

    a = max - min
    b = avg - min
    dist -= min

    while percents > 0.0001:
        if dist > b:
            accuracy -= percents
            dist -= b
            a -= b

        else:
            a = b

        b = a * ratio
        percents /= 2

    return accuracy


def forecast_to_accuracy(datetime, update=True):
    existing_time_ranges = TimeRange.objects.filter(start=datetime, end=datetime)
    if existing_time_ranges.exists():
        existing_time_ranges.delete()

    forecasts = Forecast.objects.filter(forecasting=datetime)

    actual_values = forecasts.filter(forecasted_on=datetime)
    statistics = Statistics.objects.all()

    accuracies = []

    time_range = TimeRange.get_time_range(datetime)
    for result in actual_values.all():
        related = forecasts.filter(location=result.location, type=result.type)
        stat, created = statistics.get_or_create(type=result.type)

        for forecast in related.all():
            length = Length.objects.get(length=forecast.length())
            difference = result.get_difference(forecast)
            accuracy = get_accuracy(difference, stat.get_dimensions())

            accuracies.append(Accuracy(
                location=result.location,
                type=result.type,
                length=length,
                time_range=time_range,
                value=accuracy,
            ))

    Accuracy.objects.bulk_create(accuracies)

    if update:
        time_range.parent.update()
