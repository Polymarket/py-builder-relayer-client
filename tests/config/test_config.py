from py_builder_relayer_client.config import get_contract_config
from py_builder_relayer_client.exceptions import RelayerClientException
from unittest import TestCase


class TestConfig(TestCase):
    def test_get_contract_config(self):
        chain_id = 137
        cfg = get_contract_config(chain_id)
        self.assertEqual("0xaacFeEa03eb1561C4e67d661e40682Bd20E3541b", cfg.safe_factory)
        self.assertEqual(
            "0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761", cfg.safe_multisend
        )

        chain_id = 80002
        cfg = get_contract_config(chain_id)
        self.assertEqual("0xaacFeEa03eb1561C4e67d661e40682Bd20E3541b", cfg.safe_factory)
        self.assertEqual(
            "0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761", cfg.safe_multisend
        )

        chain_id = 1
        with self.assertRaises(RelayerClientException):
            cfg = get_contract_config(chain_id)
