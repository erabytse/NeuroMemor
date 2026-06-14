import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class Correction:
    def __init__(self, error: str, solution: str, user_id: str = "anonymous"):
        self.error = error
        self.solution = solution
        self.user_id = user_id
        self.timestamp = datetime.now().isoformat()
        self.weight = 1
        self.id = f"corr_{hash(error + solution) & 0xFFFFFFFF}"

class CorrectionGraph:
    """Graphe de corrections avec gestion des nœuds et arêtes."""
    
    def __init__(self, data_path: str = "data/corrections.json"):
        self.data_path = Path(data_path)
        self.data_path.parent.mkdir(exist_ok=True)
        self._load()
    
    def _load(self):
        """Charge le graphe depuis le fichier JSON."""
        if self.data_path.exists():
            try:
                with open(self.data_path, 'r') as f:
                    data = json.load(f)
                    self.nodes = data.get('nodes', [])
                    self.edges = data.get('edges', [])
                    return
            except:
                pass
        self.nodes = []
        self.edges = []
    
    def _save(self):
        """Sauvegarde le graphe dans le fichier JSON."""
        with open(self.data_path, 'w') as f:
            json.dump({'nodes': self.nodes, 'edges': self.edges}, f, indent=2)
    
    def add_correction(self, error: str, solution: str, user_id: str = "anonymous"):
        """Ajoute une correction au graphe."""
        # Vérifier si l'erreur existe déjà
        error_node = None
        for node in self.nodes:
            if node['type'] == 'error' and node['text'] == error:
                error_node = node
                break
        
        if error_node is None:
            error_node = {
                'id': f"error_{len(self.nodes)}",
                'type': 'error',
                'text': error,
                'user': user_id,
                'timestamp': datetime.now().isoformat()
            }
            self.nodes.append(error_node)
        
        # Vérifier si la solution existe déjà
        solution_node = None
        for node in self.nodes:
            if node['type'] == 'solution' and node['text'] == solution:
                solution_node = node
                break
        
        if solution_node is None:
            solution_node = {
                'id': f"solution_{len(self.nodes)}",
                'type': 'solution',
                'text': solution,
                'user': user_id,
                'timestamp': datetime.now().isoformat()
            }
            self.nodes.append(solution_node)
        
        # Vérifier si le lien existe déjà
        link_exists = False
        for edge in self.edges:
            if edge['source'] == error_node['id'] and edge['target'] == solution_node['id']:
                edge['weight'] += 1
                link_exists = True
                break
        
        if not link_exists:
            self.edges.append({
                'source': error_node['id'],
                'target': solution_node['id'],
                'weight': 1,
                'type': 'solves'
            })
        
        self._save()
        return error_node['id'], solution_node['id']
    
    def vote(self, error: str, solution: str):
        """Vote pour une correction existante."""
        error_node = None
        solution_node = None
        
        for node in self.nodes:
            if node['type'] == 'error' and node['text'] == error:
                error_node = node
            if node['type'] == 'solution' and node['text'] == solution:
                solution_node = node
        
        if error_node is None or solution_node is None:
            return False, "Error or solution not found"
        
        for edge in self.edges:
            if edge['source'] == error_node['id'] and edge['target'] == solution_node['id']:
                edge['weight'] += 1
                self._save()
                return True, f"Weight increased to {edge['weight']}"
        
        return False, "No link found"