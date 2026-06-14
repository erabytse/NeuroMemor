import threading  
import time
from src.graph import KnowledgeGraph
from src.search import fuzzy_search
from src.network import GossipProtocol
from src.api import start_api  

# Variable globale pour les logs
VERBOSE_GLOBAL = True  

def main():
    global VERBOSE_GLOBAL  
    
    kg = KnowledgeGraph()
    network = GossipProtocol(kg)
    
    # Appliquer le niveau de verbose initial
    network.set_verbose(VERBOSE_GLOBAL)
    
    # Démarrer le protocole Gossip dans un thread
    network_thread = threading.Thread(target=network.start)
    network_thread.daemon = True
    network_thread.start()
    
    # Démarrer l'API avec les instances de graphe et réseau
    api_thread = threading.Thread(target=start_api, args=(kg, network))
    api_thread.daemon = True
    api_thread.start()
    
    print("=== NeuroMémor v0.6 ===")
    print("A collaborative knowledge base for developers")
    print("🌐 REST API available at http://localhost:8000")
    print("🌐 Web interface available at http://localhost:8000 (opens the web/index.html file)\n")
    print(f"Local IP: {network.local_ip}, Port: {network.port}")
    print(f"🔊 Network logs: {'Enabled' if VERBOSE_GLOBAL else 'Disabled'}\n")
    print("Peers will be automatically discovered on the local network.\n")
    print("Note: Corrections added will be shared with connected peers in real-time.\n")
    print("Please wait a moment for peer discovery to complete before adding corrections or searching.\n")
    print("=== Menu ===")


    while True:

        print("\n1. Add a correction")
        print("2. Search (fuzzy)")
        print("3. Vote for a solution")
        print("4. Export the graph")
        print("5. Import a graph")
        print("6. Add a peer manually")
        print("7. Show connected peers")
        print("8. Enable/disable network logs")
        print("9. Quit")
        choice = input("> ")
        
        if choice == "1":
            error = input("Error : ")
            solution = input("Solution : ")
            kg.add_correction(error, solution)
            # Diffuser la correction aux pairs
            network.send_update(error, solution)
            print("✅ Correction added and broadcast to peers.")
            
        elif choice == "2":
            query = input("Search : ")
            results = fuzzy_search(kg.graph, query)
            if results:
                for i, r in enumerate(results, 1):
                    print(f"\n--- Result {i} ---")
                    print(f"🔴 Error : {r['error']}")
                    print(f"✅ Solution : {r['solution']} (weight: {r['weight']}, similarity: {r['similarity']})")
            else:
                print("❌ No solution found.")
                
        elif choice == "3":
            error = input("Error you encountered : ")
            solution = input("Solution that worked : ")
            print(kg.vote_for_solution(error, solution))
            
        elif choice == "4":
            path = input("Export path (e.g., export.json) : ")
            print(kg.export_to_file(path))
            
        elif choice == "5":
            path = input("Import path (e.g., export.json) : ")
            print(kg.import_from_file(path))
            
        elif choice == "6":
            ip = input("IP of the peer (e.g., 192.168.0.9) : ")
            print(network.add_peer_manual(ip))
            
        elif choice == "7":
            print(f"\nConnected peers ({len(network.peers)}):")
            for ip, last_seen in network.peers.items():
                print(f"  • {ip} (seen {int(time.time() - last_seen)}s ago)")
                
        elif choice == "8":
            VERBOSE_GLOBAL = not VERBOSE_GLOBAL
            network.set_verbose(VERBOSE_GLOBAL)
            print(f"🔊 Network logs: {'Enabled' if VERBOSE_GLOBAL else 'Disabled'}")
            
        elif choice == "9":
            print("Stopping the protocol...")
            network.stop()
            print("Thank you for using NeuroMémor. See you soon!")
            break
            
        else:
            print("Invalid choice. Please enter a number between 1 and 10.")

if __name__ == "__main__":
    main()