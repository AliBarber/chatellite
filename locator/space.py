import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Tuple

import pendulum
from pandas import DataFrame
from skyfield.api import load, wgs84

from locator.logger import logger

TLE_FILE_OR_URL_TEMPLATE = os.getenv(
    "TLE_FILE_OR_URL_TEMPLATE",
    "https://celestrak.org/NORAD/elements/gp.php?CATNR={TRACKING_ID}&FORMAT=tle",
)


def get_future_locations(
    satellite_tracking_id: int,
    duration: pendulum.Duration,
    tle_file_template=TLE_FILE_OR_URL_TEMPLATE,
    sample_rate_minutes=5,
) -> DataFrame:
    temp_dir = TemporaryDirectory()
    tle_file = Path(temp_dir.name) / f"{satellite_tracking_id}.tle"

    satellite_from_tle = load.tle_file(
        tle_file_template.format(TRACKING_ID=satellite_tracking_id),
        filename=str(tle_file),
    )[0]

    period = pendulum.period(
        pendulum.now(tz="UTC") + pendulum.duration(minutes=2),
        pendulum.now(tz="UTC") + duration,
    )
    timescale = load.timescale()

    lat_lon: list[Tuple[pendulum.DateTime, float, float]] = []
    for point_time in period.range("minutes", sample_rate_minutes):
        pt = wgs84.latlon_of(satellite_from_tle.at(timescale.utc(point_time)))
        lat_lon.append((point_time, pt[0].degrees, pt[1].degrees))
    logger.info(f"Got {len(lat_lon)} points for {satellite_tracking_id}")
    return DataFrame(
        index=[pt[0] for pt in lat_lon],
        data={"lat": [pt[1] for pt in lat_lon], "lon": [pt[2] for pt in lat_lon]},
    )
