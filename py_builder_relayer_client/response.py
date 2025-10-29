from typing import List, Optional
from .models import SafeTransaction, RelayerTransactionState


class ClientRelayerTransactionResponse:
    def __init__(self, transaction_id: str, transaction_hash: str, client):
        self.transaction_id = transaction_id
        self.transaction_hash = transaction_hash
        self.hash = transaction_hash
        self.client = client

    def get_transaction(self) -> List[SafeTransaction]:
        return self.client.get_transaction(self.transaction_id)

    def wait(self) -> Optional[SafeTransaction]:
        """
        Wait for the transaction to reach a terminal state (mined or confirmed)
        """
        if self.transaction_id is None:
            return None
        return self.client.poll_until_state(
            transaction_id=self.transaction_id,
            states=[
                RelayerTransactionState.STATE_MINED.value,
                RelayerTransactionState.STATE_CONFIRMED.value,
            ],
            fail_state=RelayerTransactionState.STATE_FAILED.value,
            max_polls=30,
        )
