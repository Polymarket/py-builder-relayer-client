import logging
import time

import requests

from py_builder_signing_sdk.config import BuilderConfig
from typing import List, Optional

from .signer import Signer
from .config import (
    get_contract_config,
    is_proxy_config_valid,
    is_safe_config_valid,
    is_deposit_wallet_config_valid,
)
from .constants.constants import ZERO_ADDRESS
from .gas import estimate_gas, DEFAULT_GAS_LIMIT
from .http_helpers.helpers import get, post, POST
from .builder.derive import (
    derive,
    derive_beacon_deposit_wallet,
    derive_uups_deposit_wallet,
    derive_proxy_wallet,
)
from .builder.safe import build_safe_transaction_request
from .builder.proxy import build_proxy_transaction_request
from .builder.create import build_safe_create_transaction_request
from .builder.deposit_wallet import (
    build_deposit_wallet_batch_request,
    build_deposit_wallet_create_request,
)
from .encode.proxy import encode_proxy_transaction_data
from .models import (
    SafeTransaction,
    SafeTransactionArgs,
    SafeCreateTransactionArgs,
    DepositWalletCall,
    DepositWalletTransactionArgs,
    TransactionType,
    Transaction,
    RelayerTxType,
    OperationType,
    CallType,
    ProxyTransaction,
    ProxyTransactionArgs,
)
from .exceptions import RelayerClientException
from .endpoints import (
    GET_NONCE,
    GET_DEPLOYED,
    GET_TRANSACTION,
    GET_TRANSACTIONS,
    SUBMIT_TRANSACTION,
    GET_RELAY_PAYLOAD,
)
from .response import ClientRelayerTransactionResponse


