import socket
import json
import threading
import time
import random
from datetime import datetime
from typing import Dict, List, Set

class GossipProtocol:
    def __init__(self, graph, port=8765, peer_timeout=30):
        self.graph = graph
        self.port = port
        self.peers: Dict[str, float] = {}
        self.running = True
        self.local_ip = self._get_local_ip()
        self.broadcast_ip = "255.255.255.255"
        self.multicast_group = "224.0.0.1"
        self.multicast_port = port + 1
        self.verbose = True
        self.auto_discovery = True
        self.ignored_ips = set()
        self._init_ignored_ips()
        
    def _init_ignored_ips(self):
        """Initialise la liste des IPs à ignorer."""
        # Réseaux virtuels courants
        ignored_prefixes = [
            "192.168.56.",   # VirtualBox
            "192.168.99.",   # Docker Toolbox
            "172.17.",       # Docker
            "172.18.",
            "172.19.",
            "10.0.2.",       # VirtualBox NAT
            "127.",          # Loopback
            "169.254.",      # APIPA
        ]
        # Ajoute les IPs virtuelles de l'utilisateur
        self.ignored_ips.update(ignored_prefixes)
    
    def _get_local_ip(self):
        """Récupère l'IP locale réelle (pas 127.0.0.1)."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172."):
                return ip
        except:
            pass
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            if not ip.startswith("127."):
                return ip
        except:
            pass
        return "127.0.0.1"
    
    def _is_ignored_ip(self, ip: str) -> bool:
        """Vérifie si une IP doit être ignorée."""
        for prefix in self.ignored_ips:
            if ip.startswith(prefix):
                return True
        return False
    
    def _send_message(self, target_ip, message_type, data=None, port=None):
        """Envoie un message UDP à un pair."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            msg = {
                "type": message_type,
                "sender": self.local_ip,
                "port": self.port,
                "data": data or {},
                "timestamp": datetime.now().isoformat()
            }
            target_port = port or self.port
            sock.sendto(json.dumps(msg).encode(), (target_ip, target_port))
            sock.close()
        except:
            pass
    
    def _broadcast(self, message_type, data=None):
        """Diffuse un message à tous les pairs connus et en broadcast."""
        for peer in list(self.peers.keys()):
            self._send_message(peer, message_type, data)
        self._send_message(self.broadcast_ip, message_type, data)
        self._send_message(self.multicast_group, message_type, data, self.multicast_port)
    
    def listen(self):
        """Écoute les messages UDP entrants."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            sock.bind(('', self.port))
            sock.settimeout(1.0)
            print(f"[Gossip] Listening at the harbour {self.port}")
        except:
            return
        
        mcast_sock = None
        try:
            mcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            mcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            mcast_sock.bind(('', self.multicast_port))
            mreq = socket.inet_aton(self.multicast_group) + socket.inet_aton('0.0.0.0')
            mcast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            mcast_sock.settimeout(1.0)
            print(f"[Gossip] Listening for multicast messages on {self.multicast_group}:{self.multicast_port}")
        except:
            mcast_sock = None
        
        while self.running:
            try:
                data, addr = sock.recvfrom(4096)
                msg = json.loads(data.decode())
                self._handle_message(msg, addr[0])
            except socket.timeout:
                pass
            except:
                pass
            
            if mcast_sock:
                try:
                    data, addr = mcast_sock.recvfrom(4096)
                    msg = json.loads(data.decode())
                    self._handle_message(msg, addr[0])
                except:
                    pass
        
        sock.close()
        if mcast_sock:
            mcast_sock.close()
    
    def _handle_message(self, msg, sender_ip):
        """Traite un message reçu."""
        if sender_ip == self.local_ip or self._is_ignored_ip(sender_ip):
            return
        
        msg_type = msg.get("type")
        
        if msg_type == "hello":
            if sender_ip not in self.peers and self.verbose:
                print(f"[Gossip] New peer: {sender_ip}")
            self.peers[sender_ip] = time.time()
            self._send_message(sender_ip, "hello_ack", {"node_count": len(self.graph.graph['nodes'])})
            
        elif msg_type == "hello_ack":
            if sender_ip not in self.peers and self.verbose:
                print(f"[Gossip] Confirmed peer: {sender_ip}")
            self.peers[sender_ip] = time.time()
            peer_nodes = msg.get("data", {}).get("node_count", 0)
            my_nodes = len(self.graph.graph['nodes'])
            if peer_nodes > my_nodes:
                self._send_message(sender_ip, "sync_request")
                
        elif msg_type == "sync_request":
            if self.verbose:
                print(f"[Gossip] Sync requested by {sender_ip}")
            self._send_message(sender_ip, "sync_response", {"graph": self.graph.graph})
            
        elif msg_type == "sync_response":
            if self.verbose:
                print(f"[Gossip] Sync received from {sender_ip}")
            remote_graph = msg.get("data", {}).get("graph")
            if remote_graph:
                self._merge_graph(remote_graph, sender_ip)
                
        elif msg_type == "update":
            if self.verbose:
                print(f"[Gossip] Update received from {sender_ip}")
            correction = msg.get("data", {})
            if correction:
                self._apply_correction(correction)
    
    def _merge_graph(self, remote_graph, source_ip):
        """Fusionne un graphe distant avec le graphe local."""
        nodes_before = len(self.graph.graph['nodes'])
        edges_before = len(self.graph.graph['edges'])
        
        existing_ids = {node['id'] for node in self.graph.graph['nodes']}
        for node in remote_graph['nodes']:
            if node['id'] not in existing_ids:
                self.graph.graph['nodes'].append(node)
                existing_ids.add(node['id'])
        
        existing_edges = {(edge['source'], edge['target']) for edge in self.graph.graph['edges']}
        for edge in remote_graph['edges']:
            key = (edge['source'], edge['target'])
            if key not in existing_edges:
                self.graph.graph['edges'].append(edge)
                existing_edges.add(key)
            else:
                for existing_edge in self.graph.graph['edges']:
                    if existing_edge['source'] == edge['source'] and existing_edge['target'] == edge['target']:
                        existing_edge['weight'] += edge['weight']
                        break
        
        self.graph._save()
        nodes_added = len(self.graph.graph['nodes']) - nodes_before
        edges_added = len(self.graph.graph['edges']) - edges_before
        
        if self.verbose:
            print(f"[Gossip] Merger: {nodes_added} knots, {edges_added} edges since {source_ip}")
    
    def _apply_correction(self, correction):
        """Applique une correction reçue d'un pair."""
        error_text = correction.get("error")
        solution_text = correction.get("solution")
        if error_text and solution_text:
            self.graph.add_correction(error_text, solution_text)
            if self.verbose:
                print(f"[Gossip] Correction applied: {error_text} → {solution_text}")
    
    def announce_presence(self):
        """Diffuse sa présence à tous les pairs."""
        self._broadcast("hello")
    
    def send_update(self, error_text, solution_text):
        """Diffuse une nouvelle correction à tous les pairs."""
        self._broadcast("update", {"error": error_text, "solution": solution_text})
    
    def add_peer_manual(self, ip_address: str) -> str:
        """Ajoute manuellement un pair connu."""
        if self._is_ignored_ip(ip_address):
            return f"⚠️ {ip_address} est une IP ignorée (réseau virtuel)."
        self.peers[ip_address] = time.time()
        self._send_message(ip_address, "hello")
        if self.verbose:
            print(f"[Gossip] Manual connection to {ip_address}")
        return f"✅ Peer {ip_address} added manually."
    
    def set_verbose(self, verbose: bool):
        """Active ou désactive les logs détaillés."""
        self.verbose = verbose
        print(f"Network logs: {'Enabled' if verbose else 'Disabled'}")
    
    def set_auto_discovery(self, enabled: bool):
        """Active ou désactive la découverte automatique."""
        self.auto_discovery = enabled
        print(f"Auto-discovery: {'Enabled' if enabled else 'Disabled'}")
    
    def start(self):
        """Démarre le protocole Gossip."""
        listener = threading.Thread(target=self.listen)
        listener.daemon = True
        listener.start()
        
        if self.auto_discovery:
            print("[Gossip] Auto-discovery enabled")
            while self.running:
                self.announce_presence()
                now = time.time()
                inactive = [ip for ip, last_seen in self.peers.items() if now - last_seen > 30]
                for ip in inactive:
                    del self.peers[ip]
                time.sleep(10)
        else:
            print("[Gossip] Manual mode: use 'add_peer_manual' to connect a peer")
    def stop(self):
        """Arrête le protocole."""
        self.running = False
        print("[Gossip] Stopped.")