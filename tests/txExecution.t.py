from globalUtils.GlobalUtils import *
from txExecution.txExecutionUtils import *
from txExecution.txExecution import *

class Test:
    def __init__(self):
        self.txExecutor = TxExecution()

    def provide_liquidity(self, mint_params: MintParams):
        try:
            self.txExecutor.deploy_liquidity(mint_params)

        except Exception as e:
            logger.error(f'TxExecution.t.py - Failed to deploy liquidity. Error: {e}', exc_info=True)