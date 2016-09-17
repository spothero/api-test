import json
import logging
import datetime
import re
from dateutil import relativedelta

from django import test
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from utils import compare_definition_to_actual
from utils import compare_actual_to_definition


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
        try:
            user = self.test_data['user']
            user_id = user['pk']
            test_user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, KeyError):
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
                    logger.debug(param_name)
                    msg = ('x-test-data must be defined for required parameter: %s' % param_name)
                    raise TestConfigurationException(msg=msg)
                else:
                    continue

            param_in = parameter['in']
            if param_in == 'query':
                param_format = parameter.get('format')
                if parameter['type'] == 'string' and param_format:
                    test_value = self.build_formatted_param(param_format, test_value)
                    pattern = parameter.get('pattern')
                    if pattern:
                        msg = ('test parameter %s does not match defined parameter pattern %s'
                               % (test_value, pattern))
                        self.assertIsNotNone(re.match(pattern, test_value), msg=msg)

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
        compare_actual_to_definition(self.response['schema'], body)

    def build_formatted_param(self, param_format, test_value):
        # check if param is just explicitly defined
        if isinstance(test_value, basestring):
            return test_value

        # build param based on relative inputs
        if param_format == 'dateTime':
            now = datetime.datetime.now()
            now += relativedelta.relativedelta(years=test_value.get('year', 0),
                                               months=test_value.get('month', 0),
                                               days=test_value.get('day', 0),
                                               hours=test_value.get('hour', 0),
                                               minutes=test_value.get('minute', 0),
                                               seconds=test_value.get('second', 0))
            test_value = now.strftime(test_value['format'])
        elif param_format == 'date':
            now = datetime.date.now()
            now += relativedelta.relativedelta(years=test_value.get('year', 0),
                                               months=test_value.get('month', 0),
                                               days=test_value.get('day', 0))
            test_value = now.strftime(test_value['format'])
        return test_value

    def setUp(self):
        super(GetTestCase, self).setUp()

