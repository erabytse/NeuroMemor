from src.graph import KnowledgeGraph

def main():
    kg = KnowledgeGraph()
    print("=== NeuroMémor CLI v0.1 ===")
    print("A collaborative knowledge base for developers\n")
    
    while True:
        print("\n1. Add a correction")
        print("2. Search for a solution")
        print("3. Quit")
        choice = input("> ")
        
        if choice == "1":
            error = input("Error encountered : ")
            solution = input("Solution found : ")
            kg.add_correction(error, solution)
            print("✅ Correction added successfully.")
        
        elif choice == "2":
            query = input("Search for an error (keywords): ")
            results = kg.search_by_text(query)
            if results:
                print(f"\n🔍 {len(results)} result(s) found:")
                for i, r in enumerate(results, 1):
                    print(f"\n--- Result {i} ---")
                    print(f"🔴 Error : {r['error']}")
                    print(f"✅ Solution : {r['solution']} (weight: {r['weight']})")
            else:
                print("❌ No results were found for this search.")
        
        elif choice == "3":
            print("Thank you for using NeuroMémor. See you soon!")
            break
        
        else:
            print("Invalid choice. Enter 1, 2 or 3.")

if __name__ == "__main__":
    main()