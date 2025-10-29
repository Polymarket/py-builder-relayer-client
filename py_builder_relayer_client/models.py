from dataclasses import dataclass
from enum import Enum
from typing import Dict


class OperationType(Enum):
    Call = 0
    DelegateCall = 1


@dataclass
class SafeTransaction:
    to: str
    operation: OperationType
    data: str
    value: str


class TransactionType(Enum):
    SAFE = "SAFE"
    SAFE_CREATE = "SAFE-CREATE"


@dataclass
class SignatureParams:
    # SAFE signature params
    gas_price: str = None
    operation: str = None
    safe_txn_gas: str = None
    base_gas: str = None
    gas_token: str = None
    refund_receiver: str = None

    # SAFE-CREATE signature params
    payment_token: str = None
    payment: str = None
    payment_receiver: str = None

    def to_dict(self):
        d = {}
        if self.gas_price is not None:
            d["gasPrice"] = self.gas_price
        if self.operation is not None:
            d["operation"] = self.operation
        if self.safe_txn_gas is not None:
            d["safeTxnGas"] = self.safe_txn_gas
        if self.base_gas is not None:
            d["baseGas"] = self.base_gas
        if self.gas_token is not None:
            d["gasToken"] = self.gas_token
        if self.refund_receiver is not None:
            d["refundReceiver"] = self.refund_receiver
        if self.payment_token is not None:
            d["paymentToken"] = self.payment_token
        if self.payment is not None:
            d["payment"] = self.payment
        if self.payment_receiver is not None:
            d["paymentReceiver"] = self.payment_receiver
        return d


@dataclass
class TransactionRequest:
    type: str
    from_address: str
    to: str
    proxy: str
    data: str
    signature: str
    signature_params: SignatureParams
    value: str = None
    nonce: str = None
    metadata: str = None

    def to_dict(self) -> Dict[str, str]:
        d = {
            "type": self.type,
            "from": self.from_address,
            "to": self.to,
            "proxyWallet": self.proxy,
            "data": self.data,
            "signature": self.signature,
        }
        if self.value is not None:
            d["value"] = self.value
        if self.signature_params is not None:
            d["signatureParams"] = self.signature_params.to_dict()
        if self.nonce is not None:
            d["nonce"] = self.nonce
        if self.metadata is not None:
            d["metadata"] = self.metadata
        return d


@dataclass
class SafeTransactionArgs:
    from_address: str
    nonce: str
    chain_id: int
    transactions: list[SafeTransaction]


@dataclass
class SafeCreateTransactionArgs:
    from_address: str
    chain_id: int
    payment_token: str
    payment: str
    payment_receiver: str


class RelayerTransactionState(Enum):
    STATE_NEW = "STATE_NEW"
    STATE_EXECUTED = "STATE_EXECUTED"
    STATE_MINED = "STATE_MINED"
    STATE_INVALID = "STATE_INVALID"
    STATE_CONFIRMED = "STATE_CONFIRMED"
    STATE_FAILED = "STATE_FAILED"


@dataclass
class SplitSig:
    r: str
    s: str
    v: str
