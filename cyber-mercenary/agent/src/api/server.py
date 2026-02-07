"""
FastAPI Server for Cyber-Mercenary Agent

Provides REST API for agent communication and control.
"""

import logging
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import Settings
from main import CyberMercenary

logger = logging.getLogger(__name__)


# Request/Response Models
class ScanRequest(BaseModel):
    """Request to scan a contract"""
    contract_address: str = Field(..., description="Contract address to scan")
    chain_id: int = Field(default=10143, description="Chain ID")
    scan_depth: str = Field(default="standard", description="Scan depth")


class ScanResponse(BaseModel):
    """Scan result response"""
    scan_id: str
    status: str
    contract_address: str
    vulnerabilities: list
    risk_score: float
    warning: Optional[str] = None
    signature: Optional[str] = None


class BountyCreateRequest(BaseModel):
    """Request to create a bounty"""
    amount_wei: int = Field(..., description="Bounty amount in wei")
    ipfs_hash: str = Field(..., description="IPFS hash of report template")
    expires_in: int = Field(default=86400, description="Expires in seconds")


class BountyResponse(BaseModel):
    """Bounty information"""
    bounty_id: int
    tx_hash: str
    status: str
    amount: int
    expires_at: int


class GigRequest(BaseModel):
    """Request to create a gig"""
    task_type: str = Field(..., description="Type of task")
    description: str = Field(..., description="Task description")
    fee_wei: int = Field(..., description="Gig fee in wei")
    required_skills: list[str] = Field(default=[], description="Required skills")


class GigResponse(BaseModel):
    """Gig information"""
    gig_id: int
    status: str
    task_type: str
    fee: int


class StatsResponse(BaseModel):
    """Agent statistics"""
    contracts_scanned: int
    vulnerabilities_found: int
    bounties_earned: int
    gigs_completed: int
    uptime_seconds: int


# Global agent reference
_agent: Optional[CyberMercenary] = None


def set_agent(agent: CyberMercenary):
    """Set the global agent reference"""
    global _agent
    _agent = agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager"""
    logger.info("Cyber-Mercenary API starting...")
    yield
    logger.info("Cyber-Mercenary API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Cyber-Mercenary API",
    description="Autonomous AI security agent for Monad blockchain",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agent": "CyberMercenary"}


# Scanning Endpoints
@app.post("/api/v1/scan", response_model=ScanResponse)
async def submit_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """
    Submit a contract for scanning.

    Returns a scan ID that can be used to check status.
    """
    if not _agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    import uuid

    scan_id = f"scan_{uuid.uuid4().hex[:8]}"

    # Start scan in background
    background_tasks.add_task(
        _run_scan,
        scan_id,
        request.contract_address,
        request.chain_id,
    )

    return {
        "scan_id": scan_id,
        "status": "queued",
        "contract_address": request.contract_address,
        "vulnerabilities": [],
        "risk_score": 0,
        "warning": None,
        "signature": None,
    }


@app.get("/api/v1/scan/{scan_id}")
async def get_scan_status(scan_id: str):
    """Get scan status and results"""
    # In a real implementation, this would check the database
    return {
        "scan_id": scan_id,
        "status": "processing",
        "result": None,
    }


# Bounty Endpoints
@app.post("/api/v1/bounty/create", response_model=BountyResponse)
async def create_bounty(request: BountyCreateRequest):
    """Create a new bounty"""
    if not _agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        bounty_id, tx_hash = await _agent.scanner.create_bounty(
            request.amount_wei,
            request.ipfs_hash,
            request.expires_in,
        )

        return {
            "bounty_id": bounty_id,
            "tx_hash": tx_hash,
            "status": "created",
            "amount": request.amount_wei,
            "expires_at": 0,  # Would calculate from expires_in
        }
    except Exception as e:
        logger.error(f"Failed to create bounty: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/bounty/list")
async def list_bounties(status: Optional[str] = None):
    """List available bounties"""
    return {"bounties": []}


@app.post("/api/v1/bounty/{bounty_id}/claim")
async def claim_bounty(bounty_id: int):
    """Claim a bounty"""
    return {"status": "success", "bounty_id": bounty_id}


# Gig Endpoints
@app.post("/api/v1/gig/create", response_model=GigResponse)
async def create_gig(request: GigRequest):
    """Create a new gig request"""
    return {
        "gig_id": 1,
        "status": "created",
        "task_type": request.task_type,
        "fee": request.fee_wei,
    }


@app.get("/api/v1/gig/list")
async def list_gigs(status: Optional[str] = None):
    """List available gigs"""
    return {"gigs": []}


@app.post("/api/v1/gig/{gig_id}/accept")
async def accept_gig(gig_id: int):
    """Accept a gig"""
    return {"status": "success", "gig_id": gig_id}


@app.post("/api/v1/gig/{gig_id}/complete")
async def complete_gig(gig_id: int, result_ipfs: str):
    """Complete a gig"""
    return {"status": "success", "gig_id": gig_id}


# Warning Endpoints
@app.get("/api/v1/warnings")
async def list_warnings(severity: Optional[str] = None):
    """List security warnings"""
    return {"warnings": []}


@app.get("/api/v1/warnings/{warning_id}")
async def get_warning(warning_id: int):
    """Get warning details"""
    return {"id": warning_id, "status": "pending"}


# Stats Endpoints
@app.get("/api/v1/stats", response_model=StatsResponse)
async def get_stats():
    """Get agent statistics"""
    return {
        "contracts_scanned": 0,
        "vulnerabilities_found": 0,
        "bounties_earned": 0,
        "gigs_completed": 0,
        "uptime_seconds": 0,
    }


# Background Tasks
async def _run_scan(scan_id: str, address: str, chain_id: int):
    """Run a contract scan in the background"""
    logger.info(f"Starting background scan: {scan_id}")

    try:
        result = await _agent.analyze_contract(address, chain_id)

        # Store result in database
        logger.info(f"Scan {scan_id} completed: {len(result['analysis'].vulnerabilities)} vulns found")

    except Exception as e:
        logger.error(f"Scan {scan_id} failed: {e}")


def create_app(agent: CyberMercenary) -> FastAPI:
    """Create and configure the FastAPI app"""
    set_agent(agent)
    return app
