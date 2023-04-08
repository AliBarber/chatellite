import pendulum
import pytest
from pandas import DataFrame

from locator import geo


@pytest.fixture
def index():
    return [
        pendulum.parse("2023-03-17T21:00:00"),
        pendulum.parse("2023-03-17T21:30:00"),
        pendulum.parse("2023-03-17T22:00:00"),
        pendulum.parse("2023-03-17T22:30:00"),
        pendulum.parse("2023-03-17T23:00:00"),
        pendulum.parse("2023-03-17T23:30:00"),
    ]


def test_determine_location_for_points(index):
    lat_lon_data: DataFrame = DataFrame(
        index=index,
        data={
            "lat": [
                52.8890,
                60.1142,
                -30.4013,
                31.8215,
                0,
                5.5394,
            ],
            "lon": [
                -1.5292,
                22.6000,
                135.3267,
                -83.6486,
                0,
                -23.9450,
            ],
        },
    )

    received_locations = geo.determine_location_for_points(lat_lon_data)

    expected_names = [
        "United Kingdom",
        "Finland",
        "South Australia, Australia",
        "Georgia, United States of America",
    ]
    for response, expected in zip(
        received_locations["readable_name"].to_list(), expected_names
    ):
        assert response == expected
