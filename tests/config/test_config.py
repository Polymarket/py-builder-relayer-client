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
        self.assertEqual(
            "0x894Ee6B254f251518206f709E9B115f214ebDf17",
            cfg.deposit_wallet_factory,
        )
        self.assertEqual(
            "0x55913A0bdecCbB77b7Af781A48300e6394B5EEAE",
            cfg.deposit_wallet_implementation,
        )

        chain_id = 80002
        cfg = get_contract_config(chain_id)
        self.assertEqual("0xaacFeEa03eb1561C4e67d661e40682Bd20E3541b", cfg.safe_factory)
        self.assertEqual(
            "0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761", cfg.safe_multisend
        )
        self.assertEqual(
            "0x801c740Bcd28531d75a5da176D5511F3329Ab049",
            cfg.deposit_wallet_factory,
        )
        self.assertEqual(
            "0x24f3257BF9451bA575E864777ab6f8D7Eac0139B",
            cfg.deposit_wallet_implementation,
        )

        chain_id = 1
        with self.assertRaises(RelayerClientException):
            cfg = get_contract_config(chain_id)
