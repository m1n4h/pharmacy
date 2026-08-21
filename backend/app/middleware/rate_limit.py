from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware with configurable limits per endpoint
    """
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000,
                 login_requests_per_minute: int = 5, login_requests_per_hour: int = 20):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Store: {ip: [(timestamp, endpoint), ...]}
        self.request_history: Dict[str, list] = defaultdict(list)
        
        # Stricter limits for sensitive endpoints (from app settings)
        self.endpoint_limits = {
            "/auth/login": (login_requests_per_minute, login_requests_per_hour),
            "/auth/refresh": (10, 100),
            "/auth/logout": (10, 100),
        }
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _clean_old_requests(self, ip: str, now: datetime):
        """Remove requests older than 1 hour"""
        cutoff = now - timedelta(hours=1)
        self.request_history[ip] = [
            (ts, endpoint) for ts, endpoint in self.request_history[ip]
            if ts > cutoff
        ]
    
    def _check_rate_limit(self, ip: str, endpoint: str, now: datetime) -> Tuple[bool, str]:
        """Check if request exceeds rate limits"""
        self._clean_old_requests(ip, now)
        
        # Get limits for this endpoint
        if endpoint in self.endpoint_limits:
            per_minute, per_hour = self.endpoint_limits[endpoint]
        else:
            per_minute, per_hour = self.requests_per_minute, self.requests_per_hour
        
        # Count requests in last minute and hour
        minute_ago = now - timedelta(minutes=1)
        requests_last_minute = sum(
            1 for ts, ep in self.request_history[ip]
            if ts > minute_ago and ep == endpoint
        )
        requests_last_hour = sum(
            1 for ts, ep in self.request_history[ip]
            if ep == endpoint
        )
        
        if requests_last_minute >= per_minute:
            return False, f"Rate limit exceeded: {per_minute} requests per minute"
        
        if requests_last_hour >= per_hour:
            return False, f"Rate limit exceeded: {per_hour} requests per hour"
        
        return True, ""
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and static frontend files
        path = request.url.path
        last_segment = path.rsplit("/", 1)[-1]
        if path in ("/", "/health", "/docs", "/redoc", "/openapi.json") or "." in last_segment:
            return await call_next(request)
        
        ip = self._get_client_ip(request)
        endpoint = request.url.path
        now = datetime.utcnow()
        
        # Check rate limit
        allowed, message = self._check_rate_limit(ip, endpoint, now)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for IP {ip} on {endpoint}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "success": False,
                    "message": message,
                    "error": "RATE_LIMIT_EXCEEDED"
                }
            )
        
        # Record this request
        self.request_history[ip].append((now, endpoint))
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - sum(
                1 for ts, ep in self.request_history[ip]
                if ts > now - timedelta(minutes=1) and ep == endpoint
            )
        )
        
        return response
