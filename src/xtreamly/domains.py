from enum import Enum
from pydantic import BaseModel


class VolatilityPrediction(BaseModel):
    timestamp: int
    timestamp_str: str
    volatility: float


class StatePrediction(BaseModel):
    timestamp: int
    timestamp_str: str
    classification: str
    classification_description: str


class Horizons(str, Enum):
    MIN1 = "1min"
    MIN15 = "15min"
    MIN60 = "60min"
    MIN240 = "240min"
    MIN1440 = "1440min"


class Symbols(str, Enum):
    ETH = "ETH"
    BTC = "BTC"