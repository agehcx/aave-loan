from web3 import Web3, Account
from eth_defi.aave_v3.deployment import fetch_deployment
from eth_defi.aave_v3.loan import supply, borrow
from eth_defi.aave_v3.constants import AAVE_V3_DEPLOYMENTS
from dotenv import load_dotenv
import os

load_dotenv()

# Setup Infura URL
infura_token = os.getenv("INFURA_TOKEN")
infura_url = f"https://mainnet.infura.io/v3/{infura_token}"
web3 = Web3(Web3.HTTPProvider(infura_url))

# Check if Web3 is connected
if not web3.is_connected():
    print("Failed to connect to Web3 provider.")
    exit()

# Fetch Aave v3 deployment details
aave_v3 = fetch_deployment(
    web3,
    pool_address=AAVE_V3_DEPLOYMENTS["ethereum"]["pool"],
    data_provider_address=AAVE_V3_DEPLOYMENTS["ethereum"]["data_provider"],
    oracle_address=AAVE_V3_DEPLOYMENTS["ethereum"]["oracle"],
)

# Token addresses (WBTC, USDC)
WBTC_ADDRESS = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"  # WBTC contract address
USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eb48"  # USDC contract address

# Token ABI (standard ERC20 ABI)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [{"name": "", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "value", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
    },
]


# Convert token amount to smallest unit
def to_token_unit(amount, decimals):
    return int(amount * 10**decimals)


# Create wallet function
def create_wallet():
    account = Account.create()
    wallet_address = account.address
    private_key = account.key.hex()
    print(f"New wallet created!")
    print(f"Address: {wallet_address}")
    print(f"Private Key: {private_key}")
    return wallet_address, private_key


# Deposit WBTC into Aave
def deposit_wbtc(wallet_address, private_key, amount):
    # WBTC uses 8 decimals (like ETH)
    amount_in_wei = to_token_unit(amount, 8)  # 8 decimals for WBTC
    wbtc_contract = web3.eth.contract(address=WBTC_ADDRESS, abi=ERC20_ABI)

    # Approve transaction for WBTC
    approve_fn, supply_fn = supply(
        aave_v3_deployment=aave_v3,
        token=wbtc_contract,
        amount=amount_in_wei,
        wallet_address=wallet_address,
    )

    # Get the nonce
    nonce = web3.eth.getTransactionCount(wallet_address)

    # Approve transaction
    tx = approve_fn.build_transaction({"from": wallet_address, "nonce": nonce})
    signed = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"Approval transaction hash: {tx_hash.hex()}")

    # Supply transaction
    tx = supply_fn.build_transaction(
        {"from": wallet_address, "nonce": nonce + 1}
    )  # Increment nonce for the next transaction
    signed = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"Deposit transaction hash: {tx_hash.hex()}")
    return tx_hash


# Borrow USDC from Aave
def borrow_usdc(wallet_address, private_key, amount):
    # USDC uses 6 decimals (Mwei)
    amount_in_mwei = to_token_unit(amount, 6)  # 6 decimals for USDC
    usdc_contract = web3.eth.contract(
        address=Web3.toChecksumAddress(USDC_ADDRESS), abi=ERC20_ABI
    )  # Use checksum address

    borrow_fn = borrow(
        aave_v3_deployment=aave_v3,
        token=usdc_contract,
        amount=amount_in_mwei,
        wallet_address=wallet_address,
    )

    # Get the nonce
    nonce = web3.eth.getTransactionCount(wallet_address)

    # Borrow transaction
    tx = borrow_fn.build_transaction({"from": wallet_address, "nonce": nonce})
    signed = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"Borrow transaction hash: {tx_hash.hex()}")
    return tx_hash


# Test deposit and borrow functions
def test_deposit_and_borrow():
    # Create a wallet
    wallet_address, private_key = create_wallet()

    # Display a warning if the wallet is empty
    print(
        f"IMPORTANT: Ensure the wallet ({wallet_address}) is funded with ETH for gas fees."
    )

    # Test deposit WBTC
    try:
        print("Testing deposit of 0.1 WBTC...")
        deposit_tx = deposit_wbtc(wallet_address, private_key, 0.1)
        print(f"Deposit transaction successful: {deposit_tx.hex()}")
    except Exception as e:
        print(f"Error during deposit: {e}")

    # Test borrow USDC
    try:
        print("Testing borrowing of 50 USDC...")
        borrow_tx = borrow_usdc(wallet_address, private_key, 50)
        print(f"Borrow transaction successful: {borrow_tx.hex()}")
    except Exception as e:
        print(f"Error during borrowing: {e}")


if __name__ == "__main__":
    test_deposit_and_borrow()
