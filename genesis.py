from core.transaction import Transaction, compute_tx_id

GENESIS_SENDER = "GENESIS"
# Use a 64-character hex string as a dummy address for receiver
GENESIS_RECEIVER = "0000000000000000000000000000000000000000000000000000000000000000"
GENESIS_AMOUNT = 1_000_000
GENESIS_TIMESTAMP = 1700000000000 # fixed time
GENESIS_NONCE = 0
GENESIS_PARENTS = ("", "")

GENESIS_TX_ID = compute_tx_id(
    sender=GENESIS_SENDER,
    receiver=GENESIS_RECEIVER,
    amount=GENESIS_AMOUNT,
    timestamp=GENESIS_TIMESTAMP,
    nonce=GENESIS_NONCE,
    parents=GENESIS_PARENTS
)

GENESIS_TX = Transaction(
    sender=GENESIS_SENDER,
    receiver=GENESIS_RECEIVER,
    amount=GENESIS_AMOUNT,
    parents=GENESIS_PARENTS,
    timestamp=GENESIS_TIMESTAMP,
    nonce=GENESIS_NONCE,
    signature="GENESIS_SIGNATURE",
    tx_id=GENESIS_TX_ID
)
