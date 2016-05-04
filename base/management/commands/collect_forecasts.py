from django.core.management.base import BaseCommand, CommandError

from base.collect import collect

class Command(BaseCommand):
  def handle(self, *args, **options):
    collect()