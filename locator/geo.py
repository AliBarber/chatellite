import os

from geopandas import GeoDataFrame
from geopandas.tools import sjoin
from pandas import DataFrame, Series

from shapely.geometry import Point

AREA_SHAPEFILE_PATH = os.getenv(
    "AREA_SHAPEFILE_PATH",
    "./Data/test-data/merged-data.shp",
)
WORLD_DATA = GeoDataFrame.from_file(AREA_SHAPEFILE_PATH)


def create_weighting(locations: DataFrame) -> Series:
    """
    As we're in a polar orbit, we're going to be seeing
    a lot of Alaska, Antarctica, remote Russian Oblasts, etc. It'll get boring if everyone
    sees these all of the time. Therefore assign a 'penalty' to anywhere  greater than 65N/S
    Exclude: Iceland, Norway because these are tiny/interesting places
    """

    def lattitude_penalty(row) -> str:
        lat = row["coords"].y
        if (lat > 65) or (lat < -65) and row["country_is"] not in ["IS", "NO"]:
            return 0.1
        if "crimea" in row["readable_name"].lower():
            return 0
        return 1

    return Series(
        index=locations.index, data=locations.apply(lattitude_penalty, axis=1)
    )


def determine_location_for_points(points: DataFrame) -> DataFrame:
    """
    Bit hacky - takes a file that is a union of
    ne_50m_countries and ne_50m_states.
    If we hit upon a duplicate, take the state.
    """

    # Flip them around to lon / lat:
    points_to_search: DataFrame = DataFrame(index=points.index)
    points_to_search["coords"] = points.apply(lambda pt: Point(pt[1], pt[0]), axis=1)
    points_to_search_geo: GeoDataFrame = GeoDataFrame(
        points_to_search, geometry="coords", crs="WGS 84"
    )

    points_and_locations = sjoin(
        points_to_search_geo, WORLD_DATA, predicate="within", how="left"
    )

    # We'll have duplicates if we have hit upon a state
    de_duplicated = points_and_locations.sort_values(["layer"]).drop_duplicates(
        ["coords"], keep="last"
    )

    # Now give them a readable name
    def readable_name(row):
        if not row.isna()["name"]:
            readable_name = f"{row['name']}, {row['geonunit']}"
        else:
            readable_name = row["country_na"]
        row["readable_name"] = readable_name
        return row

    def retrieve_country_code(row, frame=points_and_locations):
        if not row.isna()["country_is"]:
            return row
        # Fish it out from the original
        country_code_search = frame[
            (frame["coords"] == row["coords"]) & (frame["layer"] == "ne_50m_countries")
        ]["country_is"]
        if country_code_search.size:
            row["country_is"] = country_code_search[0]
        else:
            row["country_is"] = ""
        return row

    de_duplicated = de_duplicated.apply(readable_name, axis=1)
    de_duplicated = de_duplicated.apply(
        retrieve_country_code, axis=1, frame=points_and_locations
    )
    return de_duplicated[["readable_name", "coords", "country_is"]].dropna(
        subset="readable_name"
    )
