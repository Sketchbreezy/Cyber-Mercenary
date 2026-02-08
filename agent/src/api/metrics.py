"""
Prometheus Metrics for Cyber-Mercenary API

Provides comprehensive metrics for monitoring:
- HTTP request count and latency
- Scan operations (success/fail/count)
- Bounty operations (created/claimed/disputed)
- Signature operations
- Database operation latency
- AI model response times
"""

import time
from typing import Optional
from contextlib import contextmanager
from functools import wraps
import threading

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
    multiprocess,
)

# Create a separate registry for this module
registry = CollectorRegistry()

# ============================================================================
# HTTP Request Metrics
# ============================================================================

# Total HTTP requests by method and endpoint
http_requests_total = Counter(
    'cybermercenary_http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

# HTTP request duration histogram
http_request_duration_seconds = Histogram(
    'cybermercenary_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0],
    registry=registry
)

# HTTP requests in progress
http_requests_in_progress = Gauge(
    'cybermercenary_http_requests_in_progress',
    'Number of HTTP requests currently being processed',
    ['method', 'endpoint'],
    registry=registry
)

# ============================================================================
# Scan Operation Metrics
# ============================================================================

# Scan operations counter
scan_operations_total = Counter(
    'cybermercenary_scan_operations_total',
    'Total number of scan operations',
    ['status', 'scan_type'],
    registry=registry
)

# Scan duration histogram
scan_duration_seconds = Histogram(
    'cybermercenary_scan_duration_seconds',
    'Duration of scan operations in seconds',
    ['scan_type'],
    buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0],
    registry=registry
)

# Scan risk score gauge
scan_risk_score = Gauge(
    'cybermercenary_scan_risk_score',
    'Risk score of the last scan',
    ['contract_address'],
    registry=registry
)

# Vulnerability count per scan
scan_vulnerabilities_count = Histogram(
    'cybermercenary_scan_vulnerabilities_count',
    'Number of vulnerabilities found per scan',
    ['severity'],
    buckets=[0, 1, 2, 5, 10, 20, 50],
    registry=registry
)

# ============================================================================
# Bounty Operation Metrics
# ============================================================================

# Bounty operations counter
bounty_operations_total = Counter(
    'cybermercenary_bounty_operations_total',
    'Total number of bounty operations',
    ['operation', 'status'],
    registry=registry
)

# Bounty amount in ETH
bounty_amount_eth = Histogram(
    'cybermercenary_bounty_amount_eth',
    'Bounty amounts in ETH',
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0, 500.0],
    registry=registry
)

# Active bounties gauge
bounties_active = Gauge(
    'cybermercenary_bounties_active',
    'Number of currently active bounties',
    registry=registry
)

# Disputed bounties gauge
bounties_disputed = Gauge(
    'cybermercenary_bounties_disputed',
    'Number of currently disputed bounties',
    registry=registry
)

# ============================================================================
# Signature Operation Metrics
# ============================================================================

# Signature operations counter
signature_operations_total = Counter(
    'cybermercenary_signature_operations_total',
    'Total number of signature operations',
    ['operation', 'status'],
    registry=registry
)

# Signature duration histogram
signature_duration_seconds = Histogram(
    'cybermercenary_signature_duration_seconds',
    'Duration of signature operations in seconds',
    ['operation'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
    registry=registry
)

# ============================================================================
# Database Operation Metrics
# ============================================================================

# Database operations counter
db_operations_total = Counter(
    'cybermercenary_db_operations_total',
    'Total number of database operations',
    ['operation', 'status'],
    registry=registry
)

# Database operation duration histogram
db_operation_duration_seconds = Histogram(
    'cybermercenary_db_operation_duration_seconds',
    'Duration of database operations in seconds',
    ['operation'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0],
    registry=registry
)

# Database connection pool
db_connections_active = Gauge(
    'cybermercenary_db_connections_active',
    'Number of active database connections',
    registry=registry
)

# ============================================================================
# AI Model Response Metrics
# ============================================================================

# AI model request counter
ai_requests_total = Counter(
    'cybermercenary_ai_requests_total',
    'Total number of AI model requests',
    ['model', 'status'],
    registry=registry
)

# AI model response duration histogram
ai_request_duration_seconds = Histogram(
    'cybermercenary_ai_request_duration_seconds',
    'Duration of AI model requests in seconds',
    ['model'],
    buckets=[1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0],
    registry=registry
)

# AI model tokens used
ai_tokens_used = Counter(
    'cybermercenary_ai_tokens_used',
    'Total number of tokens used in AI requests',
    ['model', 'type'],
    registry=registry
)

# AI model response length
ai_response_length = Histogram(
    'cybermercenary_ai_response_length',
    'Length of AI model responses in characters',
    ['model'],
    buckets=[100, 500, 1000, 2000, 5000, 10000, 20000],
    registry=registry
)

# ============================================================================
# System Metrics
# ============================================================================

# Python interpreter info
python_info = Gauge(
    'cybermercenary_python_info',
    'Python version info',
    ['version', 'platform'],
    registry=registry
)

# Service readiness
service_ready = Gauge(
    'cybermercenary_service_ready',
    'Whether a service is ready (1=yes, 0=no)',
    ['service'],
    registry=registry
)

# Uptime counter
process_start_time_seconds = Gauge(
    'cybermercenary_process_start_time_seconds',
    'Process start time in seconds since epoch',
    registry=registry
)

# Memory usage (if available)
process_memory_bytes = Gauge(
    'cybermercenary_process_memory_bytes',
    'Process memory usage in bytes',
    ['type'],
    registry=registry
)


# ============================================================================
# Metric Collection Utilities
# ============================================================================

class MetricsCollector:
    """Helper class for collecting metrics"""
    
    def __init__(self):
        self._start_time = {}
    
    def start_request(self, method: str, endpoint: str):
        """Mark a request as started"""
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
        self._start_time[f"{method}:{endpoint}"] = time.time()
    
    def end_request(self, method: str, endpoint: str, status_code: int):
        """Mark a request as completed"""
        key = f"{method}:{endpoint}"
        if key in self._start_time:
            duration = time.time() - self._start_time[key]
            http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
            del self._start_time[key]
        
        http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()
        http_requests_total.labels(method=method, endpoint=endpoint, status_code=str(status_code)).inc()
    
    def record_scan(self, status: str, scan_type: str, duration: float, 
                   risk_score: float = 0, vulnerability_count: int = 0):
        """Record scan operation metrics"""
        scan_operations_total.labels(status=status, scan_type=scan_type).inc()
        scan_duration_seconds.labels(scan_type=scan_type).observe(duration)
        
        if vulnerability_count > 0:
            scan_vulnerabilities_count.labels(severity="with_vulns").observe(vulnerability_count)
        else:
            scan_vulnerabilities_count.labels(severity="clean").observe(vulnerability_count)
    
    def record_bounty(self, operation: str, status: str, amount_eth: float = 0):
        """Record bounty operation metrics"""
        bounty_operations_total.labels(operation=operation, status=status).inc()
        if amount_eth > 0:
            bounty_amount_eth.observe(amount_eth)
    
    def record_signature(self, operation: str, status: str, duration: float):
        """Record signature operation metrics"""
        signature_operations_total.labels(operation=operation, status=status).inc()
        signature_duration_seconds.labels(operation=operation).observe(duration)
    
    def record_db_operation(self, operation: str, status: str, duration: float):
        """Record database operation metrics"""
        db_operations_total.labels(operation=operation, status=status).inc()
        db_operation_duration_seconds.labels(operation=operation).observe(duration)
    
    def record_ai_request(self, model: str, status: str, duration: float,
                          prompt_tokens: int = 0, completion_tokens: int = 0,
                          response_length: int = 0):
        """Record AI model request metrics"""
        ai_requests_total.labels(model=model, status=status).inc()
        ai_request_duration_seconds.labels(model=model).observe(duration)
        
        if prompt_tokens > 0:
            ai_tokens_used.labels(model=model, type="prompt").inc(prompt_tokens)
        if completion_tokens > 0:
            ai_tokens_used.labels(model=model, type="completion").inc(completion_tokens)
        
        if response_length > 0:
            ai_response_length.labels(model=model).observe(response_length)


# Global metrics collector instance
metrics_collector = MetricsCollector()


# ============================================================================
# Decorators for Easy Metric Collection
# ============================================================================

def track_http_request(method: str, endpoint: str):
    """Decorator to track HTTP request metrics"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            metrics_collector.start_request(method, endpoint)
            try:
                result = await func(*args, **kwargs)
                status_code = getattr(result, 'status_code', 200) if hasattr(result, 'status_code') else 200
                metrics_collector.end_request(method, endpoint, status_code)
                return result
            except Exception as e:
                status_code = getattr(e, 'status_code', 500) if hasattr(e, 'status_code') else 500
                metrics_collector.end_request(method, endpoint, status_code)
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            metrics_collector.start_request(method, endpoint)
            try:
                result = func(*args, **kwargs)
                status_code = 200
                metrics_collector.end_request(method, endpoint, status_code)
                return result
            except Exception as e:
                status_code = getattr(e, 'status_code', 500) if hasattr(e, 'status_code') else 500
                metrics_collector.end_request(method, endpoint, status_code)
                raise
        
        # Support both async and sync functions
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


@contextmanager
def track_db_operation(operation: str):
    """Context manager to track database operation metrics"""
    start_time = time.time()
    try:
        yield
        duration = time.time() - start_time
        metrics_collector.record_db_operation(operation, "success", duration)
    except Exception as e:
        duration = time.time() - start_time
        metrics_collector.record_db_operation(operation, "error", duration)
        raise


@contextmanager
def track_scan_operation(scan_type: str):
    """Context manager to track scan operation metrics"""
    start_time = time.time()
    try:
        yield
        duration = time.time() - start_time
        metrics_collector.record_scan("success", scan_type, duration)
    except Exception as e:
        duration = time.time() - start_time
        metrics_collector.record_scan("error", scan_type, duration)
        raise


@contextmanager
def track_bounty_operation(operation: str):
    """Context manager to track bounty operation metrics"""
    start_time = time.time()
    try:
        yield
        duration = time.time() - start_time
        metrics_collector.record_bounty(operation, "success")
    except Exception as e:
        duration = time.time() - start_time
        metrics_collector.record_bounty(operation, "error")
        raise


@contextmanager
def track_signature_operation(operation: str):
    """Context manager to track signature operation metrics"""
    start_time = time.time()
    try:
        yield
        duration = time.time() - start_time
        metrics_collector.record_signature(operation, "success", duration)
    except Exception as e:
        duration = time.time() - start_time
        metrics_collector.record_signature(operation, "error", duration)
        raise


@contextmanager
def track_ai_request(model: str):
    """Context manager to track AI model request metrics"""
    start_time = time.time()
    try:
        yield
        duration = time.time() - start_time
        metrics_collector.record_ai_request(model, "success", duration)
    except Exception as e:
        duration = time.time() - start_time
        metrics_collector.record_ai_request(model, "error", duration)
        raise


# ============================================================================
# Metrics Endpoint
# ============================================================================

def get_metrics() -> bytes:
    """Generate Prometheus metrics in text format"""
    return generate_latest(registry)


def get_metrics_content_type() -> str:
    """Get the content type for Prometheus metrics"""
    return CONTENT_TYPE_LATEST


def init_metrics(process_start_time: float):
    """Initialize system metrics"""
    process_start_time_seconds.set(process_start_time)
    
    # Set Python info
    import sys
    python_info.labels(
        version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        platform=sys.platform
    ).set(1)


# Initialize with current time
init_metrics(time.time())
