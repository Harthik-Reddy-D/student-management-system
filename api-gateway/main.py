import os
from urllib.parse import quote
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
load_dotenv()
AUTH_URL = os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:8001").rstrip("/")
STUDENT_URL = os.getenv("STUDENT_SERVICE_URL", "http://127.0.0.1:8002").rstrip("/")
COURSE_URL = os.getenv("COURSE_SERVICE_URL", "http://127.0.0.1:8003").rstrip("/")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
TIMEOUT = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "8"))
app = FastAPI(title="Student Management API Gateway", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[FRONTEND_ORIGIN], allow_credentials=True, allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], allow_headers=["Authorization", "Content-Type", "Accept"])

@app.get("/health")
def health(): return {"status":"ok", "service":"api-gateway"}

def service_for(path: str):
    if path == "auth" or path.startswith("auth/"): return AUTH_URL
    if path == "students" or path.startswith("students/"): return STUDENT_URL
    if path == "courses" or path.startswith("courses/"): return COURSE_URL
    return None

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy(path: str, request: Request):
    service = service_for(path)
    if service is None:
        return JSONResponse(status_code=404, content={"error":"not_found", "detail":"Gateway route not found"})
    # Validate protected requests through auth-service. Registration and login are public.
    public = path in ("auth/register", "auth/login")
    auth_header = request.headers.get("authorization")
    if not public:
        if not auth_header or not auth_header.lower().startswith("bearer "):
            return JSONResponse(status_code=401, content={"error":"unauthorized", "detail":"Bearer token required"})
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                check = await client.get(f"{AUTH_URL}/auth/me", headers={"Authorization": auth_header})
            if check.status_code == 401:
                return JSONResponse(status_code=401, content={"error":"unauthorized", "detail":"Invalid or expired token"})
            if check.status_code >= 500:
                return JSONResponse(status_code=503, content={"error":"service_unavailable", "detail":"Authentication service failed"})
        except httpx.TimeoutException:
            return JSONResponse(status_code=504, content={"error":"gateway_timeout", "detail":"Authentication service timed out"})
        except httpx.RequestError:
            return JSONResponse(status_code=503, content={"error":"service_unavailable", "detail":"Authentication service is unavailable"})
    query = str(request.url.query)
    target = f"{service}/{path}" + (f"?{query}" if query else "")
    headers = {}
    for key in ("authorization", "content-type", "accept"):
        if key in request.headers: headers[key] = request.headers[key]
    body = await request.body()
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            upstream = await client.request(request.method, target, headers=headers, content=body)
    except httpx.TimeoutException:
        return JSONResponse(status_code=504, content={"error":"gateway_timeout", "detail":"Upstream service timed out"})
    except httpx.RequestError:
        return JSONResponse(status_code=503, content={"error":"service_unavailable", "detail":"Upstream service is unavailable"})
    content_type = upstream.headers.get("content-type", "application/json")
    excluded = {"content-encoding", "transfer-encoding", "connection", "content-length"}
    response_headers = {k:v for k,v in upstream.headers.items() if k.lower() not in excluded}
    return Response(content=upstream.content, status_code=upstream.status_code, headers=response_headers, media_type=None)
