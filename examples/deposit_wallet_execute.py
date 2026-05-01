from dotenv import load_dotenv
from eth_abi import encode
from eth_utils import keccak, to_checksum_address
import os
import time

from py_builder_relayer_client.client import RelayClient
from py_builder_relayer_client.models import DepositWalletCall
from py_builder_signing_sdk.config import BuilderConfig, BuilderApiKeyCreds

load_dotenv()


def _function_selector(signature: str) -> bytes:
    return keccak(text=signature)[:4]


def encode_approve(spender: str, amount: int) -> str:
    selector = _function_selector("approve(address,uint256)")
    encoded_args = encode(["address", "uint256"], [spender, amount])
    return "0x" + (selector + encoded_args).hex()


def main():
    relayer_url = os.getenv("RELAYER_URL", "https://relayer-v2-staging.polymarket.dev/")
    chain_id = int(os.getenv("CHAIN_ID", 80002))
    pk = os.getenv("PK")

    builder_config = BuilderConfig(
        local_builder_creds=BuilderApiKeyCreds(
            key=os.getenv("BUILDER_API_KEY"),
            secret=os.getenv("BUILDER_SECRET"),
            passphrase=os.getenv("BUILDER_PASS_PHRASE"),
        )
    )

    client = RelayClient(relayer_url, chain_id, pk, builder_config)
    wallet_address = (
        os.getenv("DEPOSIT_WALLET_ADDRESS") or client.get_expected_deposit_wallet()
    )
    token = to_checksum_address(os.getenv("USDC_ADDRESS"))
    spender = to_checksum_address(os.getenv("SPENDER_ADDRESS"))
    nonce = os.getenv("DEPOSIT_WALLET_NONCE", "0")
    deadline = os.getenv("DEPOSIT_WALLET_DEADLINE", str(int(time.time()) + 240))

    approve_data = encode_approve(
        spender,
        115792089237316195423570985008687907853269984665640564039457584007913129639935,
    )
    call = DepositWalletCall(target=token, value="0", data=approve_data)

    resp = client.execute_deposit_wallet_batch(
        calls=[call],
        wallet_address=wallet_address,
        nonce=nonce,
        deadline=deadline,
    )
    print(resp)

    awaited_txn = resp.wait()
    print(awaited_txn)


main()
