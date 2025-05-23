from typing import Union, List
from datetime import datetime

from .domains import Horizons, Symbols
from .XtreamlyAPI import XtreamlyAPI, XtreamlyAPIPath


class VolatilityAPI(XtreamlyAPI):
    def prediction(
            self,
            horizon: str = Horizons.MIN1,
            symbol: str = Symbols.ETH,
    ) -> dict:
        return self.get(XtreamlyAPIPath.VOLATILITY, {
            "symbol": symbol,
            "horizon": horizon
        })

    def historical_prediction(
            self,
            start_date: Union[datetime, int],
            end_date: Union[datetime, int],
            horizon: str = Horizons.MIN1,
            symbol: str = Symbols.ETH,
    ) -> List[dict]:
        return self.get(XtreamlyAPIPath.VOLATILITY_HISTORICAL, {
            "symbol": symbol,
            "horizon": horizon,
            "start_date": int(start_date.timestamp() * 1000) if isinstance(start_date, datetime) else start_date,
            "end_date": int(end_date.timestamp() * 1000) if isinstance(end_date, datetime) else end_date,
        })

    def state(
            self,
            symbol: str = Symbols.ETH,
    ) -> dict:
        return self.get(XtreamlyAPIPath.STATE, {
            "symbol": symbol
        })

    def historical_state(
            self,
            start_date: Union[datetime, int],
            end_date: Union[datetime, int],
            symbol: str = Symbols.ETH,
    ) -> List[dict]:
        return self.get(XtreamlyAPIPath.STATE_HISTORICAL, {
            "symbol": symbol,
            "start_date": int(start_date.timestamp() * 1000) if isinstance(start_date, datetime) else start_date,
            "end_date": int(end_date.timestamp() * 1000) if isinstance(end_date, datetime) else end_date,
        })
