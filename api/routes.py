from fastapi import APIRouter, Request, HTTPException
from core.transaction import Transaction, to_dict
from core.service import ingest_transaction
from core.balance import get_balance
from core.dag import is_confirmed
import config
import time

router = APIRouter()

@router.post("/tx")
async def create_tx(request: Request, tx_in: dict):
    state = request.app.state.node
    
    try:
        tx = Transaction(
            sender    = tx_in["sender"],
            receiver  = tx_in["receiver"],
            amount    = tx_in["amount"],
            parents   = tuple(tx_in["parents"]),
            timestamp = tx_in["timestamp"],
            nonce     = tx_in["nonce"],
            signature = tx_in["signature"],
            tx_id     = tx_in["tx_id"],
        )
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload construction: {e}")
        
    accepted, reason = await ingest_transaction(tx, state, secret_key=config.SECRET_KEY)
    if not accepted:
        raise HTTPException(status_code=422, detail=reason)
        
    return {"tx_id": tx.tx_id}

@router.get("/tx/{tx_id}")
async def get_tx(request: Request, tx_id: str):
    state = request.app.state.node
    if tx_id not in state.dag.transactions:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return to_dict(state.dag.transactions[tx_id])

@router.get("/dag/tips")
async def get_tips(request: Request):
    state = request.app.state.node
    return {"tips": list(state.dag.tips), "count": len(state.dag.tips)}

@router.get("/dag/size")
async def get_dag_size(request: Request):
    state = request.app.state.node
    return {"size": len(state.dag.transactions)}

@router.get("/balance/{pubkey}")
async def get_balance_endpoint(request: Request, pubkey: str):
    state = request.app.state.node
    bal = get_balance(pubkey, state.balance_cache)
    return {"pubkey": pubkey, "balance": bal, "unit": "milli-token"}

@router.get("/dag/confirmed/{tx_id}")
async def get_confirmed_status(request: Request, tx_id: str):
    state = request.app.state.node
    if tx_id not in state.dag.transactions:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    confirmed = is_confirmed(state.dag, tx_id)
    child_count = len(state.dag.children.get(tx_id, set()))
    return {"tx_id": tx_id, "confirmed": confirmed, "child_count": child_count}

@router.get("/peers")
async def get_peers(request: Request):
    state = request.app.state.node
    peers = [{"node_id": p.node_id, "ip": p.ip, "port": p.port, "connected": p.connected} for p in state.peers]
    return {"peers": peers}

@router.get("/health")
async def health(request: Request):
    state = request.app.state.node
    return {
        "status": "ok", 
        "node_id": config.NODE_ID, 
        "dag_size": len(state.dag.transactions), 
        "tip_count": len(state.dag.tips)
    }
