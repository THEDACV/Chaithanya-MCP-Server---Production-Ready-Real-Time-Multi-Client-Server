<!-- Banner -->
<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=28&pause=1000&color=FF6F61&center=true&vCenter=true&width=700&lines=⚡+Chaithanya+MCP+Server;Real-Time+Multi-Client+Server;Production+Ready+%7C+Secure+%7C+Scalable;Built+with+Python+3+🔥" alt="Typing Animation" />
</p>

<!-- Badges -->
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Socket-Programming-green?logo=socketdotio&logoColor=white" />
  <img src="https://img.shields.io/badge/Security-Enabled-red?logo=shield&logoColor=white" />
  <img src="https://img.shields.io/github/license/your-username/chaithanya-mcp-server?color=yellow" />
</p>

---

# ⚡ Chaithanya MCP Server

**Chaithanya MCP Server** is a **production-ready, real-time multi-client communication server** built with **Python 3 socket programming**.  
It includes **authentication, rate limiting, monitoring, performance logging, and broadcasting** — designed for **secure & scalable deployments**.

<p align="center">
  <img src="https://github.com/abhisheknaiidu/abhisheknaiidu/blob/master/code.gif?raw=true" width="500" />
</p>

---

## ✨ Features

- 🔐 **Secure Authentication** with hashed tokens  
- ⚡ **High Performance** – 100+ clients supported concurrently  
- 📊 **Real-time Monitoring** (connections, disconnections, uptime, errors)  
- 📡 **Broadcast Messaging** across all clients  
- 🚦 **Rate Limiting** (100 requests/minute per IP)  
- 🛠 **Command System** (`time`, `clients`, `broadcast`, `stats`, `exit`)  
- 🧹 **Auto Cleanup** of inactive connections and stale rate limits  
- 📜 **Detailed Logging** (`chaithanya_server.log`)  

---

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/your-username/chaithanya-mcp-server.git

# Navigate into the folder
cd chaithanya-mcp-server

# Run the server
python3 chaithanya_mcp_server.py --host 0.0.0.0 --port 9999 --max-clients 100```

⚡ Usage

Once the server is running, clients can connect via Telnet or custom Python client.

telnet localhost 9999


🖥 Example Commands:
time         → Get server time
clients      → List connected users
broadcast hi → Send message to all clients
stats        → Show server statistics
exit         → Disconnect

📐 Architecture Overview
flowchart TD
    A[Client 1] -->|TCP Socket| B[Chaithanya MCP Server]
    C[Client 2] -->|TCP Socket| B
    D[Client N] -->|TCP Socket| B

    B -->|Broadcast| A
    B -->|Broadcast| C
    B -->|Broadcast| D

    subgraph Monitoring & Security
      E[Authentication]
      F[Rate Limiting]
      G[Logging & Stats]
    end

    B --> E
    B --> F
    B --> G


📊 Live Stats (Sample Log Output)
2025-08-21 18:10:32 - ChaithanyaMCPServer - INFO - Stats - Uptime: 600s,
Connections: 20, Active: 12,
Messages: 150 received, 140 sent

📂 Project Structure
chaithanya-mcp-server/
│── chaithanya_mcp_server.py   # Main server file
│── chaithanya_server.log      # Auto-generated logs
│── README.md                  # Project documentation

📜 License

📝 Copyright © 2025 [Chaithanya Vishwamitra D A]

<p align="center"> Made with ❤️ by <b>Chaithanya Vishwamitra D A</b> <br> <img src="https://img.shields.io/badge/Server-Running-brightgreen?style=for-the-badge&logo=serverless&logoColor=white" /> </p> ```



