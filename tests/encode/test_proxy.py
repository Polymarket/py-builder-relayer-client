from unittest import TestCase

from py_builder_relayer_client.encode.proxy import encode_proxy_transaction_data
from py_builder_relayer_client.models import CallType, ProxyTransaction


class TestProxyEncode(TestCase):

    def test_encode_proxy_transaction_data_single(self):
        """Test encoding a single proxy transaction"""
        tx = ProxyTransaction(
            to="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
            type_code=CallType.Call,
            data="0x095ea7b3",
            value="0",
        )
        result = encode_proxy_transaction_data([tx])
        # Check basic format
        self.assertTrue(result.startswith("0x"))
        # Function selector is 4 bytes = 8 hex chars, plus "0x" = 10 chars minimum
        self.assertGreaterEqual(len(result), 10)
        # Should have reasonable length (at least function selector + some encoded data)
        self.assertGreater(len(result), 100)

    def test_encode_proxy_transaction_data_multiple(self):
        """Test encoding multiple proxy transactions"""
        tx1 = ProxyTransaction(
            to="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
            type_code=CallType.Call,
            data="0x095ea7b3",
            value="0",
        )
        tx2 = ProxyTransaction(
            to="0x4d97dcd97ec945f40cf65f87097ace5ea0476045",
            type_code=CallType.Call,
            data="0x095ea7b3",
            value="0",
        )
        result = encode_proxy_transaction_data([tx1, tx2])
        # Check basic format
        self.assertTrue(result.startswith("0x"))
        # Multiple transactions should be longer than single transaction
        single_result = encode_proxy_transaction_data([tx1])
        self.assertGreater(len(result), len(single_result))
