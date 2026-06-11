from src.graph import KnowledgeGraph

def main():
    kg = KnowledgeGraph()
    print("=== NeuroMémor CLI v0.1 ===")
    print("Mémoire collective associative pour développeurs\n")
    
    while True:
        print("\n1. Ajouter une correction")
        print("2. Rechercher une solution")
        print("3. Quitter")
        choice = input("> ")
        
        if choice == "1":
            error = input("Erreur rencontrée : ")
            solution = input("Solution trouvée : ")
            kg.add_correction(error, solution)
            print("✅ Correction ajoutée avec succès.")
        
        elif choice == "2":
            query = input("Rechercher une erreur (mots-clés) : ")
            results = kg.search_by_text(query)
            if results:
                print(f"\n🔍 {len(results)} résultat(s) trouvé(s) :")
                for i, r in enumerate(results, 1):
                    print(f"\n--- Résultat {i} ---")
                    print(f"🔴 Erreur : {r['error']}")
                    print(f"✅ Solution : {r['solution']} (poids: {r['weight']})")
            else:
                print("❌ Aucune correction trouvée pour cette recherche.")
        
        elif choice == "3":
            print("Merci d'avoir utilisé NeuroMémor. À bientôt !")
            break
        
        else:
            print("Choix invalide. Entrez 1, 2 ou 3.")

if __name__ == "__main__":
    main()