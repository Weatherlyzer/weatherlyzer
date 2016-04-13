from __future__ import unicode_literals

from datetime import timedelta
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
    parent = models.ForeignKey("self", null=True, blank=True, related_name="children")
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __unicode__(self):
        return "Time range: %s - %s" % (self.start, self.end)

    @classmethod
    def get_or_create(cls, start, end, parent_description):
        res = cls.objects.filter(start=start, end=end)
        if res.count():
            return res[0]

        return cls.objects.create(
            start=start,
            end=end,
            parent=cls.get_time_range(start, parent_description),
        )

    @classmethod
    def get_time_range(cls, datetime, interval_description=None):
        if interval_description is None:
            return cls.get_or_create(datetime, datetime, "3 hours")

        if interval_description == "3 hours":
            hour = datetime.hour - (datetime.hour % 3)
            start = datetime.replace(hour=hour, minute=0, second=0, microsecond=0)
            end = start + timedelta(hours=3)
            return cls.get_or_create(start, end, "1 day")

        if interval_description == "1 day":
            start = datetime.replace(hour=0)
            end = start + timedelta(days=1)
            return cls.get_or_create(start, end, "1 month")

        if interval_description == "1 month":
            start = datetime.replace(day=1)
            month = start.month
            end = start + timedelta(days=25)
            while end.month == month:
                end += timedelta(days=1)

            return cls.get_or_create(start, end, "1 year")

        if interval_description == "1 year":
            start = datetime.replace(month=1)
            year = start.year
            end = start + timedelta(days=360)
            while end.year == year:
                end += timedelta(days=1)

            return cls.get_or_create(start, end, "complete")

        if interval_description == "complete":
            start = datetime.replace(year=2000)
            end = datetime.replace(year=2100)
            return cls.get_or_create(start, end, "none")

        return None

    def update(self, include_parent=True):
        if self.children.exists():
            my_accuracies = Accuracy.objects.filter(time_range=self)
            children_accuracies = Accuracy.objects.filter(time_range__in=self.children.all())

            accuracies = []
            bulk_create = False
            if not my_accuracies.exists():
                bulk_create = True

            for type in Type.objects.all():
                for length in Length.objects.all():
                    for location in Location.objects.all():
                        value = children_accuracies.filter(
                            type=type,
                            length=length,
                            location=location,
                        ).aggregate(Avg('value'))['value__avg']

                        if bulk_create:
                            accuracies.append(Accuracy(
                                type=type,
                                length=length,
                                location=location,
                                time_range=self,
                                value=value,
                            ))

                        else:
                            my_accuracies.update_or_create(
                                type=type,
                                length=length,
                                location=location,
                                time_range=self,  # because of creation
                                defaults={'value': value},
                            )

            if bulk_create:
                Accuracy.objects.bulk_create(accuracies)

        if include_parent and self.parent:
            self.parent.update()


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
    location = models.ForeignKey(Location, related_name="accuracies")
    type = models.ForeignKey(Type, related_name="accuracies")
    length = models.ForeignKey(Length, related_name="accuracies")
    time_range = models.ForeignKey(TimeRange, related_name="accuracies")

    value = models.FloatField(default=0)


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
