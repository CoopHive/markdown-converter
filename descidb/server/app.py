# Create new file: descidb/server/app.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import os
import sys
from fastapi.middleware.cors import CORSMiddleware

# Import your entry points
from descidb.query.evaluation_agent import EvaluationAgent

# Setup FastAPI app
app = FastAPI(
    title="DeSciDB API",
    description="API for DeSciDB - a decentralized RAG database",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Define request/response models
class EvaluationRequest(BaseModel):
    query: str
    collections: List[str]
    db_path: Optional[str] = None
    model_name: str = "openai/gpt-3.5-turbo"

@app.post("/api/evaluate")
async def evaluate_endpoint(request: EvaluationRequest):
    """Endpoint for evaluation (maps to run_evaluation.sh)"""
    try:
        # Initialize evaluation agent
        agent = EvaluationAgent(model_name=request.model_name)
        # Run query on collections
        results_file = agent.query_collections(
            query=request.query,
            collection_names=request.collections,
            db_path=request.db_path,
        )
        
        # Read the results from the JSON file
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)