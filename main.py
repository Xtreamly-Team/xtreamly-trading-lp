from uvicorn import run
from fastapi import FastAPI, Query, Body, BackgroundTasks, HTTPException, File, UploadFile, Depends  # , Depends, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os
import json
from run_copytrading import _run_copytrading
from settings.gmail import _send_user_email
from xtreamly_trading_lp.txExecution.txExecution import *
from xtreamly_trading_lp.globalUtils.getPriceFromPool import *

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

TX_EXECUTOR = TxExecution()

@app.get("/")
def home(): return 'Dalongo AI'

@app.get("/copytrading/")
def _function(
        emails = "pablo.masior@gmail.com;p.masior@gmail.com",
        freq = 1440*7
    ):
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
def deploy_liquidity_endpoint(amount_usdc: int):
    try:
        center_price = float(get_price_from_pool(POOL_CONTRACTS.ETH_USDC))
        current_tick = float(get_current_tick(POOL_CONTRACTS.ETH_USDC))
        percent_bound = 5
        tick_spacing = 60
        tick_lower, tick_upper = get_tick_range_from_current_tick(current_tick, percent_bound, tick_spacing)
        amount_eth = amount_usdc / center_price * (10 ** 18)

        mint_params = MintParams(
            WETH_ADDRESS,
            USDC_ADDRESS,
            3000,
            tick_lower,
            tick_upper,
            int(amount_eth),
            int(amount_usdc),
            EXECUTOR_ADDRESS
        )

        result = TX_EXECUTOR.deploy_liquidity(mint_params)

        if not result:
            raise HTTPException(status_code=500, detail="Liquidity deployment failed.")

        return JSONResponse(content={
            "success": True,
            "tx_result": result
        })

    except Exception as e:
        logger.error(f"main.py - API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error.")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    run(app, host="0.0.0.0", port=port)
