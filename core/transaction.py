from dataclasses import dataclass, asdict
import hashlib
import struct
import hmac

@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: int
    parents: tuple[str, str]
    timestamp: int
    nonce: int
    signature: str
    tx_id: str = ""

def compute_tx_id(sender: str, receiver: str, amount: int, timestamp: int, nonce: int, parents: tuple[str, str]) -> str:
    # Decode 64-char hex strings into 32 bytes
    sender_bytes = bytes.fromhex(sender) if sender != "GENESIS" else b"GENESIS".ljust(32, b'\0')
    receiver_bytes = bytes.fromhex(receiver)
    p1_bytes = bytes.fromhex(parents[0]) if parents[0] else b'\0'*32
    p2_bytes = bytes.fromhex(parents[1]) if parents[1] else b'\0'*32
    
    # Format: >32s32sQQI32s32s
    packed = struct.pack(">32s32sQQI32s32s", sender_bytes, receiver_bytes, amount, timestamp, nonce, p1_bytes, p2_bytes)
    return hashlib.sha256(packed).hexdigest()

def sign_transaction(tx_id: str, secret_key: str) -> str:
    # Secret key must be a 64-character hex string (32 bytes).
    key_bytes = bytes.fromhex(secret_key)
    msg_bytes = bytes.fromhex(tx_id)
    return hmac.new(key_bytes, msg_bytes, hashlib.sha256).hexdigest()

def verify_signature(tx_id: str, signature: str, secret_key: str) -> bool:
    expected = sign_transaction(tx_id, secret_key)
    return hmac.compare_digest(expected, signature)

def to_dict(tx: Transaction) -> dict:
    d = asdict(tx)
    d["parents"] = list(tx.parents) # list for msgpack
    return d

def from_dict(d: dict) -> Transaction:
    return Transaction(
        sender=d["sender"],
        receiver=d["receiver"],
        amount=int(d["amount"]),
        parents=tuple(d["parents"]),
        timestamp=int(d["timestamp"]),
        nonce=int(d["nonce"]),
        signature=d["signature"],
        tx_id=d["tx_id"]
    )
