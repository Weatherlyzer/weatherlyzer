from base.models import Forecast, Statistics, Length, TimeRange


def get_accuracy(dist, stat):
    return 1.0

def calculate_accuracy(datetime):
    forecasts = Forecast.objects.filter(forecasting=datetime)

    actual_values = forecasts.objects.filter(forecasted_on=datetime)
    statistics = Statistics.objects.all()

    time_range = TimeRange(
        start=datetime,
        end=datetime,
        parent_id=
    )

    for value in actual_values.all():
        related = forecasts.filter(location=value.location, type=value.type)
        statistic, created = statistics.get_or_create(type=value.type)

        for forecast in related.all():
            length = Length.objects.get(forecast.length())
            accuracy = get_accuracy(abs(forecast.value - value.value), statistic)