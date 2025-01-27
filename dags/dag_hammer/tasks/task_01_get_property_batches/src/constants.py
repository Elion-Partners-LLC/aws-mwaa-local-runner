import os

ALL_PROPERTIES = os.environ.get("ALL_PROPERTIES") == "True"
BATCH_SIZE = int(os.environ.get("BATCH_SIZE"))
RUN_DATE = os.environ.get("RUN_DATE")
TEMP_DATA_STORE_S3_BUCKET_NAME = os.environ.get("TEMP_DATA_STORE_S3_BUCKET_NAME")


CONTAINER_DOWNLOAD_PATH = "/usr/src/data/"
HAMMER_BATCH_S3_KEY = "hammer_batch/{today}/{filename}"

MAIN_QUERY = f"""
WITH properties AS (
    SELECT
        property_id,
        longitude,
        latitude,
        ST_Point(
            TO_NUMBER(longitude, '999D999999999999999999'),
            TO_NUMBER(latitude, '999D999999999999999999')
        ) point,
        1 joiner
    FROM analytics_acquisitions.properties
),
markets AS (
    SELECT *, 1 joiner
    FROM analytics.seed_hammer__market_boundaries
),
points_of_interest AS (
    SELECT *
    FROM analytics.seed_hammer__poi_locations
),
properties_with_markets AS (
    SELECT
        properties.property_id,
        properties.longitude property_long,
        properties.latitude property_lat,
        properties.point property_point,
        markets.market_name,
        markets.geometry market_geometry
    FROM properties
    LEFT JOIN markets ON properties.joiner=markets.joiner
    WHERE ST_Within(property_point, market_geometry)
)
SELECT
    properties_with_markets.property_id,
    properties_with_markets.property_long,
    properties_with_markets.property_lat,
    properties_with_markets.market_name,
    points_of_interest.poi_name,
    points_of_interest.longitude poi_long,
    points_of_interest.latitude poi_lat
FROM properties_with_markets
LEFT JOIN points_of_interest
ON properties_with_markets.market_name=points_of_interest.market_name
WHERE poi_name IS NOT NULL
"""

PROPERTIES_FILTER = """
AND property_id NOT IN (
    SELECT property_id
    FROM hammer.logistics_routes_latest
    WHERE updated_at > current_date - '1 Year'::INTERVAL
)
"""

PROPERTY_QUERY = MAIN_QUERY
if not ALL_PROPERTIES:
    PROPERTY_QUERY = PROPERTY_QUERY + PROPERTIES_FILTER
