from poly_eip712_structs import Address, Uint
from .base import BaseEIP712Model


class CreateProxy(BaseEIP712Model):
    """
    CreateProxy
    """

    paymentToken = Address()

    payment = Uint(256)

    paymentReceiver = Address()

    def dict(self):
        return {
            "paymentToken": self["paymentToken"],
            "payment": self["payment"],
            "paymentReceiver": self["paymentReceiver"],
        }
