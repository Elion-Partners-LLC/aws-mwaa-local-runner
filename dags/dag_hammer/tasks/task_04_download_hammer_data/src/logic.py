import logging
import os
import traceback
from datetime import datetime

import shapely
from cloud import get_properties_from_s3, upload_to_s3
from constants import CONTAINER_DOWNLOAD_PATH, RUN_DATE
from hammer_app import HammerAppAPIRequest, RouteSettings, TractorTrailerSettings
from utils import array_json_to_df, flatten_json, get_hammer_api_results

logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)


def main():
    properties = get_properties_from_s3()

    route_settings = RouteSettings()
    truck_settings = TractorTrailerSettings()
    api_request = HammerAppAPIRequest(
        route_settings=route_settings, truck_settings=truck_settings
    )

    data_in_json = []

    for record in properties.to_dict("records"):
        logger.info(
            f"Running query for property: {record['property_id']} "
            f"and destination: {record['poi_name']}"
        )
        property_coords = (record["property_long"], record["property_lat"])
        destination_coords = (record["poi_long"], record["poi_lat"])

        response = get_hammer_api_results(
            property_coords, destination_coords, api_request
        )
        response_json = flatten_json(response)
        response_json["property_id"] = record["property_id"]
        response_json["market_name"] = record["market_name"]
        response_json["poi_name"] = record["poi_name"]
        if "error" not in response_json.keys():
            data_in_json.append(response_json)
        else:
            logger.warning(
                f"Property: {record['property_id']} and POI: "
                f"{record['poi_name']} failed with error: "
                f"{response_json['error']}"
            )

    df = array_json_to_df(data_in_json)

    if df.shape[0] == 0:
        raise ValueError("No property returned data")

    less_than_4_coords = df["route_result_points"].map(len) < 4
    if less_than_4_coords.sum():
        logger.info("Removing routes with less than 4 coordinates")
        removed = df.loc[less_than_4_coords, ["property_id", "poi_name"]]
        df = df.loc[~less_than_4_coords]
        logger.info(f"Removed these properties-poi: {removed.to_dict('records')}")

    df["route_result_points"] = df["route_result_points"].map(shapely.geometry.Polygon)
    df["route_result_points"] = df["route_result_points"].map(
        lambda x: shapely.to_wkb(x, hex=True)
    )

    del df["route_result_itinerary"]
    del df["route_waypoints"]
    df["updated_at"] = RUN_DATE
    df.to_csv(os.path.join(CONTAINER_DOWNLOAD_PATH, "data.csv"), index=False)
    upload_to_s3()


if __name__ == "__main__":
    main()
