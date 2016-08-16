import unittest2
import yaml
import json
import logging

import django
from django.conf import settings
from django import test
from django.test.runner import DiscoverRunner
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
User = get_user_model()


from utils import compare_definition_to_actual


logger = logging.getLogger(__name__)


class TestConfigurationException(Exception):
    msg = 'Cannot run test due to improper configuration'

    def __init__(self, msg):
        self.msg = msg


class GetTestCase(test.TransactionTestCase):
    def __init__(self, path, url, parameters, response, test_object=None, methodName='runTest'):
        super(GetTestCase, self).__init__(methodName)
        self.path = path
        self.url = url
        self.parameters = parameters
        self.response = response
        self.test_object = test_object

    def runTest(self):
        client = APIClient()
        test_user = User.objects.create_superuser(username='user', email='user@test.com',
                                                  password='top_secret')
        client.force_authenticate(user=test_user)

        params = dict()
        for parameter in self.parameters:
            test_value = parameter.get('x-test-data')
            if not test_value:
                if parameter['required']:
                    raise TestConfigurationException(msg='x-test-data must be defined for required'
                                                     ' parameters')
                else:
                    continue

            param_in = parameter['in']
            param_name = parameter['name']
            if param_in == 'query':
                params[param_name] = test_value
            elif param_in == 'path':
                self.url = self.url.replace('{%s}' % param_name, str(test_value))

        get_response = client.get(self.url, data=params)
        content = get_response.content
        code = get_response.status_code
        msg = 'code: %s, content: %s' % (code, content)
        self.assertEqual(code, self.response['status_code'], msg)
        body = json.loads(content)
        compare_definition_to_actual(self.response['schema'], body)

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
                    # case = GetTestCase(url)
                    # suite.addTest(case)

        return suite


def run_tests():
    django.setup()
    runner = TestRunner(verbosity=2)

    runner.run_tests([])
