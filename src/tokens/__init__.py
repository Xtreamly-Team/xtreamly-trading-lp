from .token import *
from src.tokens.token_classes import (
    WETHTokenCls,
    USDCTokenCls,
    WBTCTokenCls,
)

WETH = WETHTokenCls()
USDC = USDCTokenCls()
WBTC = WBTCTokenCls()

TOKENS = {
    "WETH": WETH,
    "WBTC": WBTC,
    "USDC": USDC,
}

