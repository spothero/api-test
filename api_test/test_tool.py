import os
import unittest2
from unittest2 import TextTestRunner
import argparse
import requests
from requests.auth import HTTPBasicAuth
import yaml
import logging

import django
from django_hosts.resolvers import reverse
from django.conf import settings
from django import test
from django.test.utils import get_runner
from django.test.runner import DiscoverRunner
from rest_framework.test import APIClient, APIRequestFactory

from django.contrib.auth import get_user_model
User = get_user_model()


logger = logging.getLogger(__name__)


class GetTestCase(test.TransactionTestCase):
    def __init__(self, url, methodName='runTest'):
        super(GetTestCase, self).__init__(methodName)
        self.url = url

    def runTest(self):
        # basic_auth = HTTPBasicAuth('lkiss80@hotmail.com', 'larry123')
        # client = APIClient(HTTP_HOST='api.spothero.local')
        client = APIClient()
        test_user = User.objects.create_superuser(username='user', email='user@test.com',
                                                  password='top_secret')
        client.force_authenticate(user=test_user)
        get = client.get(self.url)
        logger.info('RESPONSE: %s' % get)
        self.assertEqual(get.status_code, 200)

    def setUp(self):
        super(GetTestCase, self).setUp()


class TestRunner(DiscoverRunner):
    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        if not settings.API_SPEC:
            return

        suite = unittest2.TestSuite()
        with open(settings.API_SPEC) as spec:
            spec_nodes = yaml.load(spec)
            base_path = spec_nodes['basePath']
            paths = spec_nodes['paths']
            logger.debug('paths %s' % paths)
            for path_name, values in paths.iteritems():
                # logger.debug('path values %s' % values)
                url = '//' + settings.PARENT_HOST + base_path + path_name
                if 'get' in values.keys():
                    logger.info('url %s' % url)
                    case = GetTestCase(url)
                    suite.addTest(case)

        return suite


def run_tests():
    django.setup()
    runner = TestRunner(verbosity=2)

    runner.run_tests([])
