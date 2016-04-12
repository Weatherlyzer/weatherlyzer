from __future__ import unicode_literals

from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    lon = models.FloatField()


class Type(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=63)


class Length(models.Model):
    name = models.CharField(max_length=255)
    length = models.PositiveSmallIntegerField() # hours


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


class Accuracy(models.Model):
    location = models.ForeignKey(Location, related_name="accuracies", null=True, blank=True)
    type = models.ForeignKey(Type, related_name="accuracies", null=True, blank=True)
    length = models.ForeignKey(Length, related_name="accuracies", null=True, blank=True)
    time_range = models.ForeignKey(TimeRange, related_name="accuracies")

    value = models.FloatField()