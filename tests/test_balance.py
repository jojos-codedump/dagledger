import pytest
from core.dag import DAG
from core.transaction import Transaction
from core.balance import apply_transaction, get_balance

def test_genesis_balance():
    cache = {}
    tx0 = Transaction("GENESIS", "00"*32, 1000, ("", ""), 0, 0, "sig", "hash0")
    apply_transaction(tx0, cache)
    
    assert get_balance("00"*32, cache) == 1000
    assert get_balance("GENESIS", cache) == 0

def test_transfer_balance():
    cache = {}
    tx0 = Transaction("GENESIS", "00"*32, 1000, ("", ""), 0, 0, "sig", "hash0")
    apply_transaction(tx0, cache)
    
    tx1 = Transaction("00"*32, "01"*32, 300, ("hash0", "hash0"), 0, 0, "sig", "hash1")
    apply_transaction(tx1, cache)
    
    assert get_balance("00"*32, cache) == 700
    assert get_balance("01"*32, cache) == 300
