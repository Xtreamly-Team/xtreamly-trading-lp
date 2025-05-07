from xtreamly_trading_lp.globalUtils.GlobalUtils import *
from xtreamly_trading_lp.txExecution.txExecutionUtils import *
from xtreamly_trading_lp.txExecution.txExecution import *

center_price = 1788
percent_bound = 3    
tick_spacing = 60
tick_lower, tick_upper = get_tick_range(center_price, percent_bound, tick_spacing)
amount_usdc = 8 * (10 ** 6)
amount_eth = 0.004 * (10 ** 18)

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
class Test:
    def __init__(self):
        self.txExecutor = TxExecution()

    def provide_liquidity(self, mint_params: MintParams):
        try:
            print('made it to here 1')
            self.txExecutor.deploy_liquidity(mint_params)

        except Exception as e:
            logger.error(f'TxExecution.t.py - Failed to deploy liquidity. Error: {e}', exc_info=True)

x = Test()
y = x.provide_liquidity(mint_params)
print(y)