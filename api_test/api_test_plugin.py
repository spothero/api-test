import collections
import logging

from django.conf import settings
from nose.plugins.base import Plugin
from nose.failure import Failure

from test_cases import GetTestCase
import test_generator


logger = logging.getLogger(__name__)


class ApiTest(Plugin):
    # Test classes
    test_classes = []
    # This plugin is incompatible with Django 1.9 parallel testing due to `beforeTest`
    parallel_compatible = False

    def __init__(self):
        super(ApiTest, self).__init__()
        self.url_substring = ''
        self.required_tags = []

    def options(self, parser, env):
        """Nosetests use the deprecated OptionParser framework. If running this module as a
        nose plugin, use `add_option`, otherwise default to the modern ArgParse `add_argument`.
        """
        add_args_kwargs_list = [
            (["--api"],             dict(dest="api", action="store_true", default=False)),
            (["--endpoint-substr"], dict(dest="url_substring", action="store", default='')),
            (["--tags"],            dict(dest="required_tags", action="store", default=None)),
        ]

        if hasattr(parser, 'add_option'):
            for args, kwargs in add_args_kwargs_list:
                parser.add_option(*args, **kwargs)
        else:
            for args, kwargs in add_args_kwargs_list:
                parser.add_argument(*args, **kwargs)

    def configure(self, options, conf):
        self.enabled = options.api
        self.url_substring = options.url_substring
        self.required_tags = options.required_tags.split(',') if options.required_tags else []

    def wantFile(self, file):
        if 'yaml' in file:
            return True
        return False

    def wantClass(self, cls):
        """Signal that we want to run test cases which are derivative of `GetTestCase`"""
        if cls == GetTestCase:
            return True
        return False

    def describeTest(self, test):
        actual_test = test.test
        if isinstance(actual_test, GetTestCase):
            response_code = actual_test.response.get('status_code')
            return 'Testing path %s for response code %s' % (actual_test.path, response_code)
        else:
            return None

    def beforeTest(self, test):
        custom_test = test.test
        if isinstance(custom_test, Failure):
            return
        print 'Testing: %s ' % custom_test.path
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

                if isinstance(object_data, collections.Mapping):
                    self.insert_test_data(object_data, import_func)
                elif isinstance(object_data, collections.Iterable):
                    for data in object_data:
                        self.insert_test_data(data, import_func)

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
        return test_generator.generate_tests(file, self.url_substring, self.required_tags)
