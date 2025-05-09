import os
from xtreamly_trading_lp.globalUtils.GlobalUtils import *
import time
from web3.types import TxReceipt
from uniswappy import *
import math
import requests


fee = UniV3Utils.FeeAmount.MEDIUM
tick_spacing = UniV3Utils.TICK_SPACINGS[fee]
lwr_tick = UniV3Utils.getMinTick(tick_spacing)
upr_tick = UniV3Utils.getMaxTick(tick_spacing)

ETH = ERC20("WETH", WETH_ADDRESS)
BTC = ERC20("WBTC", WBTC_ADDRESS)
USDC = ERC20("USDC", USDC_ADDRESS)

exchg_data = UniswapExchangeData(tkn0 = ETH, tkn1 = USDC, symbol="LP", 
                                   address="0xC1A31dC7Bc2e06aA0228D2Ea58dF4F92C3A16998", version = 'V3', 
                                   tick_spacing = tick_spacing, 
                                   fee = fee)

def get_tick_range_from_current_tick(current_tick: int, percent_bound: int, tick_spacing: int) -> tuple:
    if percent_bound <= 0:
        raise ValueError("percent_bound must be greater than 0")

    # Approximate number of ticks corresponding to ±percent_bound
    ticks_per_1_percent = int(round(math.log(1.01) / math.log(1.0001)))
    bound_in_ticks = percent_bound * ticks_per_1_percent

    # Calculate raw bounds
    tick_lower = current_tick - bound_in_ticks
    tick_upper = current_tick + bound_in_ticks

    # Align both to tick spacing
    def align_tick(tick: int, spacing: int) -> int:
        aligned = tick - (tick % spacing)
        return aligned

    tick_lower_aligned = align_tick(tick_lower, tick_spacing)
    tick_upper_aligned = align_tick(tick_upper, tick_spacing)

    return int(tick_lower_aligned), int(tick_upper_aligned)



class MintParams():
    def __init__(self,
        token0_address,
        token1_address,
        fee,
        tickLower,
        tickUpper,
        amount0,
        amount1,
        wallet_address
        ):
        self.token0 = GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(token0_address)
        self.token1 = GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(token1_address)
        self.fee = GLOBAL_ARBITRUM_PROVIDER.to_int(fee)
        self.tickLower = GLOBAL_ARBITRUM_PROVIDER.to_int(tickLower)
        self.tickUpper = GLOBAL_ARBITRUM_PROVIDER.to_int(tickUpper)
        self.amount0Desired = GLOBAL_ARBITRUM_PROVIDER.to_int(amount0)
        self.amount1Desired = GLOBAL_ARBITRUM_PROVIDER.to_int(amount1)
        self.amount0Min = 0 # GLOBAL_ARBITRUM_PROVIDER.to_int(int(amount0 * 1)) # 0.1% slippage tolerance 
        self.amount1Min = 0 # GLOBAL_ARBITRUM_PROVIDER.to_int(int(amount1 * 1))
        self.recipient = GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(wallet_address)
        self.deadline = GLOBAL_ARBITRUM_PROVIDER.to_int(int(time.time()) + 600)  # 10 minutes from now

        self.data = (
            self.token0, 
            self.token1, 
            self.fee, 
            self.tickLower, 
            self.tickUpper, 
            self.amount0Desired, 
            self.amount1Desired, 
            self.amount0Min,
            self.amount1Min,
            self.recipient, 
            self.deadline
        )


class ReduceParams():
    def __init__(self,
        token_id,
        liquidity,
        amount0_min,
        amount1_min,
        ):
        self.token_id = GLOBAL_ARBITRUM_PROVIDER.to_int(token_id)
        self.liquidity = GLOBAL_ARBITRUM_PROVIDER.to_int(liquidity)
        self.amount0_min = GLOBAL_ARBITRUM_PROVIDER.to_int(amount0_min)
        self.amount1_min = GLOBAL_ARBITRUM_PROVIDER.to_int(amount1_min)
        self.deadline = GLOBAL_ARBITRUM_PROVIDER.to_int(int(time.time()) + 600)

        self.data = (
            self.token_id, 
            self.liquidity, 
            self.amount0_min, 
            self.amount1_min, 
            self.deadline
        )

class CollectParams():
    def __init__(self,
        token_id,
        recipient,
        amount0_min,
        amount1_min
        ):
        self.token_id = GLOBAL_ARBITRUM_PROVIDER.to_int(token_id)
        self.recipient = GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(recipient)
        self.amount0_min = GLOBAL_ARBITRUM_PROVIDER.to_int(amount0_min)
        self.amount1_min = GLOBAL_ARBITRUM_PROVIDER.to_int(amount1_min)

        self.data = (
            self.token_id, 
            self.recipient, 
            self.amount0_min, 
            self.amount1_min, 
        )

