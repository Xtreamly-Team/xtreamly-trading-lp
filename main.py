import os
import json
from uvicorn import run
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from run_copytrading import _run_copytrading
from settings.gmail import _send_user_email
from logging import getLogger
from src.uniswapV3 import UniswapV3Lp
from src.tokens import TOKENS
from src.swap import Swap
from src.wallet import get_balances
from src.xtreamly import VolatilityAPI, Symbols

logger = getLogger(__name__)

app = FastAPI(
    title="🕵🏻‍♂️ Xtreamly Trading",
    description='Internal Engine',
    version="0.0.0",
    terms_of_service="xtreamly.io",
    contact={
        "name": "contact",
        "url": "https://xtreamly.io",
        "email": "info@xtreamly.io",
    },
    license_info={
        "name": "Samlpe licence",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

origins = [
    "https://xtreamly.io",
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5000",
    "http://localhost:5001",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home(): return 'Dalongo AI'


@app.get("/copytrading/")
def _function(
        emails="pablo.masior@gmail.com;p.masior@gmail.com",
        freq=1440 * 1
):
    success = 'empty'
    df_opn, df_cls = _run_copytrading(int(freq))
    if len(df_opn) or len(df_cls):
        email_receiver_list = emails.split(';')
        success = _send_user_email(email_receiver_list, df_opn, df_cls)
    return JSONResponse(content={
        'success': success,
        'open': json.loads(df_opn.to_json(orient='records')),
        'close': json.loads(df_cls.to_json(orient='records')),
    })


@app.post("/deploy-liquidity/")
def deploy_liquidity_endpoint(
    amount_usdc: float,
    price_lower: float = None,
    price_upper: float = None,
    token0: str = "WETH",
    token1: str = "USDC",
    fee: str = "0.3%"
):
    try:
        ulp = UniswapV3Lp(TOKENS[token0], TOKENS[token1], fee)
        result = ulp.deploy_liquidity(amount_usdc, price_lower, price_upper)
        return JSONResponse(content={"success": result})
    except Exception as e:
        logger.error(f"API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error.")


@app.get("/positions/")
def get_positions(
    token0: str = "WETH",
    token1: str = "USDC",
    fee: str = "0.3%"
):
    try:
        ulp = UniswapV3Lp(TOKENS[token0], TOKENS[token1], fee)
        return JSONResponse(content= ulp.get_positions())
    except Exception as e:
        logger.error(f"API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error.")


@app.get("/open-positions/")
def get_open_positions(
    token0: str = "WETH",
    token1: str = "USDC",
    fee: str = "0.3%"
):
    try:
        ulp = UniswapV3Lp(TOKENS[token0], TOKENS[token1], fee)
        return JSONResponse(content=ulp.get_open_positions())
    except Exception as e:
        logger.error(f"API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error.")


@app.post("/reduce-liquidity/")
def reduce_liquidity(
    token_id: int,
    percentage_to_remove: int = 100,
    token0: str = "WETH",
    token1: str = "USDC",
    fee: str = "0.3%"
):
    try:
        ulp = UniswapV3Lp(TOKENS[token0], TOKENS[token1], fee)
        result = ulp.reduce_and_collect_liquidity(token_id, percentage_to_remove)
        return JSONResponse(content={"success": result})
    except Exception as e:
        logger.error(f"API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error.")


@app.post("/swap-tokens/")
def swap_tokens(sell_token: str, buy_token: str, sell_amount: float):
    try:
        swap = Swap()
        result = swap.swap(TOKENS[sell_token], TOKENS[buy_token], sell_amount)
        return JSONResponse(content={"success": result})
    except Exception as e:
        logger.error(f"API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error.")


@app.get("/wallet-balances/")
def wallet_balances():
    try:
        return JSONResponse(content=get_balances())
    except Exception as e:
        logger.error(f"API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error.")


@app.get("/volatility-status/")
def volatility_status(
    symbol: Symbols = Symbols.ETH
):
    try:
        api = VolatilityAPI()
        return JSONResponse(content=api.state(symbol))
    except Exception as e:
        logger.error(f"API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error.")
    

@app.get("/volatility-prediction/")
def volatility_prediction(
    horizon: str = "1440min",
    symbol: Symbols = Symbols.ETH
):
    try:
        api = VolatilityAPI()
        return JSONResponse(content=api.prediction(horizon, symbol))
    except Exception as e:
        logger.error(f"API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error.")    


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    run(app, host="0.0.0.0", port=port)
