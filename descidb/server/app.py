# Create new file: descidb/server/app.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import os
import sys

# Import your entry points
from descidb.query.evaluation_agent import EvaluationAgent

# Setup FastAPI app
app = FastAPI(
    title="DeSciDB API",
    description="API for DeSciDB - a decentralized RAG database",
    version="0.1.0"
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
        
        # Evaluate results
        evaluation = agent.evaluate_results(results_file)
        
        return evaluation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)