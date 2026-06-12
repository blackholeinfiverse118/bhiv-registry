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


OPEN_PATHS = {"/", "/health", "/docs", "/redoc", "/api/v1/openapi.json"}


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