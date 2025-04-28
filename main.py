from uvicorn import run
from fastapi import FastAPI, Query, Body, BackgroundTasks, HTTPException, File, UploadFile, Depends  # , Depends, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os
import json
from run_copytrading import _run_copytrading

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
        name = "Uniswap" 
    ):
    df_opn, df_cls = _run_copytrading()
    return JSONResponse(content={
        'success': True,
        'open': json.loads(df_opn.to_json(orient='records')),
        'close': json.loads(df_cls.to_json(orient='records')),
    })


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    run(app, host="0.0.0.0", port=port)
