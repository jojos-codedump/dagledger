import os

NODE_ID   = os.getenv("NODE_ID",   "node1")
NODE_IP   = os.getenv("NODE_IP",   "192.168.1.101")
P2P_PORT  = int(os.getenv("P2P_PORT", "9001"))
API_PORT  = int(os.getenv("API_PORT", "8000"))
SECRET_KEY = os.getenv("SECRET_KEY", "00" * 32)

ALL_NODES = [
    {"id": "node1", "ip": "dagnode1.local", "port": 9001},
    {"id": "node2", "ip": "dagnode2.local", "port": 9001},
    {"id": "node3", "ip": "dagnode3.local", "port": 9001},
    {"id": "node4", "ip": "dagnode4.local", "port": 9001},
]

PEERS = [n for n in ALL_NODES if n["id"] != NODE_ID]

PEER_CONNECT_RETRY_SECONDS  = 5
PING_INTERVAL_SECONDS       = 10
SYNC_INTERVAL_SECONDS       = 30

CONFIRMATION_THRESHOLD      = 2
TIP_MAX_AGE_MS              = 60_000
