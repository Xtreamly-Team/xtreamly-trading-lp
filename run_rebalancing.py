# %reset -f
import os
import json
import numpy as np
from uvicorn import run
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from settings.gmail import _send_user_email
from logging import getLogger
from src.uniswapV3 import UniswapV3Lp
from src.tokens import TOKENS
from src.swap import Swap
from src.wallet import get_balances
from src.xtreamly import VolatilityAPI, Symbols
from src.tokens import Token, WETH

logger = getLogger(__name__)

def _uni_init(p, v, p_a, p_b):
    p_lower = min(p_a, p_b)
    p_upper = max(p_a, p_b)
    sqrt_p = np.sqrt(p)
    sqrt_pl = np.sqrt(p_lower)
    sqrt_pu = np.sqrt(p_upper)
    L_trial = 1
    amt0 = L_trial * (sqrt_pu - sqrt_p) / (sqrt_p * sqrt_pu)
    amt1 = L_trial * (sqrt_p - sqrt_pl)
    val0 = amt0 * p
    val1 = amt1
    total_val = val0 + val1
    scale = v / total_val
    x = amt0 * scale
    y = amt1 * scale
    L = L_trial * scale
    pos_uni = {
        'x': x, 
        'y': y, 
        'p_a': p_a, 
        'p_b': p_b, 
        'L': L, 
        'inv_usd': v,
        }
    return pos_uni

vol_thres = {
    'BTC': 0.016668227,
    'ETH': 0.02214743375,
    }

concentration = .2
move = .2
cash_keep = .01

def _rebalancing(
    benchmark_vol: str = "ETH",
    horizon: str = "1440min",
    token0: str = "WETH",
    token1: str = "USDC",
    fee: str = "0.3%"        
    ):
    # xtreamly prediction   
    try:
        api = VolatilityAPI()
        xly_vol = api.prediction(horizon, benchmark_vol)
        vol = xly_vol['volatility']
    except Exception as e:
        logger.error(f"get_balances: {e}", exc_info=True)
        return 0
    
    ulp = UniswapV3Lp(TOKENS[token0], TOKENS[token1], fee)
    
    # get_open_positions
    try:
        open_positions = ulp.get_open_positions()
        logger.info(f"get_open_positions", exc_info=True)
    except Exception as e:
        logger.error(f"get_open_positions", exc_info=True)
        return 0
    
    # check volatility
    if vol <= vol_thres[benchmark_vol]:
        logger.info(f"check volatility: Open LP on Volatility: vol <= vol_thres[{benchmark_vol}]", exc_info=True)
        # open lp
        # wallet
        try:
            wallet = get_balances()
            logger.info(f"get_balances", exc_info=True)
        except Exception as e:
            logger.error(f"get_balances: {e}", exc_info=True)
            return 0
          
        # price
        try:
            p = float(ulp.pool.get_price())
            logger.info(f"get_price", exc_info=True)
        except Exception as e:
            logger.error(f"get_price: {e}", exc_info=True)
            return 0
            
        # define lp
        v = wallet[token1] + wallet[token0]*p
        p_a, p_b = [p * (1 + (s * concentration)) * (1 + move * concentration) for s in (-1, 1)]
        pos_uni = _uni_init(p, v*(1-cash_keep), p_a, p_b)
        dx = wallet[token0] - pos_uni['x']
        dy = wallet[token1] - pos_uni['y']
        
        # swap
        if dx < 0 and dy < 0: 
            logger.error(f"swap: insufficient in all tokens | wallet: {wallet}", exc_info=True)    
            return 0
        elif dx < 0 and dy > 0: 
            try:
                swap = Swap()
                swaped = swap.swap(TOKENS[token1], TOKENS[token0], dy)
                logger.info(f"swap: {dy} {token1} into {token0} ({dy} USDC)")
            except Exception as e: 
                logger.error(f"swap: {e}")
                return 0
            
        elif dy < 0 and dx > 0:
            try:
                swap = Swap()
                swaped = swap.swap(TOKENS[token0], TOKENS[token1], dx)
                logger.info(f"swap: {dx} {token0} into {token1} ({dx*p} USDC)")
            except Exception as e: 
                logger.error(f"swap: {e}") 
                return 0
            
        # wallet swap
        try:
            wallet_swap = get_balances()
            v_swap = wallet_swap[token1] + wallet_swap[token0]*p
            swap_cost = np.abs(v - v_swap)
            logger.info(f"get_balances swap: swap_cost: {swap_cost}", exc_info=True)
        except Exception as e:
            logger.error(f"get_balances swap: {e}", exc_info=True)
            return 0
        
        # check amounts
        if (wallet[token0] - pos_uni['x']) > 0 and (wallet[token1] - pos_uni['y']) > 0:
            logger.info(f"check amounts: sufficient amounts in wallet {wallet}; deploying liquidity....")            
        else:
            logger.error(f"check amounts: unsufficient amounts in wallet: {wallet} for lp position: {pos_uni}")
            return 0
                
        # deploy_liquidity            
        try:
            deployed_liquidity = ulp.deploy_liquidity(pos_uni['y'], p_a, p_b)
            logger.info(f"deploy_liquidity", exc_info=True)
        except Exception as e:
            logger.error(f"deploy_liquidity: {e}", exc_info=True)
            return 0
        
        # check deployed_liquidity 
        try:
            open_positions = ulp.get_open_positions()
            logger.info(f"check deployed_liquidity: get_open_positions", exc_info=True)
            if not len(open_positions):
                logger.error(f"check deployed_liquidity: open_positions", exc_info=True)
        except Exception as e:
            logger.error(f"check deployed_liquidity: {e}", exc_info=True)
            return 0
    
    else:
        logger.info(f"check volatility: Close LP on Volatility: vol > vol_thres[{benchmark_vol}]", exc_info=True)
        # close open_positions
        if len(open_positions):
            for pos in open_positions:
                try:
                    result = ulp.reduce_and_collect_liquidity(pos['tokenId'], 100)
                    logger.info(f"reduce_and_collect_liquidity {pos['tokenId']}", exc_info=True)
                except Exception as e:
                    logger.error(f"reduce_and_collect_liquidity {pos['tokenId']}", exc_info=True)
                    return 0
    return 1    


# deployed_liquidity = ulp.deploy_liquidity(22, p_a, p_b)


# =============================================================================
# get current position
# if liquidity:
#     reduce liquidity
#     (collect tokens)
# 
# get vol prediction 
# if vol low:
#     get pool price
#     get token amnts
#     get upper & lower price
#     swap tokens
#     apply liq
# =============================================================================
