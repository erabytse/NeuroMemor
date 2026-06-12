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
    
    def vote_solution(self, error_text: str, solution_text: str):
        """Ajoute un vote pour une solution existante."""
        # Trouver le nœud erreur
        error_node = None
        solution_node = None
        for node in self.graph['nodes']:
            if node['type'] == 'error' and node['text'] == error_text:
                error_node = node
            if node['type'] == 'solution' and node['text'] == solution_text:
                solution_node = node
        
        if not error_node or not solution_node:
            return "Error or solution not found."
        
        # Trouver le lien entre eux
        for edge in self.graph['edges']:
            if edge['source'] == error_node['id'] and edge['target'] == solution_node['id']:
                edge['weight'] += 1
                self._save()
                return f"✅ Weight increased to {edge['weight']}."
        
        return "No link has been found between this error and this solution."
    
    def vote_for_solution(self, error_text: str, solution_text: str) -> str:
        """
        Ajoute un vote pour une solution existante.
        Retourne un message de confirmation ou d'erreur.
        """
        # Normaliser les textes pour la comparaison
        from .search import normalize_text
        error_norm = normalize_text(error_text)
        solution_norm = normalize_text(solution_text)
        
        # Trouver le nœud erreur correspondant (comparaison normalisée)
        error_node = None
        solution_node = None
        
        for node in self.graph['nodes']:
            if node['type'] == 'error' and normalize_text(node['text']) == error_norm:
                error_node = node
            if node['type'] == 'solution' and normalize_text(node['text']) == solution_norm:
                solution_node = node
        
        if not error_node:
            return "❌ Error not found. Check the exact wording."
        if not solution_node:
            return "❌ Solution not found. Check the exact wording."
        
        # Trouver le lien entre erreur et solution
        for edge in self.graph['edges']:
            if edge['source'] == error_node['id'] and edge['target'] == solution_node['id']:
                edge['weight'] += 1
                self._save()
                return f"✅ Vote recorded. Weight of the solution : {edge['weight']}"
        
        return "❌ No link found between this error and this solution. Did you add the correction correctly ?"
    
    def export_to_file(self, filepath: str) -> str:
        """
        Exporte tout le graphe vers un fichier JSON.
        Retourne un message de confirmation.
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.graph, f, indent=2, ensure_ascii=False)
            return f"✅ Export successful to {filepath} ({len(self.graph['nodes'])} nodes, {len(self.graph['edges'])} edges)"
        except Exception as e:
            return f"❌ Error during export : {e}"

    def import_from_file(self, filepath: str) -> str:
        """
        Importe un graphe depuis un fichier JSON et le fusionne avec le graphe existant.
        Retourne un message de confirmation.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported = json.load(f)
            
            # Vérification basique de la structure
            if not isinstance(imported, dict) or 'nodes' not in imported or 'edges' not in imported:
                return "❌ Invalid file: must contain “nodes” and “edges”."
            
            # Compter avant fusion
            nodes_before = len(self.graph['nodes'])
            edges_before = len(self.graph['edges'])
            
            # Fusionner les nœuds (sans doublon basé sur l'ID)
            existing_ids = {node['id'] for node in self.graph['nodes']}
            for node in imported['nodes']:
                if node['id'] not in existing_ids:
                    self.graph['nodes'].append(node)
                    existing_ids.add(node['id'])
            
            # Fusionner les arêtes (sans doublon basé sur source+target)
            existing_edges = {(edge['source'], edge['target']) for edge in self.graph['edges']}
            for edge in imported['edges']:
                key = (edge['source'], edge['target'])
                if key not in existing_edges:
                    self.graph['edges'].append(edge)
                    existing_edges.add(key)
                else:
                    # Si l'arête existe déjà, on additionne les poids
                    for existing_edge in self.graph['edges']:
                        if existing_edge['source'] == edge['source'] and existing_edge['target'] == edge['target']:
                            existing_edge['weight'] += edge['weight']
                            break
            
            self._save()
            
            nodes_added = len(self.graph['nodes']) - nodes_before
            edges_added = len(self.graph['edges']) - edges_before
            
            return f"✅ Import successful : {nodes_added} new nodes, {edges_added} new edges (merged weights)."
        
        except FileNotFoundError:
            return f"❌ File not found : {filepath}"
        except json.JSONDecodeError:
            return f"❌ Invalid JSON file : {filepath}"
        except Exception as e:
            return f"❌ Error during import : {e}"