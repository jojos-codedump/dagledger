import pytest
import time
from core.validator import validate, ValidationError
from core.dag import DAG
from core.transaction import Transaction, compute_tx_id, sign_transaction

def test_valid_tx():
    dag = DAG()
    cache = {"00"*32: 1000}
    applied = set()
    
    now_ms = int(time.time() * 1000)
    tx0 = Transaction("GENESIS", "00"*32, 1000, ("", ""), now_ms, 0, "sig", "11"*32)
    dag.add_transaction(tx0)
    
    sender = "00"*32
    receiver = "01"*32
    parents = ("11"*32, "11"*32)
    amount = 200
    nonce = 1
    
    tx_id = compute_tx_id(sender, receiver, amount, now_ms, nonce, parents)
    sig = sign_transaction(tx_id, "00"*32) # Dummy secret_key
    
    tx1 = Transaction(sender, receiver, amount, parents, now_ms, nonce, sig, tx_id)
    
    validate(tx1, dag, cache, applied, secret_key="00"*32)

def test_invalid_amount():
    dag = DAG()
    tx = Transaction("GENESIS", "00"*32, -100, ("", ""), 0, 0, "sig", "11"*32)
    with pytest.raises(ValidationError, match="positive integer"):
        validate(tx, dag, {}, set(), secret_key="00"*32)
