"""
Cyber-Mercenary API - Minimal Working Version
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import logging
import uuid

logger = logging.getLogger(__name__)

# Global agent reference (simple)
_agent = None

def set_agent(agent):
    global _agent
    _agent = agent

# Create FastAPI app
app = FastAPI(
    title="Cyber-Mercenary API",
    description="Autonomous AI security agent for Monad",
    version="1.0.0",
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ScanRequest(BaseModel):
    contract_address: str
    chain_id: int = 10143
    scan_depth: str = "standard"


class ScanResponse(BaseModel):
    scan_id: str
    status: str
    contract_address: str
    vulnerabilities: list
    risk_score: float
    warning: Optional[str] = None


class BountyRequest(BaseModel):
    amount_wei: int
    ipfs_hash: str
    expires_in: int = 86400


# Endpoints
@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "agent": "CyberMercenary"}


@app.post("/api/v1/scan", response_model=ScanResponse)
async def submit_scan(request: ScanRequest):
    """Submit a contract for scanning"""
    scan_id = f"scan_{uuid.uuid4().hex[:8]}"
    
    logger.info(f"📝 Scan submitted: {request.contract_address}")
    
    return {
        "scan_id": scan_id,
        "status": "queued",
        "contract_address": request.contract_address,
        "vulnerabilities": [],
        "risk_score": 0,
        "warning": None,
    }


@app.get("/api/v1/scan/{scan_id}")
async def get_scan_status(scan_id: str):
    """Get scan status"""
    return {
        "scan_id": scan_id,
        "status": "processing",
        "result": None,
    }


@app.post("/api/v1/bounty/create")
async def create_bounty(request: BountyRequest):
    """Create a bounty"""
    return {
        "bounty_id": 1,
        "tx_hash": "0xplaceholder",
        "status": "created",
        "amount": request.amount_wei,
    }


@app.get("/api/v1/stats")
async def get_stats():
    """Get agent statistics"""
    return {
        "contracts_scanned": 0,
        "vulnerabilities_found": 0,
        "bounties_earned": 0,
        "gigs_completed": 0,
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Cyber-Mercenary",
        "version": "1.0.0",
        "status": "running",
    }


logger.info("✅ API Server loaded")
