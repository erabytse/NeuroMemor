from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import threading
import tempfile
import json
from src.graph import KnowledgeGraph
from src.search import fuzzy_search

# Créer l'application FastAPI
app = FastAPI(title="NeuroMemor API", description="A collective repository for developers")

# Variables globales (seront initialisées par start_api)
kg = None
network = None

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
    return {"message": "NeuroMemor API is running", "version": "0.6"}

@app.post("/correction")
def add_correction(correction: CorrectionInput):
    """Ajoute une nouvelle correction."""
    if kg is None:
        raise HTTPException(status_code=503, detail="API not initialised")
    kg.add_correction(correction.error, correction.solution)
    # Diffuser aux pairs (si réseau disponible)
    if network:
        network.send_update(correction.error, correction.solution)
    return {"status": "success", "message": "Correction added and published"}

@app.post("/vote")
def vote(vote: VoteInput):
    """Vote pour une solution existante."""
    if kg is None:
        raise HTTPException(status_code=503, detail="API not initialised")
    result = kg.vote_for_solution(vote.error, vote.solution)
    return {"status": "success", "message": result}

@app.get("/search")
def search(query: str, threshold: float = 0.2):
    """Recherche une solution par similarité."""
    if kg is None:
        raise HTTPException(status_code=503, detail="API not initialised")
    results = fuzzy_search(kg.graph, query, threshold)
    return [SearchResult(**r) for r in results]

@app.get("/export")
def export():
    """Exporte le graphe complet."""
    if kg is None:
        raise HTTPException(status_code=503, detail="API not initialised")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(kg.graph, f, indent=2)
        f.flush()
        return {"file": f.name}
    
@app.get("/stats")
def stats():
    """Retourne des statistiques sur le graphe."""
    if kg is None:
        raise HTTPException(status_code=503, detail="API not initialised")
    return {
        "nodes": len(kg.graph['nodes']),
        "edges": len(kg.graph['edges']),
        "peers": len(network.peers) if network else 0
    }

def start_api(kg_instance, network_instance=None, host="0.0.0.0", port=8000):
    """Démarre l'API avec les instances de graphe et réseau."""
    global kg, network
    kg = kg_instance
    network = network_instance
    print(f"[API] Starting on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")