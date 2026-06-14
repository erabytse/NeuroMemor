import re
import json
from typing import Dict, List, Any

def normalize_text(text: str) -> str:
    """Normalise le texte : minuscule, supprime ponctuation, espaces multiples."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def jaccard_similarity(text1: str, text2: str) -> float:
    """Calcule la similarité de Jaccard entre deux chaînes normalisées."""
    set1 = set(normalize_text(text1).split())
    set2 = set(normalize_text(text2).split())
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)

def fuzzy_search(graph: Dict, query: str, threshold: float = 0.2) -> List[Dict]:
    """Recherche floue par similarité Jaccard."""
    results = []
    for node in graph['nodes']:
        if node['type'] != 'error':
            continue
        sim = jaccard_similarity(query, node['text'])
        if sim >= threshold:
            # Trouve la solution liée
            for edge in graph['edges']:
                if edge['source'] == node['id']:
                    for sol_node in graph['nodes']:
                        if sol_node['id'] == edge['target']:
                            results.append({
                                "error": node['text'],
                                "solution": sol_node['text'],
                                "weight": edge['weight'],
                                "similarity": round(sim, 2)
                            })
    results.sort(key=lambda x: x['similarity'], reverse=True)
    return results

def export_graph(graph: Dict, filepath: str) -> str:
    """Exporte le graphe vers un fichier JSON."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)
    return f"✅ Exported to {filepath}"

def import_graph(filepath: str) -> Dict:
    """Importe un graphe depuis un fichier JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)