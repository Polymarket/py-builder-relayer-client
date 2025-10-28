from py_builder_signing_sdk.config import BuilderConfig, BuilderApiKeyCreds

from .signer import Signer
from .config import get_contract_config
from .http_helpers.helpers import get
from .types import SafeTransaction, SafeTransactionArgs, SafeCreateTransactionArgs
from .exceptions import RelayerClientException
from .endpoints import (
    GET_NONCE,
    GET_DEPLOYED,
    GET_TRANSACTION,
    GET_TRANSACTIONS,
    SUBMIT_TRANSACTION,
)


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

    def get_nonce(self, signer_adderss: str, signer_type: str):
        """
        Gets the nonce for the signer
        """
        return get(
            f"{self.relayer_url}{GET_NONCE}?address={signer_adderss}&type={signer_type}"
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

    def execute(self, transactions: list[SafeTransaction], metadata: str = None):
        self.assert_signer_needed()
        self.assert_builder_creds_needed()

        pass

    def deploy(self):
        self.assert_signer_needed()
        self.assert_builder_creds_needed()
        # TODO

        pass

    def get_deployed(self, safe_address) -> bool:

        # TODO
        return False

    def poll_until_state(
        self,
        transaction_id: str,
        states: list[str],
        failState: str = None,
        maxPolls: int = None,
        poll_freq: int = None,
    ):
        # TODO

        pass

    def assert_signer_needed(self):
        if self.signer is None:
            raise RelayerClientException("signer is required for this endpoint")

    def assert_builder_creds_needed(self):
        if self.builder_config is None:
            raise RelayerClientException(
                "builder credentials are required for this endpoint"
            )

    pass
