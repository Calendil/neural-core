from fastapi import FastAPI, HTTPException, Request
import os
from fastapi.openapi.utils import get_openapi

app = FastAPI(openapi_version="3.1.0")

@app.get("/")
def read_root():
    return {"message": "Bridge API is live."}

@app.get("/list-files")
def list_files():
    files = os.listdir(".")
    return {"files": files}

@app.api_route("/bridge/notion/{action}", methods=["GET", "POST"])
async def notion_dynamic_bridge(action: str, request: Request):
    if not action.startswith("notion"):
        raise HTTPException(status_code=400, detail=f"Action '{action}' is not a Notion-related action.")

    from functional_notion_api import __dict__ as notion_funcs
    func_name = action.replace("-", "_")
    func = notion_funcs.get(func_name)

    if func is None:
        raise HTTPException(status_code=400, detail=f"No handler found for action '{action}' in functional_notion_api.")

    if request.method == "POST":
        try:
            body = await request.json()
        except Exception:
            body = {}
        return func(body=body)

    elif request.method == "GET":
        params = dict(request.query_params)
        return func(**params)

    else:
        raise HTTPException(status_code=405, detail="Method not allowed.")

def custom_openapi():
    openapi_schema = get_openapi(
        title="GPT Beyond Neural Core API",
        version="0.3.0",
        description="Universal Dynamic Bridge API for Notion integrations.",
        routes=app.routes,
    )
    openapi_schema["servers"] = [
        {"url": "https://neural-core.onrender.com"}
    ]
    return openapi_schema

app.openapi = custom_openapi
