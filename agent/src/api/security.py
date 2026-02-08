"""
Cyber-Mercenary Security Headers Middleware

Security headers implementation using Helmet-style approach for FastAPI.
Provides comprehensive HTTP security headers for all responses.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import re
from typing import Optional, List, Dict


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security headers to all HTTP responses.
    
    Implements defense-in-depth with comprehensive security headers
    to protect against common web application vulnerabilities.
    """
    
    # Default security headers
    DEFAULT_HEADERS = {
        # Prevent MIME type sniffing
        "X-Content-Type-Options": "nosniff",
        
        # Prevent clickjacking
        "X-Frame-Options": "DENY",
        
        # XSS protection (legacy but still useful)
        "X-XSS-Protection": "1; mode=block",
        
        # Referrer policy
        "Referrer-Policy": "strict-origin-when-cross-origin",
        
        # Feature policy / Permissions policy
        "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=()",
        
        # Cross-Origin policies
        "Cross-Origin-Opener-Policy": "same-origin",
        "Cross-Origin-Resource-Policy": "same-origin",
    }
    
    # Content Security Policy directives
    CSP_DIRECTIVES = {
        "default-src": ["'self'"],
        "script-src": ["'self'"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "img-src": ["'self'", "data:"],
        "connect-src": ["'self'"],
        "font-src": ["'self'"],
        "object-src": ["'none'"],
        "frame-ancestors": ["'none'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
        "upgrade-insecure-requests": [],
    }
    
    def __init__(
        self,
        app,
        csp: Optional[Dict[str, List[str]]] = None,
        hsts_max_age: int = 31536000,  # 1 year
        include_subdomains: bool = True,
        preload: bool = False,
        **kwargs
    ):
        """
        Initialize security headers middleware.
        
        Args:
            app: ASGI application
            csp: Custom CSP directives (overrides defaults)
            hsts_max_age: HSTS max-age in seconds
            include_subdomains: Include subdomains in HSTS
            preload: Allow HSTS preload
        """
        super().__init__(app)
        
        # Merge CSP directives
        self.csp_directives = {**self.CSP_DIRECTIVES}
        if csp:
            self.csp_directives.update(csp)
        
        # Build HSTS header
        hsts_value = f"max-age={hsts_max_age}"
        if include_subdomains:
            hsts_value += "; includeSubDomains"
        if preload:
            hsts_value += "; preload"
        
        self.hsts_header = hsts_value
        
        # Build CSP header value
        self.csp_header = self._build_csp()
        
    def _build_csp(self) -> str:
        """Build Content-Security-Policy header value"""
        directives = []
        for directive, sources in self.csp_directives.items():
            if sources:
                directives.append(f"{directive} {' '.join(sources)}")
            else:
                directives.append(directive)
        return "; ".join(directives)
    
    async def dispatch(self, request: Request, call_next):
        """Process request and add security headers to response"""
        
        # Get response from next middleware/handler
        response = await call_next(request)
        
        # Add security headers to response
        # Skip for streaming responses
        if hasattr(response, 'headers'):
            # Core security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=()"
            
            # CSP header
            response.headers["Content-Security-Policy"] = self.csp_header
            
            # HSTS (only for HTTPS requests)
            if request.url.scheme == "https":
                response.headers["Strict-Transport-Security"] = self.hsts_header
            
            # Cross-Origin policies
            response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
            response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
            
            # Remove server information (use del instead of pop for MutableHeaders)
            if "Server" in response.headers:
                del response.headers["Server"]
            if "X-Powered-By" in response.headers:
                del response.headers["X-Powered-By"]
        
        return response


class SecurityHeadersConfig:
    """
    Configuration holder for security headers.
    
    Provides easy configuration of security headers for different
    environments (development, staging, production).
    """
    
    ENV_CONFIGS = {
        "development": {
            "hsts_max_age": 0,  # No HSTS in dev
            "csp": {
                "default-src": ["'self'"],
                "script-src": ["'self'", "'unsafe-inline'"],
                "style-src": ["'self'", "'unsafe-inline'"],
                "connect-src": ["'self'", "ws://localhost:*", "http://localhost:*"],
            }
        },
        "staging": {
            "hsts_max_age": 604800,  # 1 week
            "csp": {
                "default-src": ["'self'"],
                "script-src": ["'self'"],
                "style-src": ["'self'"],
                "connect-src": ["'self'"],
            }
        },
        "production": {
            "hsts_max_age": 31536000,  # 1 year
            "csp": {
                "default-src": ["'self'"],
                "script-src": ["'self'"],
                "style-src": ["'self'"],
                "img-src": ["'self'", "data:"],
                "connect-src": ["'self'"],
                "font-src": ["'self'"],
                "object-src": ["'none'"],
                "frame-ancestors": ["'none'"],
                "base-uri": ["'self'"],
                "form-action": ["'self'"],
                "upgrade-insecure-requests": [],
            }
        }
    }
    
    @classmethod
    def get_config(cls, environment: str = "production") -> Dict:
        """Get security headers configuration for environment"""
        return cls.ENV_CONFIGS.get(environment, cls.ENV_CONFIGS["production"])
    
    @classmethod
    def create_middleware(cls, app, environment: str = "production"):
        """Create security middleware with environment config"""
        config = cls.get_config(environment)
        return SecurityHeadersMiddleware(
            app,
            hsts_max_age=config["hsts_max_age"],
            csp=config.get("csp")
        )


# Input Validation Utilities

def sanitize_input(value: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        value: Input value to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Limit length
    value = value[:max_length]
    
    # Remove null bytes
    value = value.replace("\x00", "")
    
    # HTML escape for output (for display contexts)
    value = (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )
    
    return value


def validate_ethereum_address(address: str) -> bool:
    """
    Validate Ethereum address format and checksum.
    
    Args:
        address: Ethereum address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not address:
        return False
    
    # Check format
    if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
        return False
    
    # Note: Full checksum validation requires web3 library
    # This is a basic format check
    return True


def validate_contract_address(address: str, chain_ids: List[int] = None) -> bool:
    """
    Validate contract address for supported chains.
    
    Args:
        address: Contract address to validate
        chain_ids: List of valid chain IDs
        
    Returns:
        True if valid, False otherwise
    """
    if not validate_ethereum_address(address):
        return False
    
    # For chain ID validation, you would need web3 connection
    # This is a placeholder for chain-specific validation
    return True


def sanitize_numeric_input(value: any, min_value: int = 0, max_value: int = None) -> int:
    """
    Sanitize and validate numeric input.
    
    Args:
        value: Input value
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Sanitized integer value
        
    Raises:
        ValueError: If value is out of range
    """
    try:
        num = int(value)
    except (TypeError, ValueError):
        raise ValueError("Invalid numeric value")
    
    if num < min_value:
        raise ValueError(f"Value must be >= {min_value}")
    
    if max_value is not None and num > max_value:
        raise ValueError(f"Value must be <= {max_value}")
    
    return num


def sanitize_ipfs_hash(hash: str) -> str:
    """
    Validate and sanitize IPFS hash.
    
    Args:
        hash: IPFS hash to validate
        
    Returns:
        Sanitized IPFS hash
        
    Raises:
        ValueError: If invalid format
    """
    if not hash:
        raise ValueError("IPFS hash is required")
    
    # Simplified validation - accepts Qm... hashes for testing
    # Full validation would check base58btc encoding
    if len(hash) < 46:
        raise ValueError("IPFS hash must be at least 46 characters")
    
    # Basic character validation (alphanumeric except ambiguous chars)
    if not re.match(r'^[1-9A-HJ-NP-Za-km-z]+$', hash):
        raise ValueError("Invalid IPFS hash format")
    
    return hash


# API Key Framework (Future Implementation)

class APIKeyValidator:
    """
    Validator for API key authentication.
    
    This is a placeholder for future API key authentication.
    Currently, the API is open with rate limiting only.
    """
    
    # API key format: cm_<32 random chars>
    KEY_FORMAT = re.compile(r'^cm_[a-f0-9]{32}$')
    
    @staticmethod
    def validate_format(key: str) -> bool:
        """Validate API key format"""
        if not key or len(key) != 35:
            return False
        return bool(APIKeyValidator.KEY_FORMAT.match(key))
    
    @staticmethod
    def validate_checksum(key: str) -> bool:
        """
        Validate API key checksum.
        
        Future implementation for key validation.
        """
        # Placeholder for checksum validation
        return True


class AuthorizationHeader:
    """
    Authorization header parser and validator.
    """
    
    SUPPORTED_SCHEMES = ["Bearer", "ApiKey"]
    
    @staticmethod
    def parse(auth_header: str) -> tuple:
        """
        Parse authorization header.
        
        Args:
            auth_header: Authorization header value
            
        Returns:
            Tuple of (scheme, credentials)
            
        Raises:
            ValueError: If header is invalid
        """
        if not auth_header:
            raise ValueError("Authorization header is required")
        
        parts = auth_header.split(" ", 1)
        if len(parts) != 2:
            raise ValueError("Invalid authorization header format")
        
        scheme, credentials = parts
        
        if scheme not in AuthorizationHeader.SUPPORTED_SCHEMES:
            raise ValueError(f"Unsupported authorization scheme: {scheme}")
        
        return scheme, credentials
