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

def test_invalid_signature():
    dag = DAG()
    now_ms = int(time.time() * 1000)
    tx_id = compute_tx_id("00"*32, "01"*32, 200, now_ms, 1, ("11"*32, "11"*32))
    # Valid hex but mathematically wrong for signing
    sig = sign_transaction(tx_id, "FF"*32)
    
    tx1 = Transaction("00"*32, "01"*32, 200, ("11"*32, "11"*32), now_ms, 1, sig, tx_id)
    with pytest.raises(ValidationError, match="Invalid signature"):
        validate(tx1, dag, {"00"*32: 1000}, set(), secret_key="00"*32)

def test_insufficient_balance():
    dag = DAG()
    now_ms = int(time.time() * 1000)
    
    # Needs valid parents in DAG for rule 8
    dummy_parent = Transaction("GENESIS", "00"*32, 1000, ("", ""), now_ms, 0, "sig", "11"*32)
    dag.add_transaction(dummy_parent)
    
    tx_id = compute_tx_id("00"*32, "01"*32, 500, now_ms, 1, ("11"*32, "11"*32))
    sig = sign_transaction(tx_id, "00"*32)
    
    tx1 = Transaction("00"*32, "01"*32, 500, ("11"*32, "11"*32), now_ms, 1, sig, tx_id)
    with pytest.raises(ValidationError, match="Insufficient available funds"):
        validate(tx1, dag, {"00"*32: 100}, set(), secret_key="00"*32)

def test_double_spend_pending():
    dag = DAG()
    now_ms = int(time.time() * 1000)
    cache = {"00"*32: 500}
    
    # tx1 is pending bounds
    tx1_id = compute_tx_id("00"*32, "01"*32, 400, now_ms, 1, ("11"*32, "11"*32))
    sig1 = sign_transaction(tx1_id, "00"*32)
    tx_pending = Transaction("00"*32, "01"*32, 400, ("11"*32, "11"*32), now_ms, 1, sig1, tx1_id)
    dag.add_transaction(tx_pending)
    
    # tx2 double spends
    tx2_id = compute_tx_id("00"*32, "02"*32, 200, now_ms, 2, (tx1_id, tx1_id))
    sig2 = sign_transaction(tx2_id, "00"*32)
    tx_attempt = Transaction("00"*32, "02"*32, 200, (tx1_id, tx1_id), now_ms, 2, sig2, tx2_id)
    
    with pytest.raises(ValidationError, match="Insufficient available funds"):
        validate(tx_attempt, dag, cache, set(), secret_key="00"*32)

def test_stale_timestamp():
    dag = DAG()
    too_old_ms = int(time.time() * 1000) - 400_000 
    tx_id = compute_tx_id("00"*32, "01"*32, 200, too_old_ms, 1, ("11"*32, "11"*32))
    sig = sign_transaction(tx_id, "00"*32)
    
    tx_stale = Transaction("00"*32, "01"*32, 200, ("11"*32, "11"*32), too_old_ms, 1, sig, tx_id)
    with pytest.raises(ValidationError, match="Timestamp too far from current time"):
        validate(tx_stale, dag, {"00"*32: 1000}, set(), secret_key="00"*32)
