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


type_dict = {
    'array': list,
    'integer': int,
    'string': str
}


class GetTestCase(test.TransactionTestCase):
    def __init__(self, path, url, parameters, response, test_object=None, methodName='runTest'):
        super(GetTestCase, self).__init__(methodName)
        self.path = path
        self.url = url
        self.parameters = parameters
        self.response = response
        self.test_object = test_object

    def runTest(self):
        # basic_auth = HTTPBasicAuth('lkiss80@hotmail.com', 'larry123')
        # client = APIClient(HTTP_HOST='api.spothero.local')
        client = APIClient()
        test_user = User.objects.create_superuser(username='user', email='user@test.com',
                                                  password='top_secret')
        client.force_authenticate(user=test_user)

        params = dict()
        for parameter in self.parameters:
            logger.info('parameter %s' % parameter)
            param_type = parameter['type']
            if param_type == 'string' and parameter['required']:
                param_val = parameter.get('x-test-data', 'somestring')
                params[parameter['name']] = param_val

        get_response = client.get(self.url, data=params)
        logger.info('RESPONSE: %s' % get_response)
        self.assertEqual(get_response.status_code, self.response['status_code'])
        body = json.loads(get_response.content)
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
