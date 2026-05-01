from unittest import TestCase

from py_builder_relayer_client.builder.deposit_wallet import (
    build_deposit_wallet_batch_request,
    build_deposit_wallet_create_request,
)
from py_builder_relayer_client.config import get_contract_config
from py_builder_relayer_client.models import (
    DepositWalletCall,
    DepositWalletTransactionArgs,
    TransactionType,
)
from py_builder_relayer_client.signer import Signer


# Public Hardhat/Anvil fixture key. This is not a live credential.
TEST_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
WALLET = "0xa2927E7834648F1C03b4961CeeA4597292e3c025"
TOKEN = "0x0000000000000000000000000000000000000001"
APPROVE_CALLDATA = "0x095ea7b30000000000000000000000000000000000000000000000000000000000000002ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
EXPECTED_BATCH_SIGNATURE = "0x7827946c566e7860f6c5f2e641587ed6928989c8618e463a00dd56832e7300023b7436c67a2ea82d6d506b1a5eda3e27526e9e2ffaad52128d75c47c2e9d1fac1b"


class TestDepositWallet(TestCase):

    def test_build_deposit_wallet_create_request(self):
        config = get_contract_config(137)
        req = build_deposit_wallet_create_request(ADDRESS, config)

        self.assertEqual(
            {
                "type": TransactionType.WALLET_CREATE.value,
                "from": ADDRESS,
                "to": config.deposit_wallet_factory,
            },
            req.to_dict(),
        )

    def test_build_deposit_wallet_batch_request(self):
        config = get_contract_config(137)
        signer = Signer(private_key=TEST_PRIVATE_KEY, chain_id=137)
        call = DepositWalletCall(target=TOKEN, value="0", data=APPROVE_CALLDATA)
        args = DepositWalletTransactionArgs(
            from_address=ADDRESS,
            chain_id=137,
            wallet_address=WALLET,
            nonce="0",
            deadline="1234567890",
            calls=[call],
        )

        req = build_deposit_wallet_batch_request(signer, args, config)
        payload = req.to_dict()

        self.assertEqual(EXPECTED_BATCH_SIGNATURE, req.signature)
        self.assertTrue(req.signature.startswith("0x"))
        self.assertEqual(132, len(req.signature))
        self.assertEqual(TransactionType.WALLET.value, payload["type"])
        self.assertEqual(ADDRESS, payload["from"])
        self.assertEqual(config.deposit_wallet_factory, payload["to"])
        self.assertEqual("0", payload["nonce"])
        self.assertEqual(EXPECTED_BATCH_SIGNATURE, payload["signature"])
        self.assertEqual(
            {
                "depositWallet": WALLET,
                "deadline": "1234567890",
                "calls": [
                    {
                        "target": TOKEN,
                        "value": "0",
                        "data": APPROVE_CALLDATA,
                    },
                ],
            },
            payload["depositWalletParams"],
        )
