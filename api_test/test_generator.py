import yaml
from django.conf import settings

import yaml_utils


def generate_tests(spec_file, url_substring='', required_tags=None):
    if not required_tags:
        required_tags = []

    from test_cases import GetTestCase

    with open(spec_file) as spec:
        # parse yaml spec file into a dict-like object
        spec_nodes = yaml.load(spec)

        base_path = spec_nodes['basePath']
        paths = spec_nodes['paths']

        for path_name, values in paths.iteritems():
            url = '//' + settings.PARENT_HOST + base_path + path_name

            # url substring condition
            if url_substring not in url:
                continue

            if 'get' in values.keys():
                get_specification = values['get']
                if get_specification.get('x-test-skip'):
                    continue

                # tag condition: if the current tags match any of the required tags, then we should return it
                tags = get_specification.get('tags', [])
                if required_tags and not set(tags).intersection(set(required_tags)):
                    # continue on to next path
                    #   (Note: after implementing more HTTP methods besides GET, make sure you go
                    #   on to the next method instead of the next path here)
                    continue

                while 1:
                    loaded = inline_swagger_refs(get_specification, spec_nodes)
                    if not loaded:
                        break

                responses = get_specification['responses']
                for code, response in responses.iteritems():
                    if not int(code) == 200:
                        continue  # not yet implemented
                    response['status_code'] = int(code)
                    test_cases = get_specification.get('x-test')
                    parameters = get_specification.get('parameters')
                    if test_cases is None:
                        yield GetTestCase(path_name, url, parameters, response)
                        continue
                    for test_data in test_cases:
                        case = GetTestCase(path_name, url, parameters, response, test_data)
                        yield case
    raise StopIteration


def inline_swagger_refs(target_load_dict, full_swagger):
    def find_ref(node, key, item, **kwargs):
        search = kwargs['search']
        if key == search:
            kwargs[search].append(node)

    ref_nodes = list()
    yaml_utils.traverse_yaml(target_load_dict, find_ref, **{'search': '$ref', '$ref': ref_nodes})
    if not ref_nodes:
        return False

    for ref_node in ref_nodes:
        if '$ref' in ref_node:
            ref_value = ref_node['$ref'].replace('#', '')
            identifiers = ref_value.split('/')
            actual_node = yaml_utils.get_reference(full_swagger, identifiers)
            if not actual_node:
                raise LookupError(msg='unable to find target %s' % ref_node)

            del ref_node['$ref']
            ref_node.update(actual_node[identifiers[-1]])
    return True
