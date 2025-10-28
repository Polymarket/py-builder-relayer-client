from unittest import TestCase

from py_builder_relayer_client.model.safe_tx import SafeTx
from poly_eip712_structs import make_domain


class TestSafeTx(TestCase):

    def test_generate_struct_hash(self):
        safe = "0xd93B25cb943D14d0d34FBaF01Fc93a0f8b5F6E47"
        safeTx = SafeTx(
            to="0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761",
            value=0,
            data="0x8d80ff0a00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000132002791bca1f2de4661ed88a30c99a7a9449aa8417400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044095ea7b30000000000000000000000004d97dcd97ec945f40cf65f87097ace5ea0476045ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff002791bca1f2de4661ed88a30c99a7a9449aa8417400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044095ea7b30000000000000000000000004d97dcd97ec945f40cf65f87097ace5ea0476045ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff0000000000000000000000000000",
            operation=1,
            safeTxGas=0,
            baseGas=0,
            gasPrice=0,
            gasToken="0x0000000000000000000000000000000000000000",
            refundReceiver="0x0000000000000000000000000000000000000000",
            nonce=8,
        )

        domain = make_domain(chainId=137, verifyingContract=safe)
        struct_hash = safeTx.generate_struct_hash(domain)
        expected_struct_hash = (
            "0x06d5102c3e356b62a75f8203cd5ce7ab1fa8fdab33875ef621eee102220d90b8"
        )
        self.assertEqual(expected_struct_hash, struct_hash)
