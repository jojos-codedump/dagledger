import pytest
import time
from core.dag import DAG, select_tips, topological_sort
from core.transaction import Transaction

def test_genesis_tip():
    dag = DAG()
    tx = Transaction("GENESIS", "00"*32, 1000, ("", ""), 0, 0, "sig", "hash0")
    dag.add_transaction(tx)
    
    assert len(dag.tips) == 1
    assert "hash0" in dag.tips

def test_new_tx_updates_tips():
    dag = DAG()
    tx0 = Transaction("GENESIS", "00"*32, 1000, ("", ""), 0, 0, "sig", "hash0")
    dag.add_transaction(tx0)
    
    tx1 = Transaction("00"*32, "01"*32, 100, ("hash0", "hash0"), 10, 1, "sig", "hash1")
    dag.add_transaction(tx1)
    
    assert len(dag.tips) == 1
    assert "hash1" in dag.tips
    assert "hash0" not in dag.tips

def test_age_weighted_selection():
    dag = DAG()
    now_ms = int(time.time() * 1000)
    
    tx0 = Transaction("GENESIS", "00"*32, 1000, ("", ""), 0, 0, "sig", "hash0")
    dag.add_transaction(tx0)
    
    for i in range(1, 6):
        tx = Transaction("00"*32, "01"*32, 10, ("hash0", "hash0"), now_ms - (i * 10000), i, "sig", f"hash{i}")
        dag.add_transaction(tx)
        
    p1, p2 = select_tips(dag)
    assert p1 in dag.tips
    assert p2 in dag.tips
    assert p1 != p2 # Check >2 returns 2 distinct parents
