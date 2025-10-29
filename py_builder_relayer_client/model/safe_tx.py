from poly_eip712_structs import Address, Uint, Bytes
from .base import BaseEIP712Model


class SafeTx(BaseEIP712Model):
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
