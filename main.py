import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
import config
from genesis import GENESIS_TX
from core.dag import DAG
from network.gossip import handle_peer_connection, connect_to_peer
from api.routes import router

class NodeState:
    def __init__(self):
        self.dag = DAG()
        self.balance_cache: dict[str, int] = {}
        self.applied_tx_ids: set[str] = set()
        self.seen_ids: set[str] = set()
        self.peers = []
        self.node_id = config.NODE_ID

def load_genesis(state: NodeState):
    state.dag.add_transaction(GENESIS_TX)
    state.seen_ids.add(GENESIS_TX.tx_id)
    
    from core.balance import apply_transaction
    apply_transaction(GENESIS_TX, state.balance_cache)
    state.applied_tx_ids.add(GENESIS_TX.tx_id)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # === STARTUP ===
    state = NodeState()
    load_genesis(state)
    app.state.node = state

    server = await asyncio.start_server(
        lambda r, w: handle_peer_connection(r, w, state),
        host="0.0.0.0",
        port=config.P2P_PORT
    )

    peer_tasks = [
        asyncio.create_task(connect_to_peer(peer, state))
        for peer in config.PEERS
    ]

    yield

    # === SHUTDOWN ===
    server.close()
    await server.wait_closed()
    for task in peer_tasks:
        task.cancel()

app = FastAPI(lifespan=lifespan)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=config.API_PORT, reload=False)
