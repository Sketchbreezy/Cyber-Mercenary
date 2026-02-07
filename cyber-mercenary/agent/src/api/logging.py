"""
Structured JSON Logging for Cyber-Mercenary API

Provides:
- Structured JSON logging
- Request ID tracing
- Log level configuration
- Context-aware logging
"""

import sys
import os
import json
import logging
import uuid
import threading
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from pathlib import Path


# ============================================================================
# Log Level Configuration
# ============================================================================

LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

DEFAULT_LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


def get_log_level(level_name: str) -> int:
    """Get log level from string"""
    return LOG_LEVELS.get(level_name.upper(), logging.INFO)


# ============================================================================
# Request ID Context
# ============================================================================

_request_id_context = threading.local()


def get_request_id() -> str:
    """Get current request ID from context"""
    if hasattr(_request_id_context, 'request_id'):
        return _request_id_context.request_id
    return ""


def set_request_id(request_id: str):
    """Set request ID in context"""
    _request_id_context.request_id = request_id


def generate_request_id() -> str:
    """Generate a new request ID"""
    return f"req_{uuid.uuid4().hex[:12]}"


@contextmanager
def request_context(request_id: Optional[str] = None):
    """Context manager for request ID"""
    if request_id is None:
        request_id = generate_request_id()
    old_request_id = get_request_id()
    set_request_id(request_id)
    try:
        yield request_id
    finally:
        set_request_id(old_request_id)


# ============================================================================
# Structured Log Record
# ============================================================================

class StructuredLogRecord(logging.LogRecord):
    """Custom log record with structured fields"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_id = get_request_id()
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.service = "cyber-mercenary"
        self.version = "3.0.0"


class StructuredLogger:
    """Structured logger with JSON output"""
    
    def __init__(self, name: str, log_file: Optional[str] = None, 
                 json_output: bool = True, level: str = DEFAULT_LOG_LEVEL):
        self.name = name
        self.json_output = json_output
        self._setup_logger(log_file, level)
    
    def _setup_logger(self, log_file: Optional[str], level: str):
        """Setup the logger"""
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(get_log_level(level))
        self.logger.handlers = []
        self.logger.propagate = False
        
        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(get_log_level(level))
        
        if self.json_output:
            console_handler.setFormatter(JSONFormatter())
        else:
            console_handler.setFormatter(PlainFormatter())
        
        self.logger.addHandler(console_handler)
        
        # Add file handler if specified
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(get_log_level(level))
            file_handler.setFormatter(JSONFormatter())
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with structured data"""
        self.logger.debug(message, extra=self._extra(kwargs))
    
    def info(self, message: str, **kwargs):
        """Log info message with structured data"""
        self.logger.info(message, extra=self._extra(kwargs))
    
    def warning(self, message: str, **kwargs):
        """Log warning message with structured data"""
        self.logger.warning(message, extra=self._extra(kwargs))
    
    def error(self, message: str, **kwargs):
        """Log error message with structured data"""
        self.logger.error(message, extra=self._extra(kwargs))
    
    def critical(self, message: str, **kwargs):
        """Log critical message with structured data"""
        self.logger.critical(message, extra=self._extra(kwargs))
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback"""
        self.logger.exception(message, extra=self._extra(kwargs))
    
    def log_request(self, method: str, path: str, status_code: int, 
                    duration_ms: float, request_id: str, **kwargs):
        """Log HTTP request with structured data"""
        self.logger.info(
            f"{method} {path} {status_code}",
            extra=self._extra({
                "event": "http_request",
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "request_id": request_id,
                **kwargs
            })
        )
    
    def log_scan(self, scan_id: str, contract_address: str, status: str,
                 duration_ms: float, risk_score: float, **kwargs):
        """Log scan operation with structured data"""
        self.logger.info(
            f"Scan {scan_id}: {status}",
            extra=self._extra({
                "event": "scan_operation",
                "scan_id": scan_id,
                "contract_address": contract_address,
                "status": status,
                "duration_ms": duration_ms,
                "risk_score": risk_score,
                **kwargs
            })
        )
    
    def log_bounty(self, bounty_id: int, operation: str, status: str, **kwargs):
        """Log bounty operation with structured data"""
        self.logger.info(
            f"Bounty {bounty_id}: {operation} - {status}",
            extra=self._extra({
                "event": "bounty_operation",
                "bounty_id": bounty_id,
                "operation": operation,
                "status": status,
                **kwargs
            })
        )
    
    def log_signature(self, operation: str, status: str, duration_ms: float, **kwargs):
        """Log signature operation with structured data"""
        self.logger.info(
            f"Signature {operation}: {status}",
            extra=self._extra({
                "event": "signature_operation",
                "operation": operation,
                "status": status,
                "duration_ms": duration_ms,
                **kwargs
            })
        )
    
    def log_ai_request(self, model: str, status: str, duration_ms: float,
                      tokens: int, **kwargs):
        """Log AI model request with structured data"""
        self.logger.info(
            f"AI {model}: {status}",
            extra=self._extra({
                "event": "ai_request",
                "model": model,
                "status": status,
                "duration_ms": duration_ms,
                "tokens": tokens,
                **kwargs
            })
        )
    
    def log_db_operation(self, operation: str, status: str, duration_ms: float, **kwargs):
        """Log database operation with structured data"""
        self.logger.debug(
            f"DB {operation}: {status}",
            extra=self._extra({
                "event": "db_operation",
                "operation": operation,
                "status": status,
                "duration_ms": duration_ms,
                **kwargs
            })
        )
    
    def _extra(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Add standard fields to extra dict"""
        request_id = get_request_id()
        if request_id:
            kwargs["request_id"] = request_id
        return kwargs


