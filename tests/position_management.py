from src.uniswapV3 import UniswapV3Lp
from src.wallet import get_balances
from src.tokens import WETH, USDC
from src.swap import Swap

balances = get_balances()
print(balances)

p = UniswapV3Lp(WETH, USDC, "0.3%")
# p = p.deploy_liquidity(1, 2500, 3600)
# p = p.reduce_and_collect_liquidity()

# s = Swap()
# s.swap(WETH, USDC, 0.001)
# s.swap(USDC, WETH, 2)
