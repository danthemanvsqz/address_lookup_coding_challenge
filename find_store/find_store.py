"""
Find Store
  find_store will locate the nearest store (as the vrow flies) from
  store-locations.csv, print the matching store address, as well as
  the distance to that store.

Usage:
  find_store --address=<address>
  find_store --address=<address> [--units=(mi|km)] [--output=(text|json)]
  find_store --zip=<zip>
  find_store --zip=<zip> [--units=(mi|km)] [--output=(text|json)]

Options:
  --zip=<zip>          Find nearest store to this zip code. If there are multiple best-matches, return the first.
  --address=<address>  Find nearest store to this address. If there are multiple best-matches, return the first.
  --units=(mi|km)      Display units in miles or kilometers [default: mi]
  --output=(text|json) Output in human-readable text, or in JSON (e.g. machine-readable) [default: text]

Example
  find_store --address="1770 Union St, San Francisco, CA 94123"
  find_store --zip=94115 --units=km
"""

from csv import DictReader
import json
from math import cos

from docopt import docopt
from geopy.geocoders import Nominatim


OUTPUT = (
    '{Store Location}  -  {distance:.2f} {units}\n{Address}\n{City} {State}, '
    '{Zip Code}'
)
KILOS_TO_MILES = 0.621371
NOT_FOUND = 'Store was not found for input: '


def find_store(arguments):
    """
    Find nearest store and format based on input.

    Args:
        arguments(dict): command line args

    Returns:
        string: nearest store from csv file formated in plain text or json.
    """
    try:
        lat, lng = _get_lat_long(arguments)
    except TypeError:
        return NOT_FOUND + str(arguments)
    data = _get_data()
    store = _find_closest(lat, lng, data)
    store = _convert_units(arguments, store)
    if arguments.get('--output') == 'json':
        return json.dumps(store)
    return OUTPUT.format(**store)
        

def _get_lat_long(arguments, geolocator=None):
    geolocator = geolocator or Nominatim()
    location = None
    if arguments.get('--address'):
        location = geolocator.geocode(arguments['--address'])
    elif arguments.get('--zip'):
        location = geolocator.geocode(arguments['--zip'])
    if location:
        return location.latitude, location.longitude


def _get_data():
    with open('store-locations.csv', 'r') as fh:
        for row in DictReader(fh):
            yield row


def _calculate_distance(lat, lng, row):
    """
    Calculate approximate Euclidean distance.

    Note: breaks down for large distances but we can use geopy's build in
     distance function.
    """
    degree_length = 110.25
    lat0, lng0 = float(row['Latitude']), float(row['Longitude'])
    lat_diff = lat - lat0
    lng_diff = (lng - lng0) * cos(lng0)
    distance = degree_length * (lat_diff**2 + lng_diff**2)**.5 
    return dict(row, distance=distance)


def _find_closest(lat, lng, data):
    distances = (
        _calculate_distance(lat, lng, row)
        for row in data
    )
    return min(distances, key=lambda x: x['distance'])


def _convert_units(arguments, store):
    if arguments.get('--units') == 'km':
        return dict(store, units='km')
    return dict(store, units='mi', distance=store['distance']*KILOS_TO_MILES)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Find Store 1.0')
    print(find_store(arguments))
    
