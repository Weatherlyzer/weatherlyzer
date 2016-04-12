from base.models import Type, Statistics


def update_statistics():
    for type in Type.objects.all():
        stat = Statistics.objects.get_or_create(type=type)
        stat.update()