#run.py
import time

from src.graph import KnowledgeGraph
from src.search import fuzzy_search
from src.network import GossipProtocol
import threading



def main():
    kg = KnowledgeGraph()
    network = GossipProtocol(kg)
    VERBOSE = False
    
    # Démarrer le protocole Gossip dans un thread
    network_thread = threading.Thread(target=network.start)
    network_thread.daemon = True
    network_thread.start()  # Démarrage sans auto-discovery pour éviter les logs initiaux
    
    print("=== NeuroMémor v0.5 - Peer-to-Peer ===")
    print("A collaborative knowledge base for developers")
    print(f"Local IP: {network.local_ip}, Port: {network.port}")
    print("Peers will be automatically discovered on the local network.\n")
    print("Note: Corrections added will be shared with connected peers in real-time.\n")
    print("Please wait a moment for peer discovery to complete before adding corrections or searching.\n")
    print("=== Menu ===")

    if not network.peers:
        print("No peers detected yet. Please wait while we discover other instances on the network...")
    else:        print(f"Connected peers: {', '.join(network.peers.keys())}")
    
    while True: 
        
        print("\n1. Add a correction")
        print("2. Search (fuzzy)")
        print("3. Vote for a solution")
        print("4. Export the graph")
        print("5. Import a graph")
        print("\n6. Add a peer manually")
        print("7. Scan a range of IP addresses for peers")
        print("8. Show connected peers")
        print("9. Enable/disable network logs")
        print("10. Quit")
        choice = input("> ")
        
        if choice == "1":
            error = input("Error : ")
            solution = input("Solution : ")
            kg.add_correction(error, solution)
            # Diffuser la nouvelle correction aux pairs
            network.send_update(error, solution)
            print("✅ Correction added and broadcast to peers.")
            
        elif choice == "2":
            query = input("Search : ")
            results = fuzzy_search(kg.graph, query)
            if results:
                for r in results:
                    print(f"\n🔴 Error : {r['error']}")
                    print(f"✅ Solution : {r['solution']} (weight: {r['weight']}, similarity: {r['similarity']})")
            else:
                print("❌ No results found.")
                
        elif choice == "3":
            error = input("Error that you encountered : ")
            solution = input("Solution that worked : ")
            print(kg.vote_for_solution(error, solution))
            
        elif choice == "4":
            path = input("Export path (e.g., export.json) : ")
            print(kg.export_to_file(path))
            
        elif choice == "5":
            path = input("Import path (e.g., export.json) : ")
            print(kg.import_from_file(path))
            
        elif choice == "6":
            ip = input("IP du pair (ex: 192.168.1.10) : ")
            print(network.add_peer_manual(ip))
            
        elif choice == "7":
            start = input("IP de début (ex: 192.168.1.1) : ")
            end = input("IP de fin (ex: 192.168.1.254) : ")
            print(network.discover_peers_manual(start, end))
            
        elif choice == "8":
            print(f"\nConnected peers ({len(network.peers)}):")
            for ip, last_seen in network.peers.items():
                print(f"  • {ip} (seen {int(time.time() - last_seen)}s ago)")

        elif choice == "9":
            VERBOSE = not VERBOSE
            network.set_verbose(VERBOSE)
            print(f"Network logs: {'Enabled' if VERBOSE else 'Disabled'}")
                
        elif choice == "10":
            print("Stopping the protocol...")
            network.stop()
            print("Thank you for using NeuroMémor. See you soon!")
            break
            
        else:
            print("Invalid choice. Please enter a number between 1 and 10.")

if __name__ == "__main__":
    main()