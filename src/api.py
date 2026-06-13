from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src import network
import uvicorn
import threading
from src.graph import KnowledgeGraph
from src.search import fuzzy_search

app = FastAPI(title="NeuroMemor API", description="Mémoire collective associative pour développeurs")

# Initialisation du graphe (partagé)
kg = KnowledgeGraph()

class CorrectionInput(BaseModel):
    error: str
    solution: str

class VoteInput(BaseModel):
    error: str
    solution: str

class SearchResult(BaseModel):
    error: str
    solution: str
    weight: int
    similarity: float

@app.get("/")
def root():
    return {"message": "NeuroMemor API est en ligne", "version": "0.6"}

@app.post("/correction")
def add_correction(correction: CorrectionInput):
    """Ajoute une nouvelle correction."""
    kg.add_correction(correction.error, correction.solution)
    # Diffuser aux pairs
    from run import network  # Import tardif pour éviter la circularité
    if network:
        network.send_update(correction.error, correction.solution)
    return {"status": "success", "message": "Correction ajoutée et diffusée"}

@app.post("/vote")
def vote(vote: VoteInput):
    """Vote pour une solution existante."""
    result = kg.vote_for_solution(vote.error, vote.solution)
    return {"status": "success", "message": result}

@app.get("/search")
def search(query: str, threshold: float = 0.2):
    """Recherche une solution par similarité."""
    results = fuzzy_search(kg.graph, query, threshold)
    return [SearchResult(**r) for r in results]

@app.get("/export")
def export():
    """Exporte le graphe complet."""
    import tempfile
    import json
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(kg.graph, f, indent=2)
        f.flush()
        return {"file": f.name}
    
@app.get("/stats")
def stats():
    """Retourne des statistiques sur le graphe."""
    return {
        "nodes": len(kg.graph['nodes']),
        "edges": len(kg.graph['edges']),
        "peers": len(network.peers) if network else 0
    }

def start_api(host="0.0.0.0", port=8000):
    """Démarre l'API (à appeler dans un thread)."""
    uvicorn.run(app, host=host, port=port, log_level="info")