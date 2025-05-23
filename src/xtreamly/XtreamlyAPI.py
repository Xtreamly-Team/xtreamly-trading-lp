import os
import requests


class XtreamlyAPIPath:
    VOLATILITY = "volatility_prediction"
    VOLATILITY_HISTORICAL = "volatility_historical"
    STATE = "state_recognize"
    STATE_HISTORICAL = "state_historical"


class XtreamlyAPI:
    def __init__(self):
        self.base_url = "https://api.xtreamly.io/"
        self.api_key = os.getenv("XTREAMLY_API_KEY")

        if not self.api_key:
            raise EnvironmentError(
                "Missing environment variable: XTREAMLY_API_KEY.\n"
                "Request your API key here: https://xtreamly.io/api"
            )

        self.headers = {
            "x-api-key": self.api_key
        }

    def get(self, path: str, params: dict = None) -> dict:
        url = self.base_url + path
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        return response.json()
