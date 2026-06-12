"""
BHIV Registry — API Key Authentication + Audit Logging Middleware

Every request to /api/v1/* must include a valid X-API-Key header.
/health and / remain open for monitoring.

Every request (successful or not) is logged to audit_logs
with the resolved owner name, for ecosystem consumption evidence.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from datetime import datetime, timezone
from sqlalchemy import select

from app.db.base import AsyncSessionLocal
from app.models.registry import ApiKey, AuditLog
from collections import defaultdict
from datetime import timedelta


OPEN_PATHS = {"/", "/health", "/docs", "/redoc", "/api/v1/openapi.json"}

# Simple in-memory rate limiter: max requests per window per API key
RATE_LIMIT_MAX = 100
RATE_LIMIT_WINDOW_SECONDS = 60
_request_counts = defaultdict(list)

class ApiKeyAuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Open paths bypass auth entirely, no audit log
        if path in OPEN_PATHS or path.startswith("/docs") or path.startswith("/redoc"):
            return await call_next(request)

        api_key_header = request.headers.get("x-api-key")
        owner_name = None
        status_code = 401

        async with AsyncSessionLocal() as db:
            if api_key_header:
                result = await db.execute(
                    select(ApiKey).where(
                        ApiKey.key == api_key_header,
                        ApiKey.is_active == True
                    )
                )
                key_record = result.scalar_one_or_none()

                if key_record:
                    owner_name = key_record.owner_name
                    key_record.last_used_at = datetime.now(timezone.utc)
                    await db.commit()

            if not owner_name:
                # Log the failed attempt
                log = AuditLog(
                    method=request.method,
                    path=path,
                    api_key_owner=None,
                    status_code=401,
                    client_host=request.client.host if request.client else None,
                )
                db.add(log)
                await db.commit()

                return JSONResponse(
                    status_code=401,
                    content={"detail": "Missing or invalid API key. Provide a valid X-API-Key header."}
                )

        # Rate limiting check
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=RATE_LIMIT_WINDOW_SECONDS)
        _request_counts[owner_name] = [
            t for t in _request_counts[owner_name] if t > window_start
        ]

        if len(_request_counts[owner_name]) >= RATE_LIMIT_MAX:
            async with AsyncSessionLocal() as db:
                log = AuditLog(
                    method=request.method,
                    path=path,
                    api_key_owner=owner_name,
                    status_code=429,
                    client_host=request.client.host if request.client else None,
                )
                db.add(log)
                await db.commit()

            return JSONResponse(
                status_code=429,
                content={"detail": f"Rate limit exceeded: max {RATE_LIMIT_MAX} requests per {RATE_LIMIT_WINDOW_SECONDS} seconds."}
            )

        _request_counts[owner_name].append(now)

        # Valid key — proceed with request
        response = await call_next(request)

        # Log the successful (or downstream-failed) request
        async with AsyncSessionLocal() as db:
            log = AuditLog(
                method=request.method,
                path=path,
                api_key_owner=owner_name,
                status_code=response.status_code,
                client_host=request.client.host if request.client else None,
            )
            db.add(log)
            await db.commit()

        return response