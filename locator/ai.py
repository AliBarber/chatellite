import os

import flag
import humanize
import openai
import pendulum
from pandas import DataFrame, Series

openai.api_key = os.getenv("OPENAI_API_KEY")


def create_greeting_for_satellite(satellite_name) -> str:
    prompt = f"Write me a greeting for a satellite called {satellite_name} that is orbiting the earth."
    openai_response = openai.Completion.create(
        prompt=prompt,
        model="text-davinci-003",
        temperature=0.7,
        max_tokens=128,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.3,
        stop=["."],
    )

    return openai_response["choices"][0]["text"]


def create_responses_for_location_selection(location_selection: DataFrame) -> list[str]:
    prompts_template: list[str] = [
        "I am a satellite flying over earth. Write two sentences describing what I will see from above {}",
        "Describe what I will see looking down over {} in two sentences.",
        "Write two sentences describing {}, don't number them.",
    ]

    prompts = [
        t.format(row[1]["readable_name"])
        for t, row in zip(prompts_template, location_selection[:3].iterrows())
    ]
    ## The bit we've all been waiting for
    openai_response = openai.Completion.create(
        prompt=prompts,
        model="text-davinci-003",
        max_tokens=128,
        presence_penalty=0.20,
        # stop=["."],
    )
    return Series(
        index=location_selection[:3].index,
        data=[
            (
                f"In about {humanize.naturaldelta(location_selection.index[0] - pendulum.now(tz='UTC'))}"
                f" I'll fly over {location_selection['readable_name'][0]} {flag.flag(location_selection['country_is'][0]) if location_selection['country_is'][0] else ''}"
                f" {openai_response['choices'][0]['text']}."
            ),
            ##
            (
                f"Then, {humanize.naturaldelta(location_selection.index[1] - location_selection.index[0])} later,"
                f"{location_selection['readable_name'][1]} {flag.flag(location_selection['country_is'][1]) if location_selection['country_is'][1] else ''}"
                f" {openai_response['choices'][1]['text']}."
            ),
            ##
            (
                f"Later I'll be above {location_selection['readable_name'][2]} {flag.flag(location_selection['country_is'][2]) if location_selection['country_is'][2] else ''}"
                f" {openai_response['choices'][2]['text']}."
            ),
        ],
    )
