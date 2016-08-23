import json
import logging

from django import test
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from utils import compare_definition_to_actual


User = get_user_model()
logger = logging.getLogger(__name__)


class TestConfigurationException(Exception):
    msg = 'Cannot run test due to improper configuration'

    def __init__(self, msg):
        self.msg = msg


class GetTestCase(test.TransactionTestCase):
    def __init__(self, path, url, parameters, response, test_data=None, methodName='runTest'):
        super(GetTestCase, self).__init__(methodName)
        if test_data is None:
            test_data = dict()
        self.path = path
        self.url = url
        self.parameters = parameters
        self.response = response
        self.test_data = test_data

    def runTest(self):
        client = APIClient()
        test_user = User.objects.create_superuser(username='user', email='user@test.com',
                                                  password='top_secret')
        client.force_authenticate(user=test_user)

        params = dict()
        for parameter in self.parameters:
            test_parameters = self.test_data.get('parameters', dict())
            param_name = parameter['name']
            test_value = test_parameters.get(param_name)
            if not test_value:
                if parameter['required']:
                    raise TestConfigurationException(msg='x-test-data must be defined for required'
                                                     ' parameters')
                else:
                    continue

            param_in = parameter['in']
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

