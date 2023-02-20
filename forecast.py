import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)


def generate_forecast(latitude, longitude, start_date, end_date):
    url_base_url = "https://api.open-meteo.com"
    url_api = "v1"
    url_endpoint = "forecast"
    param_latitude = f"latitude={latitude}"
    param_longitude = f"longitude={longitude}"
    param_daily = "daily=temperature_2m_max,temperature_2m_min,sunrise,sunset,rain_sum,showers_sum,snowfall_sum,windspeed_10m_max,windgusts_10m_max,winddirection_10m_dominant&windspeed_unit=ms&timezone=Europe%2FBerlin"
    param_start_date = f"start_date={start_date}"
    param_end_date = f"end_date={end_date}"

    url = f"{url_base_url}/{url_api}/{url_endpoint}?{param_latitude}&{param_longitude}&{param_daily}&{param_start_date}&{param_end_date}"

    response = requests.request("GET", url)
    return json.loads(response.text)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: Python Saas.</h2></p>"


@app.route(
    "/content/api/v1/integration/generate",
    methods=["POST"],
)
def joke_endpoint():
    start_dt = dt.datetime.now()
    json_data = request.get_json()

    if json_data.get("latitude") is None:
        raise InvalidUsage("latitude is required", status_code=400)

    if json_data.get("longitude") is None:
        raise InvalidUsage("longitude is required", status_code=400)

    if json_data.get("start_date") is None:
        raise InvalidUsage("start_date is required", status_code=400)

    if json_data.get("end_date") is None:
        raise InvalidUsage("end_date is required", status_code=400)

    latitude = json_data.get("latitude")
    longitude = json_data.get("longitude")
    start_date = json_data.get("start_date")
    end_date = json_data.get("end_date")

    forecast = generate_forecast(latitude, longitude, start_date, end_date)

    end_dt = dt.datetime.now()

    result = {
        "event_start_datetime": start_dt.isoformat(),
        "event_finished_datetime": end_dt.isoformat(),
        "event_duration": str(end_dt - start_dt),
        "start_date": start_date,
        "end_date": end_date,
        "forecast": forecast,
    }

    return result