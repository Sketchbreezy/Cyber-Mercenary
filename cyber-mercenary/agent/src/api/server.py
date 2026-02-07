"""
Cyber-Mercenary API - Phase 2

Integrated API with MiniMax AI, database, and ECDSA signing.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import logging
import uuid
import asyncio

from config import settings

logger = logging.getLogger(__name__)

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
    version="2.0.0",
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
    contract_address: str
    chain_id: int = 10143
    scan_depth: str = "standard"


class ScanResponse(BaseModel):
    scan_id: str
    status: str
    contract_address: str
    vulnerabilities: List[dict]
    risk_score: float
    warning: Optional[str] = None
    signature: Optional[str] = None


class BountyRequest(BaseModel):
    amount_wei: int
    ipfs_hash: str
    expires_in: int = 86400


class BountyResponse(BaseModel):
    bounty_id: int
    tx_hash: str
    status: str
    amount: int


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
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "agent": "CyberMercenary",
        "phase": "2",
        "services": "ready" if services_ready else "limited"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Cyber-Mercenary",
        "version": "2.0.0",
        "status": "running",
        "phase": 2
    }


@app.post("/api/v1/scan", response_model=ScanResponse)
async def submit_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """Submit a contract for AI-powered scanning"""
    scan_id = f"scan_{uuid.uuid4().hex[:8]}"

    logger.info(f"📝 Scan submitted: {request.contract_address}")

    # Save initial scan record
    db.save_scan(scan_id, request.contract_address, request.chain_id, status="queued")

    # Start background scan
    background_tasks.add_task(perform_scan, scan_id, request.contract_address, request.chain_id)

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
async def list_scans(limit: int = 20):
    """List all scans"""
    return {"scans": db.get_all_scans(limit)}


@app.post("/api/v1/bounty/create")
async def create_bounty(request: BountyRequest):
    """Create a bounty"""
    if not scanner.is_connected():
        raise HTTPException(status_code=503, detail="Blockchain not connected")

    bounty_id, tx_hash = await scanner.create_bounty(
        request.amount_wei,
        request.ipfs_hash,
        request.expires_in
    )

    db.save_bounty(bounty_id, None, request.amount_wei, "created")

    return {
        "bounty_id": bounty_id,
        "tx_hash": tx_hash,
        "status": "created",
        "amount": request.amount_wei,
    }


@app.get("/api/v1/bounty/{bounty_id}")
async def get_bounty_status(bounty_id: int):
    """Get bounty status"""
    bounty = db.get_bounty(bounty_id)
    if not bounty:
        raise HTTPException(status_code=404, detail="Bounty not found")

    chain_status = await scanner.check_bounty_status(bounty_id)

    return {
        **bounty,
        **chain_status
    }


@app.get("/api/v1/stats")
async def get_stats():
    """Get agent statistics"""
    return db.get_stats()


@app.get("/api/v1/agent/address")
async def get_agent_address():
    """Get the agent's signing address"""
    if not services_ready:
        raise HTTPException(status_code=503, detail="Services not ready")

    return {
        "address": signer.address
    }


@app.post("/api/v1/sign")
async def sign_message(message: str):
    """Sign a message with ECDSA"""
    if not services_ready:
        raise HTTPException(status_code=503, detail="Services not ready")

    signed = signer.sign_message(message)
    return {
        "message": signed.message,
        "signature": signed.signature,
        "hash": signed.hash,
        "signer": signed.signer_address
    }


@app.post("/api/v1/verify")
async def verify_signature(message: str, signature: str, address: str):
    """Verify a signature"""
    if not services_ready:
        raise HTTPException(status_code=503, detail="Services not ready")

    valid = signer.verify_signature(message, signature, address)
    return {
        "valid": valid
    }


logger.info("✅ API Server loaded (Phase 2)")
