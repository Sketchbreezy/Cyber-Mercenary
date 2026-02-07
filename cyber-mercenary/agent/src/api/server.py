"""
Cyber-Mercenary API - Phase 2

Integrated API with MiniMax AI, database, and ECDSA signing.
Phase 3: Added rate limiting and security headers for production hardening.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator, constr
from typing import Optional, List
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import uuid
import asyncio
import re

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from .security import (
    SecurityHeadersMiddleware,
    sanitize_input,
    validate_ethereum_address,
    sanitize_numeric_input,
    sanitize_ipfs_hash
)

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Initialize services
try:
    from services.minimax import MiniMaxClient
    from services.scanner import ContractScanner
    from services.signer import SignatureManager
    from services.database import DatabaseService

    minimax_client = MiniMaxClient(settings)
    scanner = ContractScanner(settings)
    signer = SignatureManager(settings)
    db = DatabaseService(settings.database.url)

    services_ready = True
    logger.info("✅ All Phase 2 services initialized")
except Exception as e:
    logger.warning(f"⚠️ Services not fully initialized: {e}")
    services_ready = False

# Create FastAPI app
app = FastAPI(
    title="Cyber-Mercenary API",
    description="Autonomous AI security agent for Monad",
    version="3.0.0",
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiter to app
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return HTTPException(
        status_code=429,
        detail={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please slow down.",
            "retry_after": getattr(exc, "retry_after", 60)
        }
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ScanRequest(BaseModel):
    """Request model for contract scanning"""
    contract_address: constr(min_length=42, max_length=42)  # 0x + 40 hex chars
    chain_id: int = 10143
    scan_depth: str = "standard"
    
    @validator('contract_address')
    def validate_address(cls, v):
        if not validate_ethereum_address(v):
            raise ValueError('Invalid Ethereum address format')
        return v.lower()
    
    @validator('chain_id')
    def validate_chain_id(cls, v):
        if v not in [10143, 1, 5, 11155111]:  # Monad testnet, Ethereum, Goerli, Sepolia
            raise ValueError('Unsupported chain ID')
        return v
    
    @validator('scan_depth')
    def validate_scan_depth(cls, v):
        if v not in ['standard', 'deep', 'quick']:
            raise ValueError('Invalid scan depth')
        return v


class ScanResponse(BaseModel):
    """Response model for scan results"""
    scan_id: str
    status: str
    contract_address: str
    vulnerabilities: List[dict]
    risk_score: float
    warning: Optional[str] = None
    signature: Optional[str] = None


class BountyRequest(BaseModel):
    """Request model for bounty creation"""
    amount_wei: int
    ipfs_hash: constr(min_length=46, max_length=59)  # IPFS CIDv0/v1
    expires_in: int = 86400
    
    @validator('amount_wei')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        if v > 10**22:  # Max 10,000 ETH
            raise ValueError('Amount exceeds maximum')
        return v
    
    @validator('ipfs_hash')
    def validate_ipfs_hash(cls, v):
        if not re.match(r'^(Qm[1-9A-HJ-NP-Za-km-z]{44}|baf[a-zA-Z0-9]{52,})$', v):
            raise ValueError('Invalid IPFS hash format')
        return v
    
    @validator('expires_in')
    def validate_expires_in(cls, v):
        if v < 3600:  # Minimum 1 hour
            raise ValueError('Expires in must be at least 1 hour')
        if v > 30 * 86400:  # Maximum 30 days
            raise ValueError('Expires in cannot exceed 30 days')
        return v


class SignRequest(BaseModel):
    """Request model for message signing"""
    message: constr(max_length=1000)
    
    @validator('message')
    def validate_message(cls, v):
        # Remove null bytes and sanitize
        v = v.replace('\x00', '')
        return v.strip()


class VerifyRequest(BaseModel):
    """Request model for signature verification"""
    message: constr(max_length=1000)
    signature: constr(min_length=132, max_length=138)  # Ethereum signature
    address: constr(min_length=42, max_length=42)
    
    @validator('signature')
    def validate_signature(cls, v):
        if not re.match(r'^0x[a-fA-F0-9]{130}$', v):
            raise ValueError('Invalid signature format')
        return v.lower()
    
    @validator('address')
    def validate_address(cls, v):
        if not validate_ethereum_address(v):
            raise ValueError('Invalid Ethereum address format')
        return v.lower()


class BountyDisputeRequest(BaseModel):
    """Request model for bounty dispute"""
    bounty_id: int
    
    @validator('bounty_id')
    def validate_bounty_id(cls, v):
        if v <= 0:
            raise ValueError('Bounty ID must be positive')
        return v


class BountyResolveRequest(BaseModel):
    """Request model for bounty resolution"""
    bounty_id: int
    reward_developer: bool
    
    @validator('bounty_id')
    def validate_bounty_id(cls, v):
        if v <= 0:
            raise ValueError('Bounty ID must be positive')
        return v


# Background task for async scanning
async def perform_scan(scan_id: str, contract_address: str, chain_id: int):
    """Background task to perform contract scan"""
    try:
        logger.info(f"🔍 Starting scan {scan_id} for {contract_address}")

        # Get contract code
        result = await scanner.scan_address(contract_address, chain_id)

        if not result.is_contract:
            db.save_scan(scan_id, contract_address, chain_id, status="not_contract", risk_score=0)
            return

        # Analyze with MiniMax
        if services_ready and settings.minimax.api_key:
            analysis = await minimax_client.analyze_contract(result.bytecode)
            analysis.contract_address = contract_address

            # Sign the warning if vulnerabilities found
            warning = None
            signature = None
            if analysis.vulnerabilities:
                vuln_data = [{
                    "type": v.type,
                    "severity": v.severity,
                    "description": v.description
                } for v in analysis.vulnerabilities]
                warning_text = f"Found {len(analysis.vulnerabilities)} vulnerabilities in {contract_address}"
                warning = warning_text
                signed = signer.sign_warning(warning_text)
                signature = signed.signature

                # Save to database
                db.save_scan(
                    scan_id=scan_id,
                    contract_address=contract_address,
                    chain_id=chain_id,
                    status="completed",
                    risk_score=analysis.overall_risk_score,
                    vulnerability_count=len(analysis.vulnerabilities),
                    result_data=str(vuln_data)
                )
                db.increment_vulnerabilities(len(analysis.vulnerabilities))
            else:
                db.save_scan(
                    scan_id=scan_id,
                    contract_address=contract_address,
                    chain_id=chain_id,
                    status="completed",
                    risk_score=analysis.overall_risk_score,
                    vulnerability_count=0
                )
        else:
            # Fallback without AI
            db.save_scan(
                scan_id=scan_id,
                contract_address=contract_address,
                chain_id=chain_id,
                status="completed",
                risk_score=0,
                vulnerability_count=0
            )

        logger.info(f"✅ Scan {scan_id} completed")

    except Exception as e:
        logger.error(f"❌ Scan {scan_id} failed: {e}")
        db.save_scan(scan_id, contract_address, chain_id, status="failed")


# Endpoints
@app.get("/health")
@limiter.limit("200/minute")
async def health_check(request: Request):
    """Health check"""
    return {
        "status": "healthy",
        "agent": "CyberMercenary",
        "phase": "3",
        "services": "ready" if services_ready else "limited"
    }


@app.get("/")
@limiter.limit("200/minute")
async def root(request: Request):
    """Root endpoint"""
    return {
        "name": "Cyber-Mercenary",
        "version": "3.0.0",
        "status": "running",
        "phase": 3
    }


@app.post("/api/v1/scan", response_model=ScanResponse)
@limiter.limit("10/minute")
async def submit_scan(request: Request, scan_request: ScanRequest, background_tasks: BackgroundTasks):
    """Submit a contract for AI-powered scanning"""
    scan_id = f"scan_{uuid.uuid4().hex[:8]}"

    logger.info(f"📝 Scan submitted: {scan_request.contract_address}")

    # Save initial scan record
    db.save_scan(scan_id, scan_request.contract_address, scan_request.chain_id, status="queued")

    # Start background scan
    background_tasks.add_task(perform_scan, scan_id, scan_request.contract_address, scan_request.chain_id)

    return {
        "scan_id": scan_id,
        "status": "queued",
        "contract_address": scan_request.contract_address,
        "vulnerabilities": [],
        "risk_score": 0,
        "warning": None,
        "signature": None,
    }


@app.get("/api/v1/scan/{scan_id}")
async def get_scan_status(scan_id: str):
    """Get scan status and results"""
    scan = db.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    result_data = None
    if scan["result_data"]:
        try:
            result_data = eval(scan["result_data"])
        except:
            pass

    return {
        "scan_id": scan["scan_id"],
        "status": scan["status"],
        "contract_address": scan["contract_address"],
        "risk_score": scan["risk_score"],
        "vulnerabilities": result_data or [],
        "created_at": scan["created_at"],
    }


@app.get("/api/v1/scans")
@limiter.limit("30/minute")
async def list_scans(request: Request, limit: int = 20):
    """List all scans"""
    return {"scans": db.get_all_scans(limit)}


@app.post("/api/v1/bounty/create")
@limiter.limit("5/minute")
async def create_bounty(request: Request, bounty_request: BountyRequest):
    """Create a bounty"""
    if not scanner.is_connected():
        raise HTTPException(status_code=503, detail="Blockchain not connected")

    bounty_id, tx_hash = await scanner.create_bounty(
        bounty_request.amount_wei,
        bounty_request.ipfs_hash,
        bounty_request.expires_in
    )

    db.save_bounty(bounty_id, None, bounty_request.amount_wei, "created")

    return {
        "bounty_id": bounty_id,
        "tx_hash": tx_hash,
        "status": "created",
        "amount": bounty_request.amount_wei,
    }


@app.get("/api/v1/bounty/{bounty_id}")
@limiter.limit("30/minute")
async def get_bounty_status(request: Request, bounty_id: int):
    """Get bounty status"""
    bounty = db.get_bounty(bounty_id)
    if not bounty:
        raise HTTPException(status_code=404, detail="Bounty not found")

    chain_status = await scanner.get_bounty_status(bounty_id)

    return {
        **bounty,
        **chain_status
    }


@app.post("/api/v1/bounty/{bounty_id}/dispute")
@limiter.limit("5/minute")
async def dispute_bounty(request: Request, bounty_request: BountyDisputeRequest):
    """File a dispute for a bounty"""
    if not scanner.is_connected():
        raise HTTPException(status_code=503, detail="Blockchain not connected")

    tx_hash = await scanner.dispute_bounty(bounty_request.bounty_id)

    if tx_hash.startswith("error"):
        raise HTTPException(status_code=400, detail=tx_hash)

    return {
        "bounty_id": bounty_request.bounty_id,
        "tx_hash": tx_hash,
        "status": "disputed"
    }


@app.post("/api/v1/bounty/{bounty_id}/resolve")
@limiter.limit("5/minute")
async def resolve_dispute(request: Request, bounty_request: BountyResolveRequest):
    """Resolve a dispute (owner only)"""
    if not scanner.is_connected():
        raise HTTPException(status_code=503, detail="Blockchain not connected")

    tx_hash = await scanner.resolve_dispute(bounty_request.bounty_id, bounty_request.reward_developer)

    if tx_hash.startswith("error"):
        raise HTTPException(status_code=400, detail=tx_hash)

    return {
        "bounty_id": bounty_request.bounty_id,
        "tx_hash": tx_hash,
        "reward_developer": bounty_request.reward_developer,
        "status": "resolved"
    }


@app.post("/api/v1/bounty/{bounty_id}/claim")
@limiter.limit("5/minute")
async def claim_bounty(request: Request, bounty_id: int):
    """Claim a bounty"""
    if not scanner.is_connected():
        raise HTTPException(status_code=503, detail="Blockchain not connected")

    tx_hash = await scanner.claim_bounty(bounty_id)

    if tx_hash.startswith("error"):
        raise HTTPException(status_code=400, detail=tx_hash)

    return {
        "bounty_id": bounty_id,
        "tx_hash": tx_hash,
        "status": "claimed"
    }


@app.post("/api/v1/bounty/{bounty_id}/report")
async def submit_report(bounty_id: int, report_request: VerifyRequest):
    """Submit a vulnerability report with signature"""
    if not scanner.is_connected():
        raise HTTPException(status_code=503, detail="Blockchain not connected")

    # Validate bounty_id
    if bounty_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid bounty ID")

    tx_hash = await scanner.submit_report(bounty_id, report_request.signature)

    if tx_hash.startswith("error"):
        raise HTTPException(status_code=400, detail=tx_hash)

    return {
        "bounty_id": bounty_id,
        "tx_hash": tx_hash,
        "status": "report_submitted"
    }


@app.get("/api/v1/stats")
@limiter.limit("60/minute")
async def get_stats(request: Request):
    """Get agent statistics"""
    return db.get_stats()


@app.get("/api/v1/agent/address")
@limiter.limit("60/minute")
async def get_agent_address(request: Request):
    """Get the agent's signing address"""
    if not services_ready:
        raise HTTPException(status_code=503, detail="Services not ready")

    return {
        "address": signer.address
    }


@app.post("/api/v1/sign")
@limiter.limit("30/minute")
async def sign_message(request: Request, sign_request: SignRequest):
    """Sign a message with ECDSA"""
    if not services_ready:
        raise HTTPException(status_code=503, detail="Services not ready")

    signed = signer.sign_message(sign_request.message)
    return {
        "message": signed.message,
        "signature": signed.signature,
        "hash": signed.hash,
        "signer": signed.signer_address
    }


@app.post("/api/v1/verify")
@limiter.limit("30/minute")
async def verify_signature(request: Request, verify_request: VerifyRequest):
    """Verify a signature"""
    if not services_ready:
        raise HTTPException(status_code=503, detail="Services not ready")

    valid = signer.verify_signature(verify_request.message, verify_request.signature, verify_request.address)
    return {
        "valid": valid
    }


logger.info("✅ API Server loaded (Phase 2)")
