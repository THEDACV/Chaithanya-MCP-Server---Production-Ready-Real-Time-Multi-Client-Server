#!/usr/bin/env python3
"""
Chaithanya MCP Server - Production Ready Real-Time Multi-Client Server
Enhanced for deployment with security, performance, and monitoring features.
"""

import socket
import threading
import time
import datetime
import logging
import sys
import json
import hashlib
import secrets
import select
from typing import Dict, List, Set, Tuple, Optional
import argparse

# Configure advanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('chaithanya_server.log', encoding='utf-8')
    ]
)
logger = logging.getLogger("ChaithanyaMCPServer")

class ChaithanyaMCPServer:
    def __init__(self, host: str = '0.0.0.0', port: int = 9999, max_clients: int = 100):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.server_socket = None
        self.running = False
        self.clients: Dict[socket.socket, Dict] = {}  # socket -> client info
        self.client_lock = threading.Lock()
        self.connections_count = 0
        self.start_time = time.time()
        
        # Security features
        self.auth_tokens: Set[str] = set()
        self.rate_limits: Dict[str, Tuple[int, float]] = {}  # ip -> (request_count, window_start)
        self.rate_limit_lock = threading.Lock()
        
        # Performance monitoring
        self.stats = {
            'connections': 0,
            'disconnections': 0,
            'messages_received': 0,
            'messages_sent': 0,
            'broadcasts_sent': 0,
            'errors': 0
        }
        self.stats_lock = threading.Lock()
        
        # Load or generate auth tokens
        self._load_auth_tokens()
        
    def _load_auth_tokens(self):
        """Load or generate authentication tokens"""
        try:
            # In production, load from secure storage
            # For demo purposes, we'll generate some tokens
            self.auth_tokens.add(hashlib.sha256("chaithanya2024".encode()).hexdigest())
            self.auth_tokens.add(hashlib.sha256("mcpsecure123".encode()).hexdigest())
            logger.info("Authentication tokens loaded")
        except Exception as e:
            logger.error(f"Error loading auth tokens: {e}")
    
    def _check_rate_limit(self, ip_address: str) -> bool:
        """Implement rate limiting (100 requests per minute per IP)"""
        with self.rate_limit_lock:
            current_time = time.time()
            if ip_address not in self.rate_limits:
                self.rate_limits[ip_address] = (1, current_time)
                return True
            
            count, window_start = self.rate_limits[ip_address]
            
            # Reset counter if window has passed
            if current_time - window_start > 60:  # 1 minute window
                self.rate_limits[ip_address] = (1, current_time)
                return True
            
            # Check if limit exceeded
            if count >= 100:  # 100 requests per minute
                return False
            
            # Increment counter
            self.rate_limits[ip_address] = (count + 1, window_start)
            return True
    
    def _cleanup_rate_limits(self):
        """Periodically clean up old rate limit entries"""
        while self.running:
            time.sleep(300)  # Clean up every 5 minutes
            try:
                with self.rate_limit_lock:
                    current_time = time.time()
                    to_remove = []
                    for ip, (count, window_start) in self.rate_limits.items():
                        if current_time - window_start > 300:  # Remove entries older than 5 minutes
                            to_remove.append(ip)
                    
                    for ip in to_remove:
                        del self.rate_limits[ip]
            except Exception as e:
                logger.error(f"Error cleaning rate limits: {e}")
    
    def start_server(self):
        """Start the server and begin listening for connections"""
        try:
            # Create server socket with better configuration
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_clients)
            self.server_socket.settimeout(1.0)  # Allow for periodic checking of running flag
            self.running = True
            
            # Start rate limit cleanup thread
            cleanup_thread = threading.Thread(target=self._cleanup_rate_limits, daemon=True)
            cleanup_thread.start()
            
            # Start stats logging thread
            stats_thread = threading.Thread(target=self._log_stats, daemon=True)
            stats_thread.start()
            
            logger.info(f"Chaithanya MCP Server started on {self.host}:{self.port}")
            logger.info(f"Maximum clients: {self.max_clients}")
            print(f"Chaithanya MCP Server running on {self.host}:{self.port}")
            print("Press Ctrl+C to stop the server")
            
            # Start accepting connections
            self.accept_connections()
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            print(f"Error: {e}")
        finally:
            self.stop_server()
    
    def _log_stats(self):
        """Periodically log server statistics"""
        while self.running:
            time.sleep(60)  # Log every minute
            try:
                with self.stats_lock:
                    uptime = time.time() - self.start_time
                    logger.info(
                        f"Stats - Uptime: {uptime:.0f}s, "
                        f"Connections: {self.stats['connections']}, "
                        f"Active: {len(self.clients)}, "
                        f"Messages: {self.stats['messages_received']} received, "
                        f"{self.stats['messages_sent']} sent"
                    )
            except Exception as e:
                logger.error(f"Error logging stats: {e}")
    
    def accept_connections(self):
        """Accept incoming client connections with improved error handling"""
        while self.running:
            try:
                # Use select to check for incoming connections with timeout
                read_sockets, _, _ = select.select([self.server_socket], [], [], 1.0)
                
                if self.server_socket in read_sockets:
                    client_socket, client_address = self.server_socket.accept()
                    client_ip = client_address[0]
                    
                    # Check connection limit
                    with self.client_lock:
                        if len(self.clients) >= self.max_clients:
                            client_socket.send("Server is at maximum capacity. Please try again later.\n".encode('utf-8'))
                            client_socket.close()
                            logger.warning(f"Rejected connection from {client_ip}: server full")
                            continue
                    
                    # Check rate limit for new connections from this IP
                    if not self._check_rate_limit(client_ip):
                        client_socket.send("Too many connections from your IP. Please try again later.\n".encode('utf-8'))
                        client_socket.close()
                        logger.warning(f"Rate limited connection from {client_ip}")
                        continue
                    
                    logger.info(f"New connection from {client_address}")
                    
                    # Start a new thread to handle the client
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    
            except socket.timeout:
                continue  # Expected timeout, continue running check
            except OSError as e:
                if self.running:
                    logger.error(f"Error accepting connection: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
    
    def handle_client(self, client_socket: socket.socket, client_address: tuple):
        """Handle communication with a connected client"""
        client_ip = client_address[0]
        client_id = f"{client_ip}:{client_address[1]}"
        username = f"Client-{client_address[1]}"
        
        try:
            # Set socket timeout for recv operations
            client_socket.settimeout(1.0)
            
            # Send welcome message
            welcome_msg = f"Welcome to Chaithanya MCP Server! Your username is {username}\n" \
                          "Available commands:\n" \
                          "- time: Get server time\n" \
                          "- clients: List connected users\n" \
                          "- broadcast <msg>: Send message to all users\n" \
                          "- stats: Get server statistics\n" \
                          "- exit: Disconnect from server\n"
            client_socket.send(welcome_msg.encode('utf-8'))
            
            # Add client to connected clients list
            with self.client_lock:
                self.clients[client_socket] = {
                    'username': username,
                    'ip': client_ip,
                    'connected_at': time.time(),
                    'messages_sent': 0,
                    'messages_received': 0
                }
            
            # Update stats
            with self.stats_lock:
                self.stats['connections'] += 1
                self.connections_count += 1
            
            self.broadcast_message(f"{username} has joined the server", exclude=client_socket)
            
            # Main client communication loop
            while self.running:
                try:
                    # Use select to check if data is available
                    read_sockets, _, _ = select.select([client_socket], [], [], 1.0)
                    
                    if client_socket in read_sockets:
                        data = client_socket.recv(1024).decode('utf-8').strip()
                        if not data:
                            break  # Client disconnected
                        
                        # Update client and server stats
                        with self.client_lock:
                            if client_socket in self.clients:
                                self.clients[client_socket]['messages_received'] += 1
                        
                        with self.stats_lock:
                            self.stats['messages_received'] += 1
                        
                        logger.info(f"Received from {username}: {data}")
                        
                        # Check rate limiting for this client
                        if not self._check_rate_limit(client_ip):
                            client_socket.send("Rate limit exceeded. Please wait before sending more commands.\n".encode('utf-8'))
                            continue
                        
                        # Process commands
                        response = self.process_command(data, client_socket)
                        if response:
                            client_socket.send(response.encode('utf-8'))
                            
                            # Update stats
                            with self.client_lock:
                                if client_socket in self.clients:
                                    self.clients[client_socket]['messages_sent'] += 1
                            
                            with self.stats_lock:
                                self.stats['messages_sent'] += 1
                
                except socket.timeout:
                    continue  # Expected timeout, continue running check
                except ConnectionResetError:
                    break
                except Exception as e:
                    logger.error(f"Error handling client {username}: {e}")
                    with self.stats_lock:
                        self.stats['errors'] += 1
                    try:
                        client_socket.send(f"Error: {e}\n".encode('utf-8'))
                    except:
                        break  # Client likely disconnected
                    
        except Exception as e:
            logger.error(f"Error with client {username}: {e}")
            with self.stats_lock:
                self.stats['errors'] += 1
        finally:
            # Clean up client connection
            self.remove_client(client_socket, username)
    
    def process_command(self, command: str, client_socket: socket.socket) -> str:
        """Process client commands and return appropriate response"""
        parts = command.split(' ', 1)
        cmd = parts[0].lower()
        
        if cmd == 'time':
            return f"Server time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        elif cmd == 'clients':
            with self.client_lock:
                client_list = []
                for client_info in self.clients.values():
                    client_list.append(f"{client_info['username']} ({client_info['ip']})")
                clients_str = "\n".join(client_list) if client_list else "No clients connected"
            return f"Connected clients ({len(client_list)}):\n{clients_str}\n"
        
        elif cmd == 'broadcast':
            if len(parts) > 1:
                message = parts[1]
                username = self.clients.get(client_socket, {}).get('username', 'Unknown')
                self.broadcast_message(f"[BROADCAST] {username}: {message}", exclude=client_socket)
                
                with self.stats_lock:
                    self.stats['broadcasts_sent'] += 1
                    
                return "Message broadcasted\n"
            else:
                return "Usage: broadcast <message>\n"
        
        elif cmd == 'stats':
            with self.stats_lock:
                uptime = time.time() - self.start_time
                hours, remainder = divmod(uptime, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                return (
                    f"Server Statistics:\n"
                    f"- Uptime: {int(hours)}h {int(minutes)}m {int(seconds)}s\n"
                    f"- Total connections: {self.stats['connections']}\n"
                    f"- Active clients: {len(self.clients)}\n"
                    f"- Messages received: {self.stats['messages_received']}\n"
                    f"- Messages sent: {self.stats['messages_sent']}\n"
                    f"- Broadcasts sent: {self.stats['broadcasts_sent']}\n"
                )
        
        elif cmd == 'exit':
            return "Goodbye!\n"
        
        else:
            return f"Unknown command: {cmd}. Available commands: time, clients, broadcast, stats, exit\n"
    
    def broadcast_message(self, message: str, exclude: socket.socket = None):
        """Send a message to all connected clients except the excluded one"""
        with self.client_lock:
            disconnected_clients = []
            for client_socket in self.clients.keys():
                if client_socket != exclude:
                    try:
                        client_socket.send(f"{message}\n".encode('utf-8'))
                    except (ConnectionError, OSError):
                        disconnected_clients.append(client_socket)
            
            # Remove any disconnected clients
            for client in disconnected_clients:
                username = self.clients.get(client, {}).get('username', 'Unknown')
                self.remove_client(client, username)
    
    def remove_client(self, client_socket: socket.socket, username: str):
        """Remove a client from the connected clients list"""
        try:
            with self.client_lock:
                if client_socket in self.clients:
                    del self.clients[client_socket]
            
            client_socket.close()
            logger.info(f"Client {username} disconnected")
            
            with self.stats_lock:
                self.stats['disconnections'] += 1
                
            self.broadcast_message(f"{username} has left the server")
        except Exception as e:
            logger.error(f"Error removing client {username}: {e}")
            with self.stats_lock:
                self.stats['errors'] += 1
    
    def stop_server(self):
        """Stop the server and clean up resources"""
        self.running = False
        
        # Close all client connections
        with self.client_lock:
            for client_socket in list(self.clients.keys()):
                try:
                    client_socket.send("Server is shutting down. Goodbye!\n".encode('utf-8'))
                    client_socket.close()
                except:
                    pass
            self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        logger.info("Chaithanya MCP Server stopped")
        print("Server stopped")

def main():
    """Main function to run the server with command line arguments"""
    parser = argparse.ArgumentParser(description="Chaithanya MCP Server - Real-Time Multi-Client Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host IP to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=9999, help="Port to listen on (default: 9999)")
    parser.add_argument("--max-clients", type=int, default=100, help="Maximum number of concurrent clients (default: 100)")
    
    args = parser.parse_args()
    
    server = ChaithanyaMCPServer(host=args.host, port=args.port, max_clients=args.max_clients)
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop_server()
    except Exception as e:
        print(f"Server error: {e}")
        server.stop_server()

if __name__ == "__main__":
    main()