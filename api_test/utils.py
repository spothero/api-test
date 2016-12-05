type_dict = {
    'array': list,
    'integer': int,
    'string': basestring,
    'boolean': bool,
    'float': float,
    'double': float
}


def compare_definition_to_actual(definition, actual):
    if not isinstance(definition, dict):
        return

    properties = definition.get('properties')
    if not properties:
        return
    required = definition.get('required', list())

    for prop, prop_def in properties.iteritems():
        if prop in required:
            error_msg = 'required property with name %s not found in body' % prop
            if prop not in actual:
                raise AssertionError(error_msg)


        prop_type = get_value(prop_def, 'type')
        if prop_type == 'object' and prop in actual:
            compare_definition_to_actual(prop_def, actual[prop])
        elif prop in actual:
            if prop_type == 'number':
                prop_type = get_value(prop_def, 'format')

            if actual[prop] is not None and not isinstance(actual[prop], type_dict[prop_type]):
                raise AssertionError('%s: expected type %s but got %s instead' %
                                     (prop, prop_type, actual[prop].__class__))
            if prop_type == 'array':
                items = get_value(prop_def, 'items')
                array_item_type = get_value(items, 'type')
                if array_item_type == 'object':
                    try:
                        for item in actual[prop]:
                            compare_definition_to_actual(items, item)
                    except TypeError:
                        raise AssertionError('actual[prop] for prop value of {} is None and can '
                                             'not be iterated over.'.format(prop))
                else:
                    actual_item_type = type_dict[array_item_type]
                    for item in actual[prop]:
                        if not isinstance(item, actual_item_type):
                            raise AssertionError('%s: expected type %s but got %s instead' %
                                                 (prop, prop_type, actual[prop].__cls__))


def compare_actual_to_definition(definition, actual):
    properties = definition.get('properties')
    if not properties:
        return
    try:
        for key, value in actual.iteritems():
            if key not in properties:
                raise AssertionError('Undocumented key returned %s' % key)
            if isinstance(value, dict):
                compare_actual_to_definition(properties[key], value)
            elif isinstance(value, list):
                for v in value:
                    compare_actual_to_definition(properties[key], v)
    except AttributeError:
        raise AssertionError('Actual is of type {} and does not not have iteritems(). '
                             'Definition is of type {}'.format(type(actual), type(definition)))


def combine_all_of_definition(prop_def):
    """Merges `allOf` definitions into a single property definition if present"""
    merged_properties = prop_def['allOf'][0]
    merged_properties['required'] = merged_properties.get('required', [])
    merged_properties['example'] = merged_properties.get('example', {})
    merged_properties['properties'] = merged_properties.get('properties', {})
    for property_definition in prop_def['allOf'][1:]:
        for merge_key in ('properties', 'example'):
            merged_properties[merge_key].update(property_definition.get(merge_key, {}))
        merged_properties['required'] += property_definition.get('required', [])
    return merged_properties


def get_value(prop_def, key):
    try:
        array_item_type = prop_def[key]
    except KeyError:
        if 'allOf' in prop_def:
            return get_value(combine_all_of_definition(prop_def), key)
        raise KeyError('Reference %s does not have attribute %s' % (prop_def, key))
    return array_item_type



