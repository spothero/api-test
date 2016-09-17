import unittest

from utils import compare_definition_to_actual


class TestCompare(unittest.TestCase):

    def setUp(self):
        """Common setup methods for all tests"""
        self.definition = {
            'required': ['data'],
            'type': 'object',
            'properties': {
                'notifications': {
                    'items': {'type': 'string'},
                    'type': 'array'
                },
                'data': {
                    'type': 'array',
                    'items': {
                        'required': ['email', 'display_name'],
                        'type': 'object',
                        'properties': {
                            'phone_number': {'type': 'string'},
                            'display_name': {'type': 'string'},
                            'email': {'type': 'string'},
                            'first_name': {'type': 'string'},
                            'last_name': {'type': 'string'},
                            'admin': {'type': 'string'},
                            'vehicles': {
                                'type': 'array',
                                'items': {
                                    'required': ['vehicle_info_id', 'is_default'],
                                    'type': 'object',
                                    'example': {
                                        'is_default': True,
                                        'make_pretty': 'BMW',
                                        'vehicle_info_id': 1234,
                                        'year': 2011,
                                        'make': 'bmw',
                                        'model': '1-series-m',
                                        'model_pretty': '1 Series M'
                                    },
                                    'properties': {
                                        'is_default': {'type': 'boolean'},
                                        'make_pretty': {'type': 'string'},
                                        'vehicle_info_id': {'type': 'integer'},
                                        'year': {'type': 'string'},
                                        'make': {'type': 'string'},
                                        'model': {'type': 'string'},
                                        'model_pretty': {'type': 'string'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        self.actual = {
            u'notifications': [],
            u'data':
                [
                    {
                        u'phone_number': None,
                        u'first_name': u'Lawrence',
                        u'last_name': u'Kiss',
                        u'display_name': u'Lawrence Kiss',
                        u'vehicles': [
                            {
                                u'is_default': True,
                                u'make_pretty': u'BMW',
                                u'vehicle_info_id': 1234,
                                u'year': u'2016',
                                u'make': u'bmw',
                                u'model': u'1-series-m',
                                u'model-pretty': u'1 Series M'
                            }
                        ],
                        u'email': u'lkiss80@hotmail.com',
                    },
                ]
        }

    def test_compare_definition_to_actual(self):
        """Tests basic definition comparison"""
        compare_definition_to_actual(self.definition, self.actual)

    def test_compare_definition_to_actual__all_of(self):
        """Tests definition comparison with an `allOf`"""
        all_of_definition = self.definition['properties']['data']
        all_of_definition['items'] = {'allOf': [all_of_definition['items']]}
        all_of_definition['items']['allOf'].append({
            'required': ['license_plate'],
            'type': 'object',
            'properties': {
                'license_plate': {'type': 'string'},
                'license_plate_id': {'type': 'int'}
            },
            'example': {
                'license_plate': 'abc123',
                'license_plate_id': '123'
            }
        })

        self.actual['data'][0].update({
            'license_plate': 'abc123',
            'license_plate_id': '123'
        })
        compare_definition_to_actual(self.definition, self.actual)


if __name__ == "__main__":
    unittest.main()
