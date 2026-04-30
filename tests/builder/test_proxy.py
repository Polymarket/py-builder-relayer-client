from unittest import TestCase

from py_builder_relayer_client.builder.proxy import (
    create_proxy_struct_hash,
    create_proxy_signature,
    build_proxy_transaction_request,
)
from py_builder_relayer_client.models import (
    ProxyTransaction,
    ProxyTransactionArgs,
    CallType,
)
from py_builder_relayer_client.encode.proxy import encode_proxy_transaction_data
from py_builder_relayer_client.config import get_contract_config
from py_builder_relayer_client.signer import Signer


class TestProxy(TestCase):

    def test_create_proxy_signature(self):
        """
        Build proxy transaction request
        PK: 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
        Address: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
        """
        # Publicly known PK
        signer = Signer(
            private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
            chain_id=137,
        )

        config = get_contract_config(137)

        # USDC approve calldata.
        usdc = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
        approve_calldata = "0x095ea7b30000000000000000000000004d97dcd97ec945f40cf65f87097ace5ea0476045ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"

        proxy_txn = ProxyTransaction(
            to=usdc,
            type_code=CallType.Call,
            data=approve_calldata,
            value="0",
        )

        encoded_data = encode_proxy_transaction_data([proxy_txn])

        args = ProxyTransactionArgs(
            from_address="0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
            gas_limit="85338",
            gas_price="0",
            nonce="0",
            relay="0xae700edfd9ab986395f3999fe11177b9903a52f1",
            data=encoded_data,
        )

        req = build_proxy_transaction_request(
            signer=signer,
            args=args,
            config=config,
        )

        expected_sig = "0x4c18e2d2294a00d686714aff8e7936ab657cb4655dfccb2b556efadcb7e835f800dc2fecec69c501e29bb36ecb54b4da6b7c410c4dc740a33af2afde2b77297e1b"
        self.assertEqual(expected_sig, req.signature)
