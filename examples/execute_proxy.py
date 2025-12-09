import os

from dotenv import load_dotenv
from eth_abi import encode
from eth_utils import keccak, to_checksum_address
from py_builder_signing_sdk.config import BuilderApiKeyCreds, BuilderConfig

from py_builder_relayer_client.client import RelayClient
from py_builder_relayer_client.models import (
    OperationType,
    RelayerTxType,
    SafeTransaction,
)

load_dotenv()


def _function_selector(signature: str) -> bytes:
    """First 4 bytes of Keccak-256 of the function signature."""
    return keccak(text=signature)[:4]


def encode_approve(spender: str, amount: int) -> str:
    selector = _function_selector("approve(address,uint256)")

    encoded_args = encode(["address", "uint256"], [spender, amount])
    return "0x" + (selector + encoded_args).hex()


def create_usdc_approve_txn(token: str, spender: str):
    token = to_checksum_address(token)
    spender = to_checksum_address(spender)

    data = encode_approve(
        spender,
        115792089237316195423570985008687907853269984665640564039457584007913129639935,
    )
    return SafeTransaction(
        to=token,
        operation=OperationType.Call,
        data=data,
        value="0",
    )


def main():
    print("starting proxy wallet example...")
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

    # Initialize client with PROXY transaction type
    client = RelayClient(
        relayer_url, chain_id, pk, builder_config, relayer_tx_type=RelayerTxType.PROXY
    )

    usdc = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
    ctf = "0x4d97dcd97ec945f40cf65f87097ace5ea0476045"
    txn = create_usdc_approve_txn(usdc, ctf)

    resp = client.execute([txn, txn], "approve USDC on CTF via proxy")
    print(resp)

    awaited_txn = resp.wait()
    print(awaited_txn)


if __name__ == "__main__":
    main()
