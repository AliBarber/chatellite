import random
from contextlib import asynccontextmanager

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pandas import DataFrame
from pendulum import duration, now

from locator.ai import (
    create_greeting_for_satellite,
    create_ocean_response,
    create_responses_for_location_selection,
)
from locator.geo import determine_location_for_points, create_weighting
from locator.logger import logger
from locator.space import get_future_locations

SATELLITE_CATALOGUE: dict[str, int] = {
    "ICEYE-X2": 43800,
    "ICEYE-X4": 44390,
    "ICEYE-X5": 44389,
    "ICEYE-X6": 46497,
    "ICEYE-X7": 46496,
    "ICEYE-X8": 47510,
    "ICEYE-X9": 47506,
    "ICEYE-X11": 48918,
    "ICEYE-X12": 48914,
    "ICEYE-X13": 48916,
    "ICEYE-X14": 51070,
    "ICEYE-X15": 48917,
    "ICEYE-X16": 51008,
    "ICEYE-X17": 52762,
    "ICEYE-X18": 52749,
    "ICEYE-X19": 52758,
    "ICEYE-X20": 52759,
    "ICEYE-X24": 52755,
    "ICEYE-X21": 55049,
    "ICEYE-X27": 55062,
    "SENTINEL-2B": 42063,
    "LANDSAT-9": 49260,
}


# Be careful - there are rate limits on
# celestrak...
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Downloading TLE files")
    for name, catalogue_id in SATELLITE_CATALOGUE.items():
        print(name)
        with open(f"/tmp/{catalogue_id}.tle", "w") as f_h:
            response = requests.get(
                "https://celestrak.org/NORAD/elements/gp.php?CATNR={TRACKING_ID}&FORMAT=tle".format(
                    TRACKING_ID=catalogue_id
                )
            )
            f_h.write(response.content.decode())

    yield


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://chatellite.space",
        "https://chatellite.space",
        "https://chatellite.alastair.ax",
        "http://chatellite.alastair.ax",
        "http://localhost:4567",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PENALTY_FLOOR = 20


def random_greeting() -> str:
    greetings = ["Hello", "Howdy", "Good day", "'Sup"]
    return greetings[random.randint(0, len(greetings) - 1)]


@app.get("/api/greeting/{satellite_name}")
async def conversation(satellite_name: str):
    return {
        "messages": [
            {
                "sender": "user",
                "text": f"{create_greeting_for_satellite(satellite_name)}. Where are you going today?",
            }
        ]
    }


@app.get("/api/conversation/{satellite_name}")
async def conversation(satellite_name: str, duration_hours: int = 3):
    catalogue_number: int = SATELLITE_CATALOGUE[satellite_name.upper()]
    logger.info(f"Getting locations for {satellite_name}")
    lat_lons = get_future_locations(
        catalogue_number,
        duration(hours=duration_hours),
        sample_rate_minutes=2,
    )
    place_names = determine_location_for_points(lat_lons)
    place_names["weight"] = create_weighting(place_names)
    # De-duplicate
    place_names = place_names.loc[
        place_names.shift(-1)["readable_name"] != place_names["readable_name"]
    ]

    place_sample = place_names.sample(n=3, weights="weight").sort_index()

    response = {"messages": []}

    text_responses = create_responses_for_location_selection(place_sample)
    for timestamp, text in zip(text_responses.index, text_responses.array):
        trimmed_text = text.lstrip()
        trimmed_text = trimmed_text.replace("\n\n", " ")

        response["messages"].append(
            {
                "sender": satellite_name,
                "text": trimmed_text.replace("\n", "<br/>"),
                "exact_time_utc": timestamp.strftime("%H:%M:%SUTC"),
            }
        )

    return response


@app.get("/api/catalogue")
async def satellite_catalogue():
    return {"catalogue": [key for key in SATELLITE_CATALOGUE]}


@app.get("/api/readyz")
async def ready():
    return {"status": "ok"}
