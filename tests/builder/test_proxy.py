from unittest import TestCase

from eth_utils import to_checksum_address

from py_builder_relayer_client.builder.proxy import (
    build_proxy_transaction_request,
    derive_proxy,
)
from py_builder_relayer_client.config import ContractConfig
from py_builder_relayer_client.models import ProxyTransactionArgs, RelayerTxType
from py_builder_relayer_client.signer import Signer


class TestProxy(TestCase):

    def test_derive_proxy(self):
        """Test proxy wallet address derivation"""
        address = "0x6e0c80c90ea6c15917308F820Eac91Ce2724B5b5"
        proxy_factory = "0xaacFeEa03eb1561C4e67d661e40682Bd20E3541b"
        proxy_address = derive_proxy(address, proxy_factory)
        # Verify it returns a valid checksummed address
        self.assertTrue(proxy_address.startswith("0x"))
        self.assertEqual(len(proxy_address), 42)
        self.assertEqual(proxy_address, to_checksum_address(proxy_address))

    def test_build_proxy_transaction_request(self):
        """Test building a proxy transaction request"""
        signer = Signer(
            private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
            chain_id=137,
        )
        config = ContractConfig(
            safe_factory="0xaacFeEa03eb1561C4e67d661e40682Bd20E3541b",
            safe_multisend="0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761",
            proxy_factory="0xaB45c5A4B0c941a2F231C04C3f49182e1A254052",
            relay_hub="0xD216153c06E857cD7f72665E0aF1d7D82172F494",
        )
        args = ProxyTransactionArgs(
            from_address=signer.address(),
            gas_price="0",
            data="0x095ea7b3",
            relay="0x1234567890123456789012345678901234567890",
            nonce="0",
        )
        request = build_proxy_transaction_request(
            signer=signer,
            args=args,
            config=config,
            metadata="test",
        )
        self.assertEqual(request.type, "PROXY")
        self.assertEqual(request.from_address, signer.address())
        self.assertEqual(request.to, config.proxy_factory)
        self.assertIsNotNone(request.proxy)
        self.assertIsNotNone(request.signature)
        self.assertEqual(request.metadata, "test")
        self.assertEqual(request.nonce, "0")
        self.assertIsNotNone(request.signature_params)
        self.assertEqual(request.signature_params.relay, args.relay)
        self.assertEqual(request.signature_params.relay_hub, config.relay_hub)
