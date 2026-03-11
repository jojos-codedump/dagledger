# DAG Ledger MVP

A minimalist, high-performance Directed Acyclic Graph (DAG) ledger designed to run on a cluster of Raspberry Pi Zero 2W nodes. Built over a single weekend to demonstrate distributed consensus and state synchronization on constrained edge devices.

## Architecture
- **Single Async Runtime:** FastAPI + `asyncio`. No threads, no locks, zero GIL contention.
- **In-Memory State:** Ephemeral graph and tip states constructed for extreme throughput capabilities.
- **Binary Determinism:** Employs `struct.pack` mapped directly to HMAC-SHA256 signatures ensuring network-wide absolute graph immutability. 
- **P2P Gossip Network:** Custom `msgpack` encoded framings routed over raw TCP streams for immediate topology convergences.
- **Cheapest-First Validation Pipelines:** Enforces strict local validation bounds checking including active pending outbound balances completely closing double-spend windows.

## Running Locally

1. Create a `virtualenv` and install requirements:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run tests to confirm local environment bindings:
```bash
pytest tests/
```

3. Launch a Node instance mapping your network ports:
```bash
export NODE_ID="node1"
export NODE_IP="192.168.1.101"
export P2P_PORT="9001"
export API_PORT="8000"
export SECRET_KEY="<your_secure_32_byte_hex_key>"

uvicorn main:app --host 0.0.0.0 --port $API_PORT
```

## Structure
- `api/` — FastAPI REST endpoints.
- `core/` — Domain models, DAG structures, incremental deterministic caching.
- `network/` — Asynchronous TCP framing and raw networking socket topologies.
- `tests/` — Pytest validation bounds guaranteeing hash accuracy and NTP skew offsets.
