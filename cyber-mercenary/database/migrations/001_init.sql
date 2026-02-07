-- Cyber-Mercenary Database Schema (SQLite)
-- Migration: 001_init.sql

-- Bounties table
CREATE TABLE IF NOT EXISTS bounties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_hash VARCHAR(66) NOT NULL UNIQUE,
    developer_address VARCHAR(42) NOT NULL,
    amount_wei BIGINT NOT NULL,
    status VARCHAR(20) DEFAULT 'open', -- open, claimed, disputed, expired
    ipfs_report_hash VARCHAR(46),
    agent_signature VARCHAR(132),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    claimed_at TIMESTAMP,
    disputed_at TIMESTAMP
);

-- Warnings table
CREATE TABLE IF NOT EXISTS warnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_address VARCHAR(42) NOT NULL,
    vulnerability_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    summary TEXT NOT NULL,
    full_report_ipfs VARCHAR(46),
    developer_contact VARCHAR(42),
    status VARCHAR(20) DEFAULT 'pending', -- pending, acknowledged, resolved
    bounty_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (bounty_id) REFERENCES bounties(id)
);

-- Gigs table (A2A marketplace)
CREATE TABLE IF NOT EXISTS gigs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requester_agent VARCHAR(42) NOT NULL,
    provider_agent VARCHAR(42),
    task_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'open', -- open, assigned, completed, cancelled
    fee_wei BIGINT NOT NULL,
    escrow_id INTEGER,
    result_ipfs VARCHAR(46),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (escrow_id) REFERENCES bounties(id)
);

-- Contracts scanned table
CREATE TABLE IF NOT EXISTS contracts_scanned (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address VARCHAR(42) NOT NULL,
    chain_id INTEGER NOT NULL,
    bytecode_hash VARCHAR(66),
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vulnerabilities_found INTEGER DEFAULT 0,
    severity_distribution TEXT, -- JSON: {"critical": 0, "high": 1, "medium": 2, "low": 5}
    PRIMARY KEY (address, chain_id)
);

-- Agent stats table
CREATE TABLE IF NOT EXISTS agent_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL UNIQUE,
    contracts_scanned INTEGER DEFAULT 0,
    vulnerabilities_found INTEGER DEFAULT 0,
    bounties_earned_wei BIGINT DEFAULT 0,
    gigs_completed INTEGER DEFAULT 0,
    fees_earned_wei BIGINT DEFAULT 0
);

-- Scans queue table
CREATE TABLE IF NOT EXISTS scans_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address VARCHAR(42) NOT NULL,
    chain_id INTEGER NOT NULL,
    priority INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
    scan_depth VARCHAR(20) DEFAULT 'standard',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_bounties_status ON bounties(status);
CREATE INDEX IF NOT EXISTS idx_warnings_severity ON warnings(severity);
CREATE INDEX IF NOT EXISTS idx_warnings_contract ON warnings(contract_address);
CREATE INDEX IF NOT EXISTS idx_gigs_status ON gigs(status);
CREATE INDEX IF NOT EXISTS idx_contracts_scanned_address ON contracts_scanned(address);
CREATE INDEX IF NOT EXISTS idx_scans_queue_status ON scans_queue(status);
