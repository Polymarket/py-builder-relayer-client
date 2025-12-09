from typing import List

from eth_abi import encode
from eth_utils import keccak, to_bytes, to_checksum_address, to_hex

from ..models import CallType, ProxyTransaction


def encode_proxy_transaction_data(txns: List[ProxyTransaction]) -> str:
    """
    Encode proxy transactions data using proxy function signature
    """
    # Function selector: keccak256("proxy((uint8,address,uint256,bytes)[])")[:4]
    # The function signature is: proxy((uint8,address,uint256,bytes)[])
    function_selector = keccak(text="proxy((uint8,address,uint256,bytes)[])")[:4]

    # Prepare the calls array
    # Each call is a tuple: (uint8 typeCode, address to, uint256 value, bytes data)
    calls = []
    for txn in txns:
        to_address = to_checksum_address(txn.to)
        data_bytes = (
            to_bytes(hexstr=txn.data)
            if txn.data.startswith("0x")
            else to_bytes(hexstr="0x" + txn.data)
        )

        calls.append(
            (
                int(txn.type_code.value),
                to_address,
                int(txn.value),
                data_bytes,
            )
        )

    # Encode the array of tuples
    # The ABI type is: tuple(uint8,address,uint256,bytes)[]
    encoded_data = encode(["(uint8,address,uint256,bytes)[]"], [calls])

    # Combine function selector with encoded data
    full_data = function_selector + encoded_data

    return to_hex(full_data)
