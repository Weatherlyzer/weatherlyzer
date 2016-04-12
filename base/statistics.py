from base.models import Type, Statistics


def update_statistics():
    create_if_not_exists()

    for stat in Statistics.objects.all():
        stat.update()


def create_if_not_exists():
    for type in Type.objects.all():
        if not Statistics.objects.filter(type=type).exists():
            Statistics.objects.create(
                type=type,
                max=0,
                avg=0,
            )
