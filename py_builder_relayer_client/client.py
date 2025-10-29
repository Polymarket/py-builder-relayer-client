import logging
import time

from py_builder_signing_sdk.config import BuilderConfig
from typing import List, Optional

from .signer import Signer
from .config import get_contract_config
from .constants.constants import ZERO_ADDRESS
from .http_helpers.helpers import get, post, POST
from .builder.derive import derive
from .builder.safe import build_safe_transaction_request
from .builder.create import build_safe_create_transaction_request
from .models import (
    SafeTransaction,
    SafeTransactionArgs,
    SafeCreateTransactionArgs,
    TransactionType,
)
from .exceptions import RelayerClientException
from .endpoints import (
    GET_NONCE,
    GET_DEPLOYED,
    GET_TRANSACTION,
    GET_TRANSACTIONS,
    SUBMIT_TRANSACTION,
)
from .response import ClientRelayerTransactionResponse


class RelayClient:
    """
    Client for the Polymarket Relayer
    Authenticated with builder api key credentials
    """

    def __init__(
        self,
        relayer_url,
        chain_id: int,
        private_key: str = None,
        builder_config: BuilderConfig = None,
    ):
        self.relayer_url = (
            relayer_url[0:-1] if relayer_url.endswith("/") else relayer_url
        )
        self.chain_id = chain_id
        self.contract_config = get_contract_config(chain_id)

        self.signer = None
        if private_key is not None:
            self.signer = Signer(private_key, chain_id)

        self.builder_config = None
        if builder_config is not None:
            self.builder_config = builder_config
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_nonce(self, signer_address: str, signer_type: str):
        """
        Gets the nonce for the signer
        """
        return get(
            f"{self.relayer_url}{GET_NONCE}?address={signer_address}&type={signer_type}"
        )

    def get_transaction(self, transaction_id: str):
        """
        Gets the transaction given the transaction_id
        """
        return get(f"{self.relayer_url}{GET_TRANSACTION}?id={transaction_id}")

    def get_transactions(self):
        """
        Gets all transactions for the builder
        """
        return get(f"{self.relayer_url}{GET_TRANSACTIONS}")

    def get_deployed(self, safe_address) -> bool:
        """
        Returns a boolean that indicates if a safe is deployed
        """
        deployed_payload = get(
            f"{self.relayer_url}{GET_DEPLOYED}?address={safe_address}"
        )
        if deployed_payload and deployed_payload.get("deployed"):
            return bool(deployed_payload.get("deployed"))
        return False

    def execute(self, transactions: list[SafeTransaction], metadata: str = None):
        self.assert_signer_needed()
        self.assert_builder_creds_needed()
        safe_address = self.get_expected_safe()

        deployed = self.get_deployed(safe_address)
        if not deployed:
            raise RelayerClientException(
                f"expected safe {safe_address} is not deployed"
            )

        from_address = self.signer.address()

        nonce_payload = self.get_nonce(from_address, TransactionType.SAFE.value)
        nonce = 0
        if nonce_payload is None or nonce_payload.get("nonce") is None:
            raise RelayerClientException("invalid nonce payload received")
        nonce = nonce_payload.get("nonce")

        safe_args = SafeTransactionArgs(
            from_address=from_address,
            nonce=nonce,
            chain_id=self.chain_id,
            transactions=transactions,
        )

        txn_request = build_safe_transaction_request(
            signer=self.signer,
            args=safe_args,
            config=self.contract_config,
            metadata=metadata,
        ).to_dict()

        self.logger.debug(f"Created transaction request: {txn_request}")
        resp = self._post_request(POST, SUBMIT_TRANSACTION, txn_request)
        return ClientRelayerTransactionResponse(
            resp.get("transactionID"),
            resp.get("transactionHash"),
            self,
        )

    def deploy(self):
        self.assert_signer_needed()
        self.assert_builder_creds_needed()

        safe_address = self.get_expected_safe()
        deployed = self.get_deployed(safe_address)
        if deployed:
            raise RelayerClientException(f"safe {safe_address} is already deployed!")

        from_address = self.signer.address()

        args = SafeCreateTransactionArgs(
            from_address=from_address,
            chain_id=self.chain_id,
            payment_token=ZERO_ADDRESS,
            payment="0",
            payment_receiver=ZERO_ADDRESS,
        )

        txn_request = build_safe_create_transaction_request(
            self.signer, args, self.contract_config
        ).to_dict()

        self.logger.debug(f"Created transaction request: {txn_request}")
        resp = self._post_request(POST, SUBMIT_TRANSACTION, txn_request)

        return ClientRelayerTransactionResponse(
            resp.get("transactionID"),
            resp.get("transactionHash"),
            self,
        )

    def poll_until_state(
        self,
        transaction_id: str,
        states: List[str],
        fail_state: str,
        max_polls: Optional[int] = None,
        poll_frequency: Optional[int] = None,
    ):
        target_states = set(list(states))

        poll_limit = max_polls if max_polls is not None else 10

        poll_frequency_ms = 2000
        if poll_frequency is not None and poll_frequency >= 1000:
            poll_frequency_ms = poll_frequency

        print(
            f"Waiting for transaction {transaction_id} matching states: {target_states}..."
        )

        for _ in range(poll_limit):
            transactions = self.get_transaction(transaction_id)
            if transactions:
                txn = transactions[0]
                txn_state = txn.get("state")
                if (
                    txn_state
                    and isinstance(txn_state, str)
                    and txn_state in target_states
                ):
                    return txn
                if fail_state is not None and txn_state == fail_state:
                    txn_hash = txn.get("transactionHash")
                    self.logger.error(
                        f"txn {transaction_id} failed onchain, transaction_hash: {txn_hash}!"
                    )
                    return None
            time.sleep(poll_frequency_ms / 1000)

        self.logger.info(
            f"Transaction {transaction_id} not found or not in given states, timing out!"
        )
        return None

    def _post_request(self, method: str, request_path: str, body: dict = None):
        builder_headers = self._generate_builder_headers(method, request_path, body)
        if builder_headers is None:
            raise RelayerClientException("could not generate builder headers")
        return post(
            f"{self.relayer_url}{request_path}", headers=builder_headers, data=body
        )

    def _generate_builder_headers(
        self, method: str, request_path: str, body: dict = None
    ) -> Optional[dict]:
        if body is not None:
            body = str(body)
        headers = self.builder_config.generate_builder_headers(
            method, request_path, body
        )
        return headers.to_dict() if headers is not None else None

    def get_expected_safe(self):
        """
        Returns the expected safe for the signer
        """
        self.assert_signer_needed()
        addr = self.signer.address()
        return derive(addr, self.contract_config.safe_factory)

    def assert_signer_needed(self):
        if self.signer is None:
            raise RelayerClientException("signer is required for this endpoint")

    def assert_builder_creds_needed(self):
        if self.builder_config is None:
            raise RelayerClientException(
                "builder credentials are required for this endpoint"
            )
