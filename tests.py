import json
from unittest import TestCase
from unittest.mock import ANY, create_autospec 

from geopy.geocoders import Nominatim

from find_store.find_store import (
        _convert_units,
        _get_lat_long,
        find_store,
        KILOS_TO_MILES,
        NOT_FOUND,
)

class FindStoreTestCase(TestCase):

    def test_it_should_return_not_found_when_input_not_found(self):
        self.assertIn(NOT_FOUND, find_store({}))

    def test_it_should_return_nearest_store_as_text_when_output_not_json(self):
        args = {'--address': '2472 Whipple Rd Hayward CA'}
        expect = (
            'NEC Industrial Pkwy & Whipple Rd  -  0.07 mi\n'
            '2499 Whipple Rd\n'
            'Hayward CA, 94544-7807'
        )           
        self.assertEqual(expect, find_store(args))

    def test_it_should_return_nearest_store_as_json_when_json(self):
        data = (      
            'Hayward', 'NEC Industrial Pkwy & Whipple Rd', '2499 Whipple Rd', 
            'Hayward', 'CA', '94544-7807', '37.6076346', '-122.0622772', 
            'Alameda County',
        )
        keys = (
            'Store Name', 'Store Location', 'Address', 'City', 'State', 
            'Zip Code', 'Latitude', 'Longitude', 'County',
        )
        expect = dict(zip(keys, data))
        expect['units'] = 'mi'
        expect['distance'] = ANY
        args = {'--address': '2472 Whipple Rd Hayward CA', '--output': 'json'}
        actual = find_store(args)
        self.assertDictEqual(expect, json.loads(actual))

class FindStoreHelpersTestCase(TestCase):

    def setUp(self):
       self.mock_locator = create_autospec(Nominatim)

    def test_get_lat_long_should_be_falsy_when_no_args(self):
        self.assertFalse(_get_lat_long({}))

    def test_get_lat_long_should_get_geocode_when_address(self):
        _get_lat_long({'--address': 'fake address'}, self.mock_locator)
        self.assertTrue(self.mock_locator.geocode.called)

    def test_get_lat_long_should_get_geocode_when_zip(self):
        _get_lat_long({'--zip': '999999'}, self.mock_locator)
        self.assertTrue(self.mock_locator.geocode.called)

    def test_convert_units_should_only_add_unit_when_km(self):
        result = _convert_units({'--units': 'km'}, {})
        self.assertEqual('km', result.get('units'))

    def test_convert_units_should_add_units_and_convert_when_not_km(self):
        result = _convert_units({}, dict(distance=1))
        self.assertEqual('mi', result.get('units'))
        self.assertAlmostEqual(KILOS_TO_MILES, result.get('distance'))

