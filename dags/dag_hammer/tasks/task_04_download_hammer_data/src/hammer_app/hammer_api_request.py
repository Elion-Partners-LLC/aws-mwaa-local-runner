import urllib.parse

import requests
from constants import BASE_URL


class HammerAppAPIRequest:
    base_url = BASE_URL

    def __init__(self, route_settings, truck_settings):
        self.route_settings = route_settings
        self.truck_settings = truck_settings
        self.results = None

    def get_request_url(self, origin_coords, destination_coords):
        coords_query_params = dict(
            origin_lat=origin_coords[1],
            origin_lng=origin_coords[0],
            destination_lat=destination_coords[1],
            destination_lng=destination_coords[0],
        )
        url_params = urllib.parse.urlencode(query=coords_query_params)
        route_settings_string = self.route_settings.to_query_string()
        truck_settings_string = self.truck_settings.to_query_string()
        request_url = f"{self.base_url}?{url_params}&settings={route_settings_string}&truck={truck_settings_string}"

        return request_url

    def make_api_request(self, origin_coords, destination_coords):
        request_url = self.get_request_url(origin_coords, destination_coords)
        response = requests.get(request_url)
        if not response.ok:
            response.raise_for_status()

        self.results = response.json()
