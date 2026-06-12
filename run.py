#run.py
from src.graph import KnowledgeGraph
from src.search import fuzzy_search

def main():
    kg = KnowledgeGraph()
    print("=== NeuroMémor v0.3 ===")
    print("A collaborative knowledge base for developers\n")

    while True:
        print("\n1. Add a correction")
        print("2. Search (fuzzy)")
        print("3. Vote for a solution")
        print("4. Export the graph")
        print("5. Import a graph")
        print("6. Quit")
        choice = input("> ")

        if choice == "1":
            error = input("Error : ")
            solution = input("Solution : ")
            kg.add_correction(error, solution)
            print("✅ Correction added.")

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
            error = input("Error you encountered : ")
            solution = input("A solution that worked : ")
            print(kg.vote_for_solution(error, solution))

        elif choice == "4":
            path = input("Export path (ex: export.json) : ")
            print(kg.export_to_file(path))

        elif choice == "5":
            path = input("Import path (ex: export.json) : ")
            print(kg.import_from_file(path))

        elif choice == "6":
            print("Thank you for using NeuroMémor. See you soon!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    main()