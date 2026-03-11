import logging
import asyncio
from typing import Tuple
from core.transaction import Transaction, to_dict
from core.validator import validate, ValidationError
from core.dag import is_confirmed
from core.balance import apply_transaction

logger = logging.getLogger(__name__)

async def ingest_transaction(tx: Transaction, state, exclude_node_id: str = "", secret_key: str = "") -> Tuple[bool, str]:
    """
    Single authoritative path for adding a transaction to the DAG.
    Used by both the REST API and the P2P gossip layer.
    Returns True if ingested, False if rejected.
    """
    if tx.tx_id in state.seen_ids:
        return False, "already seen"

    try:
        validate(tx, state.dag, state.balance_cache, state.applied_tx_ids, secret_key)
    except ValidationError as e:
        logger.warning(f"Rejected tx {tx.tx_id[:8]}: {e}")
        return False, str(e)

    state.seen_ids.add(tx.tx_id)
    state.dag.add_transaction(tx)

    for unapplied_id in list(state.dag.transactions.keys() - state.applied_tx_ids):
        if is_confirmed(state.dag, unapplied_id):
            unapplied_tx = state.dag.transactions[unapplied_id]
            apply_transaction(unapplied_tx, state.balance_cache)
            state.applied_tx_ids.add(unapplied_id)

    from network.gossip import broadcast
    asyncio.create_task(broadcast({"type": "NEW_TX", "tx": to_dict(tx)}, exclude_node_id, state))
    return True, ""
