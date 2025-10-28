from poly_eip712_structs import EIP712Struct, Address, Uint, Bytes
from eth_utils import keccak
from ..utils.utils import prepend_zx


class SafeTx(EIP712Struct):
    """
    SafeTx
    """

    to = Address()

    value = Uint(256)

    data = Bytes()

    operation = Uint(8)

    safeTxGas = Uint(256)

    baseGas = Uint(256)

    gasPrice = Uint(256)

    gasToken = Address()

    refundReceiver = Address()

    nonce = Uint(256)

    def dict(self):
        return {
            "to": self["to"],
            "value": self["value"],
            "data": self["data"],
            "operation": self["operation"],
            "safeTxGas": self["safeTxGas"],
            "baseGas": self["baseGas"],
            "gasPrice": self["gasPrice"],
            "gasToken": self["gasToken"],
            "refundReceiver": self["refundReceiver"],
            "nonce": self["nonce"],
        }

    def generate_struct_hash(self, domain) -> str:
        struct_hash = keccak(self.signable_bytes(domain)).hex()
        return prepend_zx(struct_hash)