# ============================================================================
# Formatters
# ============================================================================

class JSONFormatter(logging.Formatter):
    """JSON log formatter"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": "cyber-mercenary",
            "version": "3.0.0",
            "logger": record.name,
        }
        
        # Add request_id if available
        if hasattr(record, 'request_id') and record.request_id:
            log_data["request_id"] = record.request_id
        
        # Add extra fields
        if hasattr(record, 'request_id'):
            log_data["request_id"] = record.request_id
        
        # Add exception info
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra kwargs
        for key, value in record.__dict__.items():
            if key not in ('name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'lineno', 'funcName', 'created', 'msecs',
                          'relativeCreated', 'exc_info', 'exc_text', 'stack_info',
                          'request_id'):
                try:
                    log_data[key] = json.dumps(value, default=str)
                except (TypeError, ValueError):
                    log_data[key] = str(value)
        
        return json.dumps(log_data)


class PlainFormatter(logging.Formatter):
    """Plain text log formatter with structured fields"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as plain text"""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        request_id = getattr(record, 'request_id', '')
        
        if request_id:
            prefix = f"[{timestamp}] [{record.levelname:8}] [{request_id}] "
        else:
            prefix = f"[{timestamp}] [{record.levelname:8}] "
        
        return prefix + record.getMessage()


# ============================================================================
# Global Logger Instance
# ============================================================================

# Configure root logging
logging.setLogRecordFactory(StructuredLogRecord)

# Create global logger
_global_logger: Optional[StructuredLogger] = None


def get_logger(name: str = "cyber-mercenary", 
               log_file: Optional[str] = None,
               json_output: bool = True,
               level: str = DEFAULT_LOG_LEVEL) -> StructuredLogger:
    """Get or create a structured logger"""
    global _global_logger
    
    if _global_logger is None:
        _global_logger = StructuredLogger(name, log_file, json_output, level)
    return _global_logger


# ============================================================================
# Request Logging Middleware
# ============================================================================

class RequestLoggingMiddleware:
    """Middleware for logging HTTP requests"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
    
    async def log_request(self, request, response, duration_ms: float, 
                         request_id: str):
        """Log request details"""
        self.logger.log_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code if hasattr(response, 'status_code') else 200,
            duration_ms=duration_ms,
            request_id=request_id,
            client_ip=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown")
        )


# ============================================================================
# Log Rotation
# ============================================================================

class LogFile:
    """Log file manager with rotation"""
    
    def __init__(self, log_dir: str = "./logs", max_size_mb: int = 100, 
                 backup_count: int = 5):
        self.log_dir = Path(log_dir)
        self.max_size = max_size_mb * 1024 * 1024
        self.backup_count = backup_count
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def should_rotate(self, file_path: Path) -> bool:
        """Check if file should be rotated"""
        if not file_path.exists():
            return False
        return file_path.stat().st_size > self.max_size
    
    def rotate(self, file_path: Path):
        """Rotate log files"""
        for i in range(self.backup_count - 1, 0, -1):
            src = file_path.with_suffix(f".{i}.log")
            dst = file_path.with_suffix(f".{i+1}.log")
            if src.exists():
                src.rename(dst)
        
        # Rename current log
        if file_path.exists():
            file_path.rename(file_path.with_suffix(".1.log"))
        
        # Create new file
        file_path.touch()


# ============================================================================
# Setup Function
# ============================================================================

def setup_logging(
    name: str = "cyber-mercenary",
    log_file: Optional[str] = None,
    json_output: bool = True,
    level: str = DEFAULT_LOG_LEVEL,
    log_dir: str = "./logs"
) -> StructuredLogger:
    """Setup structured logging for the application"""
    
    # Create log directory if needed
    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Determine log file path
    if log_file is None and log_dir:
        log_file = f"{log_dir}/cyber-mercenary.log"
    
    # Create and configure logger
    logger = StructuredLogger(name, log_file, json_output, level)
    
    # Log startup message
    logger.info("Logging system initialized", 
               log_file=log_file or "stdout",
               log_level=level,
               json_output=json_output)
    
    return logger


# ============================================================================
# Usage Example
# ============================================================================

if __name__ == "__main__":
    # Setup logging
    logger = setup_logging(
        name="cyber-mercenary",
        log_file="./logs/app.log",
        json_output=True,
        level="DEBUG"
    )
    
    # Use in request context
    with request_context("req_abc123"):
        logger.info("Test message", extra_data={"key": "value"})
        logger.log_request("GET", "/health", 200, 15.5, "req_abc123")
        logger.log_scan("scan_abc", "0x123...", "completed", 1500.0, 0.75)