class IncreaseParams():
    def __init__(self,
        token_id,
        amount0_desired,
        amount1_desired,
        amount0_min,
        amount1_min,
        deadline):
        self.token_id = GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(token_id)
        self.amount0_desired = GLOBAL_ARBITRUM_PROVIDER.to_int(amount0_desired)
        self.amount1_desired = GLOBAL_ARBITRUM_PROVIDER.to_int(amount1_desired)
        self.amount0_min = GLOBAL_ARBITRUM_PROVIDER.to_int(amount0_min)
        self.amount1_min = GLOBAL_ARBITRUM_PROVIDER.to_int(amount1_min)
        self.deadline = GLOBAL_ARBITRUM_PROVIDER.to_int(deadline)

        self.data = (
        self.token_id, 
        self.amount0_desired, 
        self.amount1_desired,
        self.amount0_min, 
        self.amount1_min, 
        self.deadline
        )

class QuoteDetails():
    def __init__(
        self,
        sell_token: str,
        buy_token: str,
        sell_amount: str,
        ):
        self.buy_token = buy_token
        self.sell_token = sell_token
        self.sell_amount = sell_amount


class ZeroExAPIResponse():
    def __init__(
        self,
        spender: str,
        swap_amount: float,
        tx_data: str
        ):
        self.spender = spender
        self.swap_amount = swap_amount
        self.tx_data = tx_data

def get_0x_api_quote(quote_details: QuoteDetails) -> ZeroExAPIResponse:
    try:
        api_key = os.getenv('0xAPI_KEY')

        price_params = {
            "chainId": 42161,  
            "sellToken": quote_details.sell_token,
            "buyToken": quote_details.buy_token,
            "sellAmount": quote_details.sell_amount,
            "taker": EXECUTOR_ADDRESS
        }

        headers = {
            "0x-api-key": api_key,
            "0x-version": "v2",
            }

        response = requests.get("https://api.0x.org/swap/allowance-holder/quote?", params=price_params, headers=headers)
        data = json.loads(response.text)

        spender = data.get("transaction", {}).get("to", None)
        transaction_data = data.get("transaction", {}).get("data", None)

        return_data = ZeroExAPIResponse(spender=spender, swap_amount=quote_details.sell_amount, tx_data=transaction_data)

        return return_data

    except Exception as e:
        logger.error(f'ContangoUtils.py - Failed to fetch 0x API quote. Error: {e}', exc_info=True)
        return None

def build_0x_transaction(response: ZeroExAPIResponse) -> dict:
    try:
        nonce = GLOBAL_ARBITRUM_PROVIDER.eth.get_transaction_count(EXECUTOR_ADDRESS)

        tx = {
            'from': EXECUTOR_ADDRESS,
            'to': GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(response.spender),
            'data': response.tx_data,
            'value': 0, 
            'gas': 0,
            'nonce': nonce,
            'chainId': 42161
        }

        

        return tx

    except Exception as e:
        logger.error(f"Error building 0x transaction: {e}", exc_info=True)
        return None


def build_and_send_tx(tx_data: dict):
    try:
        priv_key = os.getenv('PRIV_KEY')
        estimated_gas = GLOBAL_ARBITRUM_PROVIDER.eth.estimate_gas(tx_data)
        tx_data['gas'] = estimated_gas

        fee_history = GLOBAL_ARBITRUM_PROVIDER.eth.fee_history(1, "latest")
        base_fee_per_gas = fee_history["baseFeePerGas"][-1]
        max_priority_fee_per_gas = GLOBAL_ARBITRUM_PROVIDER.eth.max_priority_fee
        max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas
        tx_data["maxFeePerGas"] = int(max_fee_per_gas * 1.05)

        signed_place_market_order_tx = GLOBAL_ARBITRUM_PROVIDER.eth.account.sign_transaction(tx_data, private_key=priv_key)
        tx_hash_place_market_order = GLOBAL_ARBITRUM_PROVIDER.eth.send_raw_transaction(signed_place_market_order_tx.raw_transaction)
        tx_receipt = GLOBAL_ARBITRUM_PROVIDER.eth.wait_for_transaction_receipt(tx_hash_place_market_order)

        return tx_receipt
    
    except Exception as e:
            logger.error(f'txExecutionUtils.py - Error while sending transaction. Error: {e}', exc_info=True)
            return None

def check_tx_success(tx_receipt: TxReceipt) -> bool:
    try:
        time.sleep(0.5)
        if tx_receipt['status'] != 1:
            return False
        else:
            return True
    
    except Exception as e:
        logger.error(f'txExecutionUtils.py - Error checking for Tx success. Error: {e}', exc_info=True)
        return None  

