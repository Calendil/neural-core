# main.py

from fastapi import FastAPI, Request
import httpx

app = FastAPI()

FUNCTIONAL_API_ROUTES = {
    "functional-memory-db": "http://localhost:8001",
}

@app.api_route("/{functional_api}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def forward_request(functional_api: str, path: str, request: Request):
    if functional_api not in FUNCTIONAL_API_ROUTES:
        return {"error": f"Unknown functional API: {functional_api}"}

    target_url = f"{FUNCTIONAL_API_ROUTES[functional_api]}/{path}"
    method = request.method
    headers = dict(request.headers)
    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.request(
                method,
                target_url,
                headers=headers,
                content=body
            )
        return response.json()
    except httpx.RequestError as exc:
        return {
            "error": "Functional API unreachable",
            "functional_api": functional_api,
            "details": str(exc)
        }
    except Exception as e:
        return {
            "error": "Unexpected bridge error",
            "details": str(e)
        }

@app.get("/")
def read_root():
    return {"message": "Bridge API is live."}
