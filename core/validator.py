from core.transaction import Transaction, compute_tx_id, verify_signature
from core.dag import DAG
from core.balance import get_balance, get_pending_outbound
import time

class ValidationError(Exception):
    pass

def validate(tx: Transaction, dag: DAG, balance_cache: dict[str, int], applied_tx_ids: set[str], secret_key: str) -> None:
    # Rule 1 — Schema completeness handled by dataclass and web routing
    
    # Rule 2 — Amount is positive integer
    if not isinstance(tx.amount, int) or tx.amount <= 0:
        raise ValidationError("Amount must be a positive integer")

    # Rule 3 — Sender ≠ Receiver
    if tx.sender == tx.receiver:
        raise ValidationError("Sender cannot be receiver")
        
    # Rule 4 — Timestamp plausibility
    now_ms = int(time.time() * 1000)
    if abs(tx.timestamp - now_ms) > 300_000:
        raise ValidationError("Timestamp too far from current time")
        
    # Rule 5 — tx_id integrity
    expected_id = compute_tx_id(tx.sender, tx.receiver, tx.amount, tx.timestamp, tx.nonce, tx.parents)
    if expected_id != tx.tx_id:
        raise ValidationError("Invalid tx_id hash")
        
    # Rule 6 — Not already seen explicitly checked in ingestion path generally, but check DAG
    if tx.tx_id in dag.transactions:
        raise ValidationError("Transaction already exists in DAG")
        
    # Rule 7 — Signature validity
    if tx.sender != "GENESIS":
        if not verify_signature(tx.tx_id, tx.signature, secret_key):
            raise ValidationError("Invalid signature")
            
    # Rule 8 — Parents exist
    if tx.sender != "GENESIS":
        if tx.parents[0] not in dag.transactions or tx.parents[1] not in dag.transactions:
            raise ValidationError("Parents do not exist in DAG")
            
    # Rule 9 — No self-reference
    if tx.tx_id in tx.parents:
        raise ValidationError("Transaction cannot reference itself")
        
    # Rule 10 — Sufficient AVAILABLE balance
    if tx.sender != "GENESIS":
        confirmed_balance  = balance_cache.get(tx.sender, 0)
        pending_outbound   = get_pending_outbound(tx.sender, dag.transactions, applied_tx_ids)
        available_balance  = confirmed_balance - pending_outbound

        if available_balance < tx.amount:
            raise ValidationError("Insufficient available funds")
