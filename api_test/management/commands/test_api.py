import nose
from nose.core import TestProgram
from django.core.management.base import BaseCommand
from django.conf import settings
from optparse import make_option

from api_test.test_tool import run_tests


class Command(BaseCommand):
    def handle(self, *args, **options):
        run_tests()