FACTORY_BEACON_SELECTOR = "0x49493a4d"
DEFAULT_RPC_URLS = {
    137: "https://polygon-rpc.com",
    80002: "https://rpc-amoy.polygon.technology",
}


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
        relay_tx_type=None,
        rpc_url: str = None,
    ):
        self.relayer_url = (
            relayer_url[0:-1] if relayer_url.endswith("/") else relayer_url
        )
        self.chain_id = chain_id
        self.contract_config = get_contract_config(chain_id)
        self.rpc_url = rpc_url or DEFAULT_RPC_URLS.get(chain_id)

        self.signer = None
        if private_key is not None:
            self.signer = Signer(private_key, chain_id)

        self.builder_config = None
        if builder_config is not None:
            self.builder_config = builder_config
        self.logger = logging.getLogger(self.__class__.__name__)

        self.relay_tx_type = (
            relay_tx_type if relay_tx_type is not None else RelayerTxType.SAFE
        )

    def get_nonce(self, signer_address: str, signer_type: str):
        """
        Gets the nonce for the signer
        """
        return get(
            f"{self.relayer_url}{GET_NONCE}?address={signer_address}&type={signer_type}"
        )

    def get_relay_payload(self, signer_address: str, signer_type: str):
        """
        Gets the relay payload for the signer
        """
        return get(
            f"{self.relayer_url}{GET_RELAY_PAYLOAD}?address={signer_address}&type={signer_type}"
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

    def get_deployed(self, address: str, signer_type: str = None) -> bool:
        """
        Returns a boolean that indicates if an address is deployed
        """
        path = f"{self.relayer_url}{GET_DEPLOYED}?address={address}"
        if signer_type is not None:
            path = f"{path}&type={signer_type}"
        deployed_payload = get(path)
        if deployed_payload and deployed_payload.get("deployed"):
            return bool(deployed_payload.get("deployed"))
        return False

    def execute(self, transactions: list[Transaction], metadata: str = None):
        self.assert_signer_needed()
        self.assert_builder_creds_needed()
        if len(transactions) == 0:
            raise RelayerClientException("no transactions to execute")

        if self.relay_tx_type == RelayerTxType.SAFE:
            safe_txns = [
                SafeTransaction(
                    to=t.to,
                    operation=OperationType.Call,
                    data=t.data,
                    value="0",
                )
                for t in transactions
            ]
            return self._execute_safe_transactions(safe_txns, metadata)
        elif self.relay_tx_type == RelayerTxType.PROXY:
            proxy_txns = [
                ProxyTransaction(
                    to=t.to,
                    type_code=CallType.Call,
                    data=t.data,
                    value="0",
                )
                for t in transactions
            ]
            return self._execute_proxy_transactions(proxy_txns, metadata)
        else:
            raise RelayerClientException(
                f"Unsupported relay transaction type: {self.relay_tx_type}"
            )

    def _execute_safe_transactions(
        self, transactions: list[SafeTransaction], metadata: str = None
    ):
        if not is_safe_config_valid(self.contract_config):
            raise RelayerClientException(
                "Safe contracts are not configured for this chain"
            )

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

    def _execute_proxy_transactions(
        self, transactions: list[ProxyTransaction], metadata: str = None
    ):
        if not is_proxy_config_valid(self.contract_config):
            raise RelayerClientException(
                "Proxy contracts are not configured for this chain"
            )

        from_address = self.signer.address()

        relay_payload = self.get_relay_payload(
            from_address, TransactionType.PROXY.value
        )
        if (
            relay_payload is None
            or relay_payload.get("nonce") is None
            or relay_payload.get("address") is None
        ):
            raise RelayerClientException("invalid relay payload received")

        encoded_data = encode_proxy_transaction_data(transactions)

        gas_limit = self._estimate_proxy_gas(
            from_address, self.contract_config.proxy_factory, encoded_data
        )

        proxy_args = ProxyTransactionArgs(
            from_address=from_address,
            nonce=relay_payload.get("nonce"),
            gas_price="0",
            data=encoded_data,
            relay=relay_payload.get("address"),
            gas_limit=gas_limit,
        )

        txn_request = build_proxy_transaction_request(
            signer=self.signer,
            args=proxy_args,
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

    def deploy_deposit_wallet(self):
        self.assert_signer_needed()
        self.assert_builder_creds_needed()
        if not is_deposit_wallet_config_valid(self.contract_config):
            raise RelayerClientException(
                "Deposit wallet contracts are not configured for this chain"
            )

        from_address = self.signer.address()
        txn_request = build_deposit_wallet_create_request(
            from_address, self.contract_config
        ).to_dict()

        self.logger.debug(f"Created transaction request: {txn_request}")
        resp = self._post_request(POST, SUBMIT_TRANSACTION, txn_request)

        return ClientRelayerTransactionResponse(
            resp.get("transactionID"),
            resp.get("transactionHash"),
            self,
        )

    def execute_deposit_wallet_batch(
        self,
        calls: list[DepositWalletCall],
        wallet_address: str,
        nonce: str,
        deadline: str,
    ):
        self.assert_signer_needed()
        self.assert_builder_creds_needed()
        if not is_deposit_wallet_config_valid(self.contract_config):
            raise RelayerClientException(
                "Deposit wallet contracts are not configured for this chain"
            )

        from_address = self.signer.address()
        args = DepositWalletTransactionArgs(
            from_address=from_address,
            chain_id=self.chain_id,
            wallet_address=wallet_address,
            nonce=nonce,
            deadline=deadline,
            calls=calls,
        )

        txn_request = build_deposit_wallet_batch_request(
            signer=self.signer,
            args=args,
            config=self.contract_config,
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

    def _estimate_proxy_gas(self, from_address: str, to: str, data: str) -> str:
        if self.rpc_url is None:
            return str(DEFAULT_GAS_LIMIT)

        try:
            gas = estimate_gas(self.rpc_url, from_address, to, data)
            return str(gas)
        except (ValueError, requests.RequestException) as e:
            self.logger.debug(f"Gas estimation failed, using default: {e}")
            return str(DEFAULT_GAS_LIMIT)

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

    def get_expected_proxy_wallet(self):
        """
        Returns the expected proxy wallet for the signer
        """
        self.assert_signer_needed()
        if not is_proxy_config_valid(self.contract_config):
            raise RelayerClientException(
                "Proxy contracts are not configured for this chain"
            )
        addr = self.signer.address()
        return derive_proxy_wallet(addr, self.contract_config.proxy_factory)

    def get_expected_deposit_wallet(self):
        """
        Returns the expected deposit wallet for the signer
        """
        self.assert_signer_needed()
        if not is_deposit_wallet_config_valid(self.contract_config):
            raise RelayerClientException(
                "Deposit wallet contracts are not configured for this chain"
            )
        addr = self.signer.address()
        uups_address = derive_uups_deposit_wallet(
            addr,
            self.contract_config.deposit_wallet_factory,
            self.contract_config.deposit_wallet_implementation,
        )
        beacon = self._get_deposit_wallet_factory_beacon(
            self.contract_config.deposit_wallet_factory
        )
        if beacon.lower() == ZERO_ADDRESS.lower():
            return uups_address
        if self._is_contract_deployed(uups_address):
            return uups_address
        return derive_beacon_deposit_wallet(
            addr,
            self.contract_config.deposit_wallet_factory,
            beacon,
        )

    def _get_deposit_wallet_factory_beacon(self, factory: str) -> str:
        try:
            data = self._rpc_call(
                "eth_call",
                [{"to": factory, "data": FACTORY_BEACON_SELECTOR}, "latest"],
            )
        except ValueError as error:
            if _is_rpc_revert(error):
                return ZERO_ADDRESS
            raise
        return _decode_address_return_data(data)

    def _is_contract_deployed(self, address: str) -> bool:
        code = self._rpc_call("eth_getCode", [address, "latest"])
        return code not in (None, "0x")

    def _rpc_call(self, method: str, params: list):
        if self.rpc_url is None:
            raise RelayerClientException("rpc_url is required for this endpoint")
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        response = requests.post(self.rpc_url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        if "error" in result:
            raise ValueError(f"RPC error: {result['error']}")
        if "result" not in result:
            raise ValueError("No result in RPC response")
        return result.get("result")

    def assert_signer_needed(self):
        if self.signer is None:
            raise RelayerClientException("signer is required for this endpoint")

    def assert_builder_creds_needed(self):
        if self.builder_config is None:
            raise RelayerClientException(
                "builder credentials are required for this endpoint"
            )


def _decode_address_return_data(data: str) -> str:
    if data is None or len(data) < 66:
        return ZERO_ADDRESS
    return "0x" + data[-40:]


def _is_rpc_revert(error: ValueError) -> bool:
    message = str(error).lower()
    return "revert" in message or "'code': 3" in message or '"code": 3' in message
