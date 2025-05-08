from xtreamly_trading_lp.globalUtils.GlobalUtils import *
from xtreamly_trading_lp.txExecution.txExecutionUtils import *
from xtreamly_trading_lp.txExecution.txExecution import *
from xtreamly_trading_lp.globalUtils.getPriceFromChainlink import *

center_price = get_chainlink_price(CHAINLINK_IDS.eth)
percent_bound = 3    
tick_spacing = 60
tick_lower, tick_upper = get_tick_range(center_price, percent_bound, tick_spacing)
amount_usdc = 8 * (10 ** 6)
amount_eth = 8 / center_price * (10 ** 18)
print(amount_usdc, amount_eth)

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

reduce_params = ReduceParams( 
    4436099,
    5975938846671457354,
    4031400000000000,
    0
)

collect_params = CollectParams(
    4436099,
    EXECUTOR_ADDRESS,
    2**128 - 1,
    2**128 - 1
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

print(center_price)


x = Test()
y = x.txExecutor.collect_removed_liquidity(collect_params)
print(y)