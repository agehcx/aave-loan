from web3 import Web3, Account
from eth_defi.aave_v3.deployment import fetch_deployment
from eth_defi.aave_v3.loan import supply, borrow
from eth_defi.aave_v3.constants import AAVE_V3_DEPLOYMENTS
from dotenv import load_dotenv
import os

load_dotenv()

infura_token = os.getenv("INFURA_TOKEN")
infura_url = f"https://mainnet.infura.io/v3/{infura_token}"
web3 = Web3(Web3.HTTPProvider(infura_url))

from web3 import Web3

WBTC_ADDRESS = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
]

wbtc_contract = web3.eth.contract(
    address=Web3.to_checksum_address(WBTC_ADDRESS), abi=ERC20_ABI
)

aave_v3 = fetch_deployment(
    web3,
    pool_address=AAVE_V3_DEPLOYMENTS["ethereum"]["pool"],
    data_provider_address=AAVE_V3_DEPLOYMENTS["ethereum"]["data_provider"],
    oracle_address=AAVE_V3_DEPLOYMENTS["ethereum"]["oracle"],
)


def to_token_unit(amount, decimals):
    return int(amount * 10**decimals)


def create_wallet():
    account = Account.create()
    wallet_address = account.address
    private_key = account.key.hex()
    print(f"New wallet created!")
    print(f"Address: {wallet_address}")
    print(f"Private Key: {private_key}")
    return wallet_address, private_key


def deposit_2(wallet_address, private_key, amount):
    print("====================================")
    print(wallet_address, private_key, amount)
    amount_in_wei = to_token_unit(amount, 8)
    borrow_fn = borrow(
        aave_v3_deployment=aave_v3,
        token=wbtc_contract,
        amount=amount_in_wei,
        wallet_address=wallet_address,
    )

    print("====================================")
    print(borrow_fn)
    
    


if __name__ == "__main__":
    wallet_address, private_key = create_wallet()

    deposit_2(wallet_address, private_key, 0.1)
