# This is the main API server
# It connects everything together: model + database + frontend

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import model
import database

# Initialize database tables
database.init_database()

# Create FastAPI app
app = FastAPI(title="PhishGuard API", description="Phishing URL Detection API")

# Enable CORS (so frontend can call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request/response models
class URLRequest(BaseModel):
    url: str

class BatchURLRequest(BaseModel):
    urls: List[str]

class BlockRequest(BaseModel):
    url: str
    action: str  # "block" or "unblock"

class PredictResponse(BaseModel):
    url: str
    label: str
    confidence: float
    reasons: List[str]

# ============ API ENDPOINTS ============

@app.get("/")
def root():
    """Root endpoint - API is running"""
    return {"message": "🛡️ PhishGuard API is running", "status": "active"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.post("/predict", response_model=PredictResponse)
def predict_single(request: URLRequest):
    """
    Predict if a single URL is phishing or safe.
    This uses REAL logic - no fake data.
    """
    url = request.url
    
    # Run the prediction model
    result = model.predict_url(url)
    
    # Save to database history
    database.save_url_check(
        url=url,
        label=result['label'],
        confidence=result['confidence'],
        reasons=result['reasons']
    )
    
    return PredictResponse(
        url=url,
        label=result['label'],
        confidence=result['confidence'],
        reasons=result['reasons']
    )

@app.post("/predict-batch")
def predict_batch(request: BatchURLRequest):
    """
    Predict multiple URLs at once (for email scanner)
    """
    results = []
    for url in request.urls:
        result = model.predict_url(url)
        database.save_url_check(
            url=url,
            label=result['label'],
            confidence=result['confidence'],
            reasons=result['reasons']
        )
        results.append({
            "url": url,
            "label": result['label'],
            "confidence": result['confidence'],
            "reasons": result['reasons']
        })
    
    return {"results": results, "total": len(results)}

@app.get("/history")
def get_history(limit: int = 50):
    """
    Get recently checked URLs
    """
    history = database.get_history(limit)
    return {"history": history, "count": len(history)}

@app.delete("/history")
def clear_history():
    """
    Clear all check history
    """
    database.clear_history()
    return {"message": "History cleared successfully"}

@app.post("/block")
def block_url(request: BlockRequest):
    """
    Permanently block a URL (user action)
    """
    if request.action == "block":
        success = database.block_link(request.url)
        return {"success": success, "message": f"URL {'blocked' if success else 'already blocked'}"}
    elif request.action == "unblock":
        success = database.unblock_link(request.url)
        return {"success": success, "message": "URL unblocked" if success else "URL not found"}
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'block' or 'unblock'")

@app.get("/blocked")
def get_blocked():
    """
    Get all permanently blocked URLs
    """
    blocked = database.get_blocked_links()
    return {"blocked": blocked, "count": len(blocked)}

@app.post("/check-blocked")
def check_blocked(request: URLRequest):
    """
    Check if a specific URL is blocked
    """
    is_blocked = database.is_url_blocked(request.url)
    return {"url": request.url, "is_blocked": is_blocked}