from unittest import TestCase

from py_builder_relayer_client.builder.safe import (
    create_struct_hash,
    create_safe_signature,
    split_and_pack_sig,
)
from py_builder_relayer_client.models import OperationType
from py_builder_relayer_client.signer import Signer


class TestSafe(TestCase):

    def test_create_struct_hash(self):
        struct_hash = create_struct_hash(
            chain_id=137,
            safe="0xd93B25cb943D14d0d34FBaF01Fc93a0f8b5F6E47",
            to="0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761",
            value="0",
            data="0x8d80ff0a00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000132002791bca1f2de4661ed88a30c99a7a9449aa8417400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044095ea7b30000000000000000000000004d97dcd97ec945f40cf65f87097ace5ea0476045ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff002791bca1f2de4661ed88a30c99a7a9449aa8417400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044095ea7b30000000000000000000000004d97dcd97ec945f40cf65f87097ace5ea0476045ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff0000000000000000000000000000",
            operation=OperationType.DelegateCall,
            safe_tx_gas="0",
            base_gas="0",
            gas_price="0",
            gas_token="0x0000000000000000000000000000000000000000",
            refund_receiver="0x0000000000000000000000000000000000000000",
            nonce="8",
        )

        expected_struct_hash = (
            "0x06d5102c3e356b62a75f8203cd5ce7ab1fa8fdab33875ef621eee102220d90b8"
        )
        self.assertEqual(expected_struct_hash, struct_hash)

    def test_create_safe_signature(self):

        struct_hash = (
            "0x06d5102c3e356b62a75f8203cd5ce7ab1fa8fdab33875ef621eee102220d90b8"
        )

        # Publicly known PK
        signer = Signer(
            private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
            chain_id=137,
        )

        sig = create_safe_signature(signer, struct_hash)
        expected_sig = "0xad62657208a0d885f91bba7490de238741bf7c51eb792f00856171aafc9e012373156fb672e55d840733c8bf723ec458545fcd5749aa5e547f808c222e7e11701c"
        self.assertEqual(expected_sig, sig)

    def test_create_packed_sig(self):

        sig = "0xad62657208a0d885f91bba7490de238741bf7c51eb792f00856171aafc9e012373156fb672e55d840733c8bf723ec458545fcd5749aa5e547f808c222e7e11701c"
        packed_sig = split_and_pack_sig(sig)
        expected_packed_sig = "0xad62657208a0d885f91bba7490de238741bf7c51eb792f00856171aafc9e012373156fb672e55d840733c8bf723ec458545fcd5749aa5e547f808c222e7e117020"
        self.assertEqual(expected_packed_sig, packed_sig)
