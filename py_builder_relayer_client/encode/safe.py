from typing import List
from eth_abi import encode
from eth_abi.packed import encode_packed
from eth_utils import to_hex, to_bytes, to_checksum_address, keccak

from ..models import SafeTransaction, OperationType


def create_safe_multisend_transaction(
    txns: List[SafeTransaction], safe_multisend_address: str
) -> SafeTransaction:
    encoded_txns = []

    for tx in txns:
        to_address = to_checksum_address(tx.to)
        data_bytes = (
            to_bytes(hexstr=tx.data)
            if tx.data.startswith("0x")
            else to_bytes(hexstr="0x" + tx.data)
        )

        # Pack: [uint8, address, uint256, uint256, bytes]
        packed_tx = encode_packed(
            ["uint8", "address", "uint256", "uint256", "bytes"],
            [
                tx.operation.value,
                to_address,
                int(tx.value),
                len(data_bytes),
                data_bytes,
            ],
        )
        encoded_txns.append(packed_tx)

    concatenated_txns = b"".join(encoded_txns)

    multisend_data = encode(["bytes"], [concatenated_txns])

    # keccak(text="multiSend(bytes)")[:4]
    function_selector = bytes.fromhex("8d80ff0a")

    full_data = function_selector + multisend_data

    data = to_hex(full_data)

    return SafeTransaction(
        to=to_checksum_address(safe_multisend_address),
        operation=OperationType.DelegateCall,
        data=to_hex(full_data),
        value="0",
    )
