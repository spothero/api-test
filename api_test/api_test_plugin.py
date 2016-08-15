import yaml
import logging

from django.core.management import call_command
from django.conf import settings
from nose.plugins.base import Plugin

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
        from test_tool import GetTestCase
        if isinstance(actual_test, GetTestCase):
            response_code = actual_test.response.get('status_code')
            return 'Testing path %s for response code %s' % (actual_test.path, response_code)
        else:
            return None

    def beforeTest(self, test):
        custom_test = test.test
        data_loader = settings.API_TEST_DATA_LOADER
        if data_loader:
            module, _, func = data_loader.rpartition('.')
            data_loader_mod = __import__(module, fromlist=[func, ])
            import_func = getattr(data_loader_mod, func)
            if not data_loader_mod:
                # TODO make better exception -AK
                raise Exception(msg='Failed data import.')

            response = custom_test.response

            examples = list()
            self.traverse_yaml(response, self.find_example, **{'examples': examples})
            for example in examples:
                if 'x-test-class' not in example:
                    continue
                target_class = example.pop('x-test-class')
                import_func(target_class, example)

    def loadTestsFromFile(self, file):
        # with open(settings.API_SPEC) as spec:
        #     spec_nodes = yaml.load(spec)
        #     base_path = spec_nodes['basePath']
        #     paths = spec_nodes['paths']
        from test_tool import GetTestCase
        with open(file) as spec:
            spec_nodes = yaml.load(spec)
            base_path = spec_nodes['basePath']
            paths = spec_nodes['paths']
            logger.debug('paths %s' % paths)
            for path_name, values in paths.iteritems():
                # logger.debug('path values %s' % values)
                url = '//' + settings.PARENT_HOST + base_path + path_name
                if 'get' in values.keys():
                    logger.info('url %s' % url)
                    get_specification = values['get']
                    while 1:
                        loaded = self.inline_swagger_refs(get_specification, spec_nodes)
                        if not loaded:
                            break

                    responses = get_specification['responses']
                    for code, response in responses.iteritems():
                        if not int(code) == 200:
                            continue  # not yet implemented
                        fixture_file = get_specification.get('x-test-class')
                        response['status_code'] = int(code)
                        case = GetTestCase(path_name, url, get_specification['parameters'],
                                           response, fixture_file)
                        yield case
        yield False

    def inline_swagger_refs(self, target_load_dict, full_swagger):
        ref_nodes = list()
        self.traverse_yaml(target_load_dict, self.find_ref, **{'search': '$ref',
                                                               '$ref': ref_nodes})
        if not ref_nodes:
            return False

        for ref_node in ref_nodes:
            # _, section, ref_name = ref_node['$ref'].partition('/')
            if '$ref' in ref_node:
                ref_value = ref_node['$ref'].replace('#', '')
                identifiers = ref_value.split('/')
                actual_node = self.get_reference(full_swagger, identifiers)
                if not actual_node:
                    raise LookupError(msg='unable to find target %s' % ref_node)

                del ref_node['$ref']
                ref_node.update(actual_node[identifiers[-1]])
        return True

    def find_ref(self, node, key, item, **kwargs):
        search = kwargs['search']
        if key == search:
            kwargs[search].append(node)

    def find_example(self, node, key, item, **kwargs):
        if key == 'example':
            kwargs['examples'].append(item)

    # def load_ref(self, node, key, item, **kwargs):
    #     if key == kwargs['ref']:
    #         return node

    def get_reference(self, node, identifiers):
        """Recurses through yaml node to find the target key."""
        if len(identifiers) == 1:
            return {identifiers[0]: node[identifiers[0]]}

        if not identifiers[0]:  # skip over any empties
            return self.get_reference(node, identifiers[1:])
        return self.get_reference(node[identifiers[0]], identifiers[1:])

    def traverse_yaml(self, node, function, **kwargs):
        """General function for traversing a dictionary representation of yaml.

            node -- root of yaml dictionary to traverse
            function -- function to be called for all non-structural (dict/list) yaml nodes
            kwargs -- additional arguments to pass into the function
        """
        if not isinstance(node, dict):
            return
        # Changed from iteritems() to items() because if we use iteritems() then when we receive a
        # reference item. So when we update the node item we run into a runtime error because the
        # size of the dictionary changes. However, using items() it returns a copy of the node so
        # modifications wont trigger a run time error.
        for key, item in node.items():
            function(node, key, item, **kwargs)
            if isinstance(item, dict):
                self.traverse_yaml(item, function, **kwargs)

            elif isinstance(item, list):
                for sub_item in item:
                    if isinstance(sub_item, dict):
                        self.traverse_yaml(sub_item, function, **kwargs)
