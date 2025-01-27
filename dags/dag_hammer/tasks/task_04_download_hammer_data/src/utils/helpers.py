import json
import re
import time

import pandas as pd
from shapely.geometry import Point, Polygon


def flatten_json(json_obj, parent_key="", sep="_"):
    """Flatten a JSON and return it as a dict"""
    items = []
    for key, value in json_obj.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_json(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


def array_json_to_df(data):
    """Convert JSON data into a pandas.DataFrame"""
    data_json = json.dumps(data)
    df = pd.json_normalize(json.loads(data_json))
    return df


def camel_case(s):
    s = re.sub(r"(_|-)+", " ", s).title().replace(" ", "")
    return "".join([s[0].lower(), s[1:]])


def convert_key_values_and_spaces(d):
    new_dict = dict()
    for old_key, value in d.items():
        new_key = camel_case(old_key)
        if isinstance(value, dict):
            new_dict[new_key] = convert_key_values_and_spaces(value)
        elif isinstance(value, str):
            new_dict[new_key] = value.replace(" ", "+")
        else:
            new_dict[new_key] = value

    return new_dict


def get_hammer_api_results(origin_coords, destination_coords, api_request):
    """Calculate the distance and estimated travel time between an origin
    location and a list of destination locations

    Args:
        origin_coords: A tuple of (latitude, longitude) representing the origin location.
        destinations_coords: A list of tuples, where each tuple is a (latitude, longitude) representing a destination location.

    Returns:
        A list of dictionaries, where each dictionary contains the following keys:
        - latitude_origin
        - longitude_origin
        - latitude_destination
        - longitude_destination
        - distance
        - time
    """

    try:
        # Make the API request and extract the route points
        time.sleep(0.5)
        api_request.make_api_request(origin_coords, destination_coords)
        return api_request.results
    except Exception as e:
        return {"error": str(e)}
