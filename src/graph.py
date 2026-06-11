# graph.py
import json
import os
from pathlib import Path
from datetime import datetime

class KnowledgeGraph:
    def __init__(self, data_path="data/corrections.json"):
        self.data_path = Path(data_path)
        self.data_path.parent.mkdir(exist_ok=True)
        self.graph = self._load()
    
    def _load(self):
        # Si le fichier n'existe pas, initialise un graphe vide
        if not self.data_path.exists():
            return {"nodes": [], "edges": []}
        
        # Si le fichier existe, essaie de le lire
        try:
            with open(self.data_path, 'r') as f:
                content = f.read().strip()
                if not content:  # Fichier vide
                    return {"nodes": [], "edges": []}
                return json.loads(content)
        except json.JSONDecodeError:
            # Si le fichier est corrompu, on le réinitialise
            return {"nodes": [], "edges": []}
    
    def _save(self):
        self.data_path.parent.mkdir(exist_ok=True)
        with open(self.data_path, 'w') as f:
            json.dump(self.graph, f, indent=2)
    
    def add_correction(self, error_text, solution_text, user_id="anonymous"):
        # Crée un nœud pour l'erreur
        error_id = f"error_{len(self.graph['nodes'])}"
        self.graph['nodes'].append({
            "id": error_id,
            "type": "error",
            "text": error_text,
            "user": user_id,
            "timestamp": datetime.now().isoformat()
        })
        # Crée un nœud pour la solution
        solution_id = f"solution_{len(self.graph['nodes'])}"
        self.graph['nodes'].append({
            "id": solution_id,
            "type": "solution",
            "text": solution_text,
            "user": user_id,
            "timestamp": datetime.now().isoformat()
        })
        # Crée un lien entre l'erreur et la solution
        self.graph['edges'].append({
            "source": error_id,
            "target": solution_id,
            "weight": 1,
            "type": "solves"
        })
        self._save()
        return error_id, solution_id

    def search_by_text(self, query_text):
        # Simple recherche par mot-clé
        results = []
        for node in self.graph['nodes']:
            if node['type'] == 'error' and query_text.lower() in node['text'].lower():
                # Trouve les solutions liées à cette erreur
                for edge in self.graph['edges']:
                    if edge['source'] == node['id']:
                        for sol_node in self.graph['nodes']:
                            if sol_node['id'] == edge['target']:
                                results.append({
                                    "error": node['text'],
                                    "solution": sol_node['text'],
                                    "weight": edge['weight']
                                })
        return results