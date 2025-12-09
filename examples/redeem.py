import os

from dotenv import load_dotenv
from eth_abi import encode
from eth_utils import keccak, to_checksum_address, to_hex
from py_builder_signing_sdk.config import BuilderApiKeyCreds, BuilderConfig

from py_builder_relayer_client.client import RelayClient
from py_builder_relayer_client.models import OperationType, SafeTransaction

load_dotenv()


def _function_selector(signature: str) -> bytes:
    """First 4 bytes of Keccak-256 of the function signature."""
    return keccak(text=signature)[:4]


def create_ctf_redeem_txn(
    contract: str,
    condition_id: str,
    collateral: str,
) -> SafeTransaction:
    """
    Create a CTF redeem transaction
    """
    contract = to_checksum_address(contract)
    collateral = to_checksum_address(collateral)

    # Function signature: redeemPositions(address,bytes32,bytes32,uint256[])
    selector = _function_selector("redeemPositions(address,bytes32,bytes32,uint256[])")

    # zeroHash for parentCollectionId
    zero_hash = bytes.fromhex(
        "0000000000000000000000000000000000000000000000000000000000000000"
    )

    # Convert condition_id from hex string to bytes32
    condition_id_bytes = bytes.fromhex(
        condition_id[2:] if condition_id.startswith("0x") else condition_id
    )

    # Encode arguments: [collateral, zeroHash, conditionId, [1, 2]]
    encoded_args = encode(
        ["address", "bytes32", "bytes32", "uint256[]"],
        [collateral, zero_hash, condition_id_bytes, [1, 2]],
    )

    calldata = to_hex(selector + encoded_args)

    return SafeTransaction(
        to=contract,
        operation=OperationType.Call,
        data=calldata,
        value="0",
    )


def create_nr_adapter_redeem_txn(
    contract: str,
    condition_id: str,
    redeem_amounts: list[int],
) -> SafeTransaction:
    """
    Create a Negative Risk Adapter redeem transaction
    """
    contract = to_checksum_address(contract)

    # Function signature: redeemPositions(bytes32,uint256[])
    selector = _function_selector("redeemPositions(bytes32,uint256[])")

    # Convert condition_id from hex string to bytes32
    condition_id_bytes = bytes.fromhex(
        condition_id[2:] if condition_id.startswith("0x") else condition_id
    )

    # Encode arguments: [conditionId, redeemAmounts]
    encoded_args = encode(
        ["bytes32", "uint256[]"], [condition_id_bytes, redeem_amounts]
    )

    calldata = to_hex(selector + encoded_args)

    return SafeTransaction(
        to=contract,
        operation=OperationType.Call,
        data=calldata,
        value="0",
    )


def main():
    print("Starting...")

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

    # Set your values here
    neg_risk = False
    condition_id = "0x...."  # conditionId to redeem

    # Amounts to redeem per outcome, only necessary for neg risk
    # Must be an array of length 2 with:
    # the first element being the amount of yes tokens to redeem and
    # the second element being the amount of no tokens to redeem
    redeem_amounts = [111000000, 0]

    usdc = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
    ctf = "0x4d97dcd97ec945f40cf65f87097ace5ea0476045"
    neg_risk_adapter = "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296"

    txn = (
        create_nr_adapter_redeem_txn(neg_risk_adapter, condition_id, redeem_amounts)
        if neg_risk
        else create_ctf_redeem_txn(ctf, condition_id, usdc)
    )

    resp = client.execute([txn], "redeem")
    print(resp)

    awaited_txn = resp.wait()
    print(awaited_txn)


if __name__ == "__main__":
    main()
