from __future__ import unicode_literals

from django.db import models
from django.db.models.aggregates import Avg, Max, Min


class Location(models.Model):
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    lon = models.FloatField()


class Type(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=63)


class Length(models.Model):
    name = models.CharField(max_length=255)
    length = models.PositiveSmallIntegerField()  # hours


class TimeRange(models.Model):
    parent_id = models.ForeignKey("self", null=True, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()


class Forecast(models.Model):
    forecasted_on = models.DateTimeField()
    forecasting = models.DateTimeField()

    location = models.ForeignKey(Location, related_name="forecasts")
    type = models.ForeignKey(Type, related_name="forecasts")

    value = models.FloatField()

    def length(self):
        return int(round((self.forecasting - self.forecasted_on).total_seconds() / 3600))

    def get_difference(self, other):
        return abs(self.value - other.value)


class Accuracy(models.Model):
    location = models.ForeignKey(Location, related_name="accuracies", null=True, blank=True)
    type = models.ForeignKey(Type, related_name="accuracies", null=True, blank=True)
    length = models.ForeignKey(Length, related_name="accuracies", null=True, blank=True)
    time_range = models.ForeignKey(TimeRange, related_name="accuracies")

    value = models.FloatField()


class Statistics(models.Model):
    type = models.OneToOneField(Type)
    min = models.FloatField(default=0)
    avg = models.FloatField(default=0)
    max = models.FloatField(default=0)

    @classmethod
    def update_all(cls):
        for type in Type.objects.all():
            stat = cls.objects.get_or_create(type=type)
            stat.update()

    def update(self):
        forecasts = Forecast.objects.filter(type=self.type)

        self.min = 0
        self.avg = 0
        self.max = 0
        if forecasts.exists():
            self.min = forecasts.aggregate(Min('value'))['value__min']
            self.avg = forecasts.aggregate(Avg('value'))['value__avg']
            self.max = forecasts.aggregate(Max('value'))['value__max']

        self.save()

    def get_dimensions(self):
        return self.min, self.avg, self.max
