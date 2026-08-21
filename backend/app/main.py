from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging

from app.core.config import get_settings
from app.utils.settings import initialize_settings

from app.api import auth, user, medicine, batch, inventory, purchase, sales, invoice, sales_report, dashboard, supplier, settings, prescription, activity, permission, currency, expense, notification, expiry, report, backup
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security.log'),
        logging.StreamHandler()
    ]
)

app = FastAPI(
    title="Pharmacy Management System",
    description="""
    A comprehensive pharmacy management system with enterprise-grade security.
    
    ## Features
    * **Authentication** - Secure JWT-based auth with refresh tokens
    * **Medicine Management** - Track medicines, batches, and inventory
    * **Sales & Purchases** - Complete transaction management
    * **Reports** - Sales reports and dashboard analytics
    * **Security** - Rate limiting, request logging, and protection against common attacks
    
    ## Security
    * Rate limiting: 60 req/min globally, 5 login attempts/min
    * Protected against: XSS, CSRF, SQL injection, brute force attacks
    * All requests logged for audit trail
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "https://develop.d393xravvewyoy.amplifyapp.com",
    "http://54.179.188.174",
    "http://10.42.0.84"
]

initialize_settings()
app_settings = get_settings()

# Security Middleware (order matters - applied in reverse)
# 1. Request logging (first to log everything)
app.add_middleware(RequestLoggingMiddleware)

# 2. Security headers
app.add_middleware(SecurityHeadersMiddleware)

# 3. Rate limiting (limits from app settings)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=app_settings.rate_limit_per_minute,
    requests_per_hour=app_settings.rate_limit_per_hour,
    login_requests_per_minute=app_settings.login_rate_limit_per_minute,
    login_requests_per_hour=app_settings.login_rate_limit_per_hour,
)

# 4. CORS (after rate limiting to prevent abuse)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 5. Trusted host (validate Host header)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "54.179.188.174",
        "develop.d393xravvewyoy.amplifyapp.com",
        "testserver"
    ]
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(medicine.router)
app.include_router(batch.router)
app.include_router(inventory.router)
app.include_router(purchase.router)
app.include_router(sales.router)
app.include_router(invoice.router)
app.include_router(sales_report.router)
app.include_router(dashboard.router)
app.include_router(supplier.router)
app.include_router(settings.router)
app.include_router(prescription.router)
app.include_router(activity.router)
app.include_router(permission.router)
app.include_router(currency.router)
app.include_router(expense.router)
app.include_router(notification.router)
app.include_router(expiry.router)
app.include_router(report.router)
app.include_router(backup.router)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "app_name": app_settings.app_name,
        "env": app_settings.app_env
    }


# Serve the pharmacy frontend (self-contained deployment).
# API routes above take priority; everything else serves static files from frontent_pharmacy.
from fastapi.staticfiles import StaticFiles
from pathlib import Path

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontent_pharmacy"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
