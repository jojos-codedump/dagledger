import asyncio
import logging
from typing import Any
from core.transaction import Transaction, from_dict, to_dict
from core.dag import topological_sort
from network.messages import encode_message, decode_message
import config

logger = logging.getLogger(__name__)

class PeerConnection:
    def __init__(self, node_id: str, ip: str, port: int):
        self.node_id = node_id
        self.ip = ip
        self.port = port
        self.writer: asyncio.StreamWriter | None = None
        self.connected = False

async def handle_peer_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, state: Any):
    peer_id = "unknown"
    try:
        # 1. Read HELLO
        hello_msg = await decode_message(reader)
        if hello_msg.get("type") != "HELLO" or hello_msg.get("version") != "1.0":
            return
        
        peer_id = hello_msg.get("node_id")
        
        # 2. Send our HELLO back
        await send_framed_message(writer, {"type": "HELLO", "version": "1.0", "node_id": config.NODE_ID})
        
        # 3. Loop forever
        while True:
            msg = await decode_message(reader)
            msg_type = msg.get("type")
            
            if msg_type == "NEW_TX":
                await validate_and_ingest(msg.get("tx"), state, exclude_node_id=peer_id)
            elif msg_type == "SYNC_REQ":
                known_ids = set(msg.get("known_ids", []))
                all_txs = list(state.dag.transactions.values())
                missing_txs = [to_dict(tx) for tx in all_txs if tx.tx_id not in known_ids]
                if missing_txs:
                    await send_framed_message(writer, {"type": "SYNC_RES", "txs": missing_txs})
            elif msg_type == "SYNC_RES":
                txs_data = msg.get("txs", [])
                txs = [from_dict(d) for d in txs_data]
                sorted_txs = topological_sort(txs)
                for tx in sorted_txs:
                    await validate_and_ingest(to_dict(tx), state, exclude_node_id=peer_id)
            elif msg_type == "PING":
                await send_framed_message(writer, {"type": "PONG", "sent_at": msg.get("sent_at")})
            elif msg_type == "PONG":
                pass
                
    except (asyncio.IncompleteReadError, ConnectionError, OSError):
        pass
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass

async def send_framed_message(writer: asyncio.StreamWriter, msg: dict):
    writer.write(encode_message(msg))
    await writer.drain()

async def validate_and_ingest(tx_dict: dict, state: Any, exclude_node_id: str):
    try:
        tx = from_dict(tx_dict)
    except Exception as e:
        logger.warning(f"Failed to decode tx: {e}")
        return

    from core.service import ingest_transaction
    await ingest_transaction(tx, state, exclude_node_id, config.SECRET_KEY)

async def connect_to_peer(peer_info: dict, state: Any):
    peer = PeerConnection(peer_info["id"], peer_info["ip"], peer_info["port"])
    state.peers.append(peer)
    
    while True:
        try:
            reader, writer = await asyncio.open_connection(peer.ip, peer.port)
            peer.writer = writer
            peer.connected = True
            
            await send_framed_message(writer, {"type": "HELLO", "version": "1.0", "node_id": config.NODE_ID})
            
            # Start sync (Anti-entropy catch-up)
            all_ids = state.dag.get_all_ids()
            await send_framed_message(writer, {"type": "SYNC_REQ", "known_ids": all_ids})
            
            while True:
                msg = await decode_message(reader)
                msg_type = msg.get("type")
                
                if msg_type == "SYNC_RES":
                    txs_data = msg.get("txs", [])
                    txs = [from_dict(d) for d in txs_data]
                    sorted_txs = topological_sort(txs)
                    for tx in sorted_txs:
                        await validate_and_ingest(to_dict(tx), state, exclude_node_id=peer.node_id)
                elif msg_type == "NEW_TX":
                    await validate_and_ingest(msg.get("tx"), state, exclude_node_id=peer.node_id)
                elif msg_type == "PING":
                    await send_framed_message(writer, {"type": "PONG", "sent_at": msg.get("sent_at")})
                        
        except (asyncio.IncompleteReadError, ConnectionError, OSError):
            peer.connected = False
            peer.writer = None
            await asyncio.sleep(config.PEER_CONNECT_RETRY_SECONDS)

async def broadcast(msg: dict, exclude_node_id: str, state: Any):
    for peer in state.peers:
        if peer.node_id == exclude_node_id or not peer.connected or not peer.writer:
            continue
            
        try:
            await send_framed_message(peer.writer, msg)
        except (ConnectionError, OSError):
            peer.connected = False
            peer.writer = None
