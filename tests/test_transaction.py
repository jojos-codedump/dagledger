import pytest
from core.transaction import Transaction, compute_tx_id

def test_deterministic_hash():
    sender = "0000000000000000000000000000000000000000000000000000000000000001"
    receiver = "0000000000000000000000000000000000000000000000000000000000000002"
    amount = 5000
    timestamp = 1600000000000
    nonce = 1
    parents = ("", "")
    
    hash1 = compute_tx_id(sender, receiver, amount, timestamp, nonce, parents)
    hash2 = compute_tx_id(sender, receiver, amount, timestamp, nonce, parents)
    assert hash1 == hash2

def test_hash_mutation():
    sender = "0000000000000000000000000000000000000000000000000000000000000001"
    receiver = "0000000000000000000000000000000000000000000000000000000000000002"
    parents = ("", "")
    
    hash_base = compute_tx_id(sender, receiver, 5000, 1600000000000, 1, parents)
    hash_mut_amount = compute_tx_id(sender, receiver, 5001, 1600000000000, 1, parents)
    hash_mut_nonce = compute_tx_id(sender, receiver, 5000, 1600000000000, 2, parents)
    
    assert hash_base != hash_mut_amount
    assert hash_base != hash_mut_nonce
