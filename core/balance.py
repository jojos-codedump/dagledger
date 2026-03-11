from core.transaction import Transaction

def apply_transaction(tx: Transaction, cache: dict[str, int]) -> None:
    if tx.sender != "GENESIS":
        cache[tx.sender] = cache.get(tx.sender, 0) - tx.amount
    cache[tx.receiver] = cache.get(tx.receiver, 0) + tx.amount

def get_balance(pubkey: str, cache: dict[str, int]) -> int:
    return cache.get(pubkey, 0)

def get_pending_outbound(pubkey: str, transactions: dict[str, Transaction], applied_ids: set[str]) -> int:
    """Sum of amounts in unconfirmed outbound txs for this sender."""
    return sum(
        tx.amount
        for tx in transactions.values()
        if tx.sender == pubkey
        and tx.tx_id not in applied_ids
    )
