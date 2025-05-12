from xtreamly_trading_lp.globalUtils.GlobalUtils import *
from xtreamly_trading_lp.txExecution.txExecutionUtils import *
from xtreamly_trading_lp.txExecution.txExecution import *
from xtreamly_trading_lp.globalUtils.getPriceFromChainlink import *
from xtreamly_trading_lp.globalUtils.getPriceFromPool import *

center_price = float(get_price_from_pool(POOL_CONTRACTS.ETH_USDC))
current_tick = float(get_current_tick(POOL_CONTRACTS.ETH_USDC))
percent_bound = 5
tick_spacing = 60
tick_lower, tick_upper = get_tick_range_from_current_tick(current_tick, percent_bound, tick_spacing)
print(tick_lower, tick_upper)
amount_usdc = 5 * (10 ** 6)
amount_eth = 5 / center_price * (10 ** 18)

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


collect_params = CollectParams(
    4455716,
    EXECUTOR_ADDRESS,
    2**128 - 1,
    2**128 - 1
)

class Test:
    def __init__(self):
        self.txExecutor = TxExecution()

    def provide_liquidity(self, mint_params: MintParams):
        try:
            self.txExecutor.deploy_liquidity(mint_params)

        except Exception as e:
            logger.error(f'TxExecution.t.py - Failed to deploy liquidity. Error: {e}', exc_info=True)


x = Test()
# b = x.provide_liquidity(mint_params)
# a = x.txExecutor.get_liquidity(4455716)
# reduce_params = ReduceParams( 
#     4455716,
#     a,
#     0,
#     0
# )
# y = x.txExecutor.remove_liquidity(reduce_params)
z = x.txExecutor.collect_removed_liquidity(collect_params)
print(z)
