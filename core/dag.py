from typing import Tuple, List, Set, Dict
import time
import random
from core.transaction import Transaction

class DAG:
    def __init__(self):
        self.transactions: Dict[str, Transaction] = {}
        self.children: Dict[str, Set[str]] = {}
        self.tips: Set[str] = set()

    def add_transaction(self, tx: Transaction):
        self.transactions[tx.tx_id] = tx
        
        for parent_id in tx.parents:
            if parent_id in self.children:
                self.children[parent_id].add(tx.tx_id)
            else:
                self.children[parent_id] = {tx.tx_id}
            
            if parent_id in self.tips:
                self.tips.remove(parent_id)
                
        self.tips.add(tx.tx_id)
        
    def get_all_ids(self) -> List[str]:
        return list(self.transactions.keys())

def is_confirmed(dag: DAG, tx_id: str, depth: int = 0) -> bool:
    direct_children = dag.children.get(tx_id, set())

    # Base case: enough direct references — definitively confirmed
    if len(direct_children) >= 2:
        return True

    # Depth cap to prevent stack overflow
    if depth > 5:
        return False

    # Recursive check
    return any(is_confirmed(dag, child_id, depth + 1) for child_id in direct_children)

def select_tips(dag: DAG) -> Tuple[str, str]:
    now_ms = int(time.time() * 1000)
    
    if len(dag.tips) == 1:
        tip_id = list(dag.tips)[0]
        return (tip_id, tip_id)
        
    if len(dag.tips) == 2:
        tip_list = list(dag.tips)
        return (tip_list[0], tip_list[1])
        
    if len(dag.tips) > 2:
        tip_list = list(dag.tips)
        # Clamped weights fix for NTP clock drift
        weights = [max(1, now_ms - dag.transactions[t].timestamp) for t in tip_list]
        sample = random.choices(tip_list, weights=weights, k=2)
        
        if sample[0] == sample[1]:
            best_fallback_tip = None
            max_w = -1
            for t, w in zip(tip_list, weights):
                if t != sample[0] and w > max_w:
                    max_w = w
                    best_fallback_tip = t
            sample[1] = best_fallback_tip if best_fallback_tip else tip_list[0]
            
        return (sample[0], sample[1])
    
    return ("", "")

def topological_sort(txs: List[Transaction]) -> List[Transaction]:
    """
    Kahn's algorithm to sort an arbitrary batch of transactions during sync
    so that parents are appended before children that reference them.
    """
    tx_dict = {tx.tx_id: tx for tx in txs}
    result = []
    
    while tx_dict:
        roots = []
        for tx_id, tx in tx_dict.items():
            if all(p not in tx_dict for p in tx.parents):
                roots.append(tx_id)
                
        if not roots:
            break # circular dependency
            
        for root_id in roots:
            result.append(tx_dict[root_id])
            del tx_dict[root_id]
            
    return result
