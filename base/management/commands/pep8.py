import os

from django.core.management.base import BaseCommand

import base


class Command(BaseCommand):
    help = 'Run PEP8 on the whole project.'

    def handle(self, *args, **kwargs):
        project_dir = os.path.join(base.__path__[0], '..')
        rc = os.system("pep8 --filename '*.py' {}".format(project_dir))
        if rc == 0:
            self.stdout.write(self.style.SUCCESS(
                'Successfully passed PEP8 test.'))
        else:
            self.stderr.write(self.style.ERROR(
                'Failed PEP8 test with return code {}.'.format(rc)))
