import json
from web3 import Web3
from eth_abi import encode
from globalUtils.GlobalUtils import NON_FUNGIBLE_POSITION_MANAGER_ADDRESS, UNISWAP_FACTORY_ADDRESS
from globalUtils.web3_utils import get_web3, get_wallet

UNISWAP_FACTORY = Web3.to_checksum_address(UNISWAP_FACTORY_ADDRESS)
POOL_INIT_CODE_HASH = "0xe34f199b19b2b4f47f68442619d555527d244f78a3297ea89325f843f87b8b54"


def get_pool_address(token0, token1, fee):
    if int(token0, 16) > int(token1, 16):
        token0, token1 = token1, token0
    salt = Web3.keccak(encode(["address", "address", "uint24"], [token0, token1, fee]))
    raw = Web3.keccak(encode(["bytes1", "address", "bytes32", "bytes32"],
                             [b'\xff', UNISWAP_FACTORY, salt, bytes.fromhex(POOL_INIT_CODE_HASH[2:])]))
    return Web3.to_checksum_address("0x" + raw[-20:].hex())


def get_positions(private_key: str = None):
    web3 = get_web3()
    position_manager_abi = json.load(open('./globalUtils/ABIs/NonFungiblePositionManager.json'))
    position_manager_address = Web3.to_checksum_address(NON_FUNGIBLE_POSITION_MANAGER_ADDRESS)
    contract = web3.eth.contract(address=position_manager_address, abi=position_manager_abi)
    wallet = get_wallet(private_key).address

    nfts = contract.functions.balanceOf(wallet).call()
    positions = []
    for i in range(nfts):
        token_id = contract.functions.tokenOfOwnerByIndex(wallet, i).call()
        pos = contract.functions.positions(token_id).call()

        token0, token1, fee, tickL, tickU, liq = pos[2], pos[3], pos[4], pos[5], pos[6], pos[7]
        pool_addr = get_pool_address(token0, token1, fee)

        positions.append({
            "tokenId": token_id,
            "token0": token0,
            "token1": token1,
            "fee": fee,
            "tickLower": tickL,
            "tickUpper": tickU,
            "liquidity": liq,
            "pool": pool_addr,
            "feeGrowthInside0LastX128": pos[8],
            "feeGrowthInside1LastX128": pos[9],
            "tokensOwed0": pos[10],
            "tokensOwed1": pos[11]
        })

    return positions
