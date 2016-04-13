from datetime import timedelta
from django.core.management.base import BaseCommand

from base.forecast_to_accuracy import forecast_to_accuracy
from base.models import Accuracy, TimeRange, Forecast


class Command(BaseCommand):
    help = 'Recount whole database'

    def handle(self, *args, **options):
        self.stdout.write("deleting accuracies")
        Accuracy.objects.all().delete()
        self.stdout.write("")

        self.stdout.write("deleting time ranges")
        TimeRange.objects.all().delete()
        self.stdout.write("")

        if not Forecast.objects.exists():
            self.stdout.write("no forecast, ending")
            return

        forecasts = Forecast.objects.order_by('forecasting')
        start_date = forecasts.first().forecasting
        end_date = forecasts.last().forecasting

        while start_date <= end_date:
            self.stdout.write("counting accuracy for %s" % start_date.strftime("%Y-%m-%d %H:%M:%S"))
            forecast_to_accuracy(start_date, False)
            start_date += timedelta(hours=3)

        self.stdout.write("")

        sorted_time_ranges = TimeRange.objects.order_by('-id')

        for time_range in sorted_time_ranges:
            self.stdout.write("counting accuracies for time range %s" % time_range)
            time_range.update(False)
