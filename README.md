# DAG Ledger (Minimum Viable Product)

Welcome to the **DAG Ledger**! This project is a super-fast, lightweight digital ledger (like a blockchain, but without the slow blocks). It is specifically designed to run on a cluster of tiny, low-power computers: **Raspberry Pi Zero 2Ws**. 

Instead of organizing transactions into a single straight line (a chain), this ledger organizes them into a web-like structure called a **Directed Acyclic Graph (DAG)**. This means multiple transactions can happen at the exact same time without waiting in line, making the network much faster.

---

## 🧠 How It Works (In Layman's Terms)

1. **No Central Server:** There is no "boss" computer. All 4 Raspberry Pis (nodes) talk to each other directly as equals.
2. **Gossip Protocol:** When one Pi receives a new transaction, it "gossips" or whispers it to the other Pis over the network. 
3. **In-Memory Speed:** To make it lightning fast on 1GHz processors, it doesn't use a heavy database. It keeps the entire web of transactions in its RAM. (Note: Because it's an MVP, if you turn off a Pi, it forgets its state, but it will sync back up when it turns on and connects to the others!)
4. **Un-fakable Math:** Every transaction is locked down with strict cryptography (HMAC-SHA256). No one can alter a transaction amount or pretend to be someone else without the network instantly rejecting it.

---

## 🛠️ Step-by-Step Raspberry Pi Deployment Guide

You have 4 Raspberry Pis with the hostnames `dagnode1`, `dagnode2`, `dagnode3`, and `dagnode4`. The default user on them is `pi`. 

Here is exactly how to get your network running from zero to Hero.

### Step 1: Connect to your Pis
Open a fresh terminal on your main computer (Windows/Mac/Linux) for **each** of your four Raspberry Pis. You will want 4 windows open side-by-side.

SSH into them using their `.local` addresses (this works automatically on most home Wi-Fi networks):
```bash
# Terminal 1
ssh pi@dagnode1.local
# Terminal 2
ssh pi@dagnode2.local
# Terminal 3
ssh pi@dagnode3.local
# Terminal 4
ssh pi@dagnode4.local
```
*(If your router doesn't support `.local` mDNS, you will need to find out their exact IP addresses from your router settings and SSH into those instead).*

### Step 2: Download the Code
Run this command on **ALL FOUR** Raspberry Pis to download this repository:

```bash
git clone https://github.com/jojos-codedump/dagledger.git
cd dagledger
```

### Step 3: Install the Requirements
Python needs a dedicated "virtual environment" so we don't mess up the Pi's system files. Run these commands on **ALL FOUR** Pis:

```bash
# Create the virtual environment
python3 -m venv venv

# Activate it (you'll see '(venv)' appear in your terminal)
source venv/bin/activate

# Install the necessary libraries (FastAPI, Uvicorn, etc.)
pip install -r requirements.txt
```

### Step 4: The Secret Key
For the network to trust itself, all nodes need to share a massive 64-character secret password (32 bytes in hex). **You must use the exact same secret key on all 4 Pis.** Let's use this one for the demo:

`1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef`

### Step 5: Create Startup Scripts for Each Node
To make launching easy, we are going to create a quick startup script on each Pi.

**On Node 1 (`dagnode1`):**
Run this to create a file called `start.sh`:
```bash
cat << 'EOF' > start.sh
#!/bin/bash
source venv/bin/activate
export NODE_ID="node1"
export NODE_IP="dagnode1.local"
export P2P_PORT="9001"
export API_PORT="8000"
export SECRET_KEY="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
uvicorn main:app --host 0.0.0.0 --port $API_PORT
EOF
chmod +x start.sh
```

**On Node 2 (`dagnode2`):**
```bash
cat << 'EOF' > start.sh
#!/bin/bash
source venv/bin/activate
export NODE_ID="node2"
export NODE_IP="dagnode2.local"
export P2P_PORT="9001"
export API_PORT="8000"
export SECRET_KEY="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
uvicorn main:app --host 0.0.0.0 --port $API_PORT
EOF
chmod +x start.sh
```

**On Node 3 (`dagnode3`):**
```bash
cat << 'EOF' > start.sh
#!/bin/bash
source venv/bin/activate
export NODE_ID="node3"
export NODE_IP="dagnode3.local"
export P2P_PORT="9001"
export API_PORT="8000"
export SECRET_KEY="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
uvicorn main:app --host 0.0.0.0 --port $API_PORT
EOF
chmod +x start.sh
```

**On Node 4 (`dagnode4`):**
```bash
cat << 'EOF' > start.sh
#!/bin/bash
source venv/bin/activate
export NODE_ID="node4"
export NODE_IP="dagnode4.local"
export P2P_PORT="9001"
export API_PORT="8000"
export SECRET_KEY="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
uvicorn main:app --host 0.0.0.0 --port $API_PORT
EOF
chmod +x start.sh
```

### Step 6: Launch the Network! 🚀
You're ready. In your four terminal windows, run the script you just created:

```bash
./start.sh
```

You will see `uvicorn` boot up. Behind the scenes, the nodes will immediately reach out to each other over port 9001, say "HELLO", and form a mesh network.

### Step 7: Testing it Out
Open a 5th terminal window on your main computer, or just use a browser. Let's see if Node 1 is healthy and sees its peers.

Run this:
```bash
curl http://dagnode1.local:8000/health
```
You should see it responding with "status": "ok" and showing the size of its DAG!

Check its peers:
```bash
curl http://dagnode1.local:8000/peers
```
It will list node2, node3, and node4 as `connected: true`. 

**Congratulations! Your 4-node Raspberry Pi Edge DAG is officially alive.**
