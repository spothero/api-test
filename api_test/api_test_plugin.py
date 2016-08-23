import yaml
import logging

from django.core.management import call_command
from django.conf import settings
from nose.plugins.base import Plugin
from nose.failure import Failure

import test_generator


logger = logging.getLogger(__name__)


class ApiTest(Plugin):
    # Test classes
    test_classes = []

    def options(self, parser, env):
        Plugin.options(self, parser, env)
        parser.add_option("--api", dest="api", action="store_true", default=False)

    def configure(self, options, conf):
        Plugin.configure(self, options, conf)
        self.enabled = options.api

    # def prepareTestRunner(self, runner):
    #     from api_test.test_tool import TestRunner
    #     return TestRunner()

    def wantFile(self, file):
        if 'yaml' in file:
            return True
        return False

    def describeTest(self, test):
        actual_test = test.test
        from test_cases import GetTestCase
        if isinstance(actual_test, GetTestCase):
            response_code = actual_test.response.get('status_code')
            return 'Testing path %s for response code %s' % (actual_test.path, response_code)
        else:
            return None

    def beforeTest(self, test):
        custom_test = test.test
        if isinstance(custom_test, Failure):
            return
        data_loader = settings.API_TEST_DATA_LOADER
        if data_loader:
            module, _, func = data_loader.rpartition('.')
            data_loader_mod = __import__(module, fromlist=[func, ])
            import_func = getattr(data_loader_mod, func)
            if not data_loader_mod:
                # TODO make better exception -AK
                raise Exception(msg='Failed data import.')

            test_data = getattr(custom_test, 'test_data')
            if test_data:
                test_copy = test_data.copy()
                object_data = test_copy['data']
                self.insert_test_data(object_data, import_func)

    def insert_test_data(self, object_data, import_func):
        if not object_data:
            return
        for key, value in object_data.items():
            if isinstance(value, dict):
                inserted_object = self.insert_test_data(value, import_func)
                object_data[key] = inserted_object

        if 'model' in object_data:
            target_class = object_data.pop('model')
            return import_func(target_class, object_data)

    def loadTestsFromFile(self, file):
        return test_generator.generate_tests(file)
