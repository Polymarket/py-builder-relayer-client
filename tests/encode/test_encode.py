from unittest import TestCase

from py_builder_relayer_client.models import SafeTransaction, OperationType
from py_builder_relayer_client.encode.safe import create_safe_multisend_transaction


class TestMultisend(TestCase):

    def test_create_safe_multisend_transaction(self):
        # Declare 2 approve transactions
        safe_txn = SafeTransaction(
            to="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
            operation=OperationType.Call,
            data="0x095ea7b30000000000000000000000004d97dcd97ec945f40cf65f87097ace5ea0476045ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
            value="0",
        )

        safe_multisend_address = "0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761"

        multisend_txn = create_safe_multisend_transaction(
            [safe_txn, safe_txn], safe_multisend_address
        )

        # Generated with Typescript client
        expected_to = "0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761"
        expected_value = "0"
        expected_operation = 1
        expected_data = "0x8d80ff0a00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000132002791bca1f2de4661ed88a30c99a7a9449aa8417400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044095ea7b30000000000000000000000004d97dcd97ec945f40cf65f87097ace5ea0476045ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff002791bca1f2de4661ed88a30c99a7a9449aa8417400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044095ea7b30000000000000000000000004d97dcd97ec945f40cf65f87097ace5ea0476045ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff0000000000000000000000000000"

        self.assertIsNotNone(multisend_txn)
        self.assertEqual(expected_to, multisend_txn.to)
        self.assertEqual(expected_value, multisend_txn.value)
        self.assertEqual(expected_operation, multisend_txn.operation.value)
        self.assertEqual(expected_data, multisend_txn.data)
