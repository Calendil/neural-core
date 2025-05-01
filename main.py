from fastapi import FastAPI, HTTPException, Path, Body, Request
from pydantic import BaseModel
import os
from functional_notion_api import push_to_notion, fetch_blocks_from_notion
from fastapi.openapi.utils import get_openapi

# Initialize the FastAPI app
app = FastAPI(openapi_version="3.0.3")

@app.get("/")
def read_root():
    return {"message": "Bridge API is live."}

@app.get("/list-files")
def list_files():
    files = os.listdir(".")
    return {"files": files}

# --- ✅ Active: Notion sync endpoint (pure bridge) ---

class NotionSyncRequest(BaseModel):
    page_id: str
    content: str

@app.post("/bridge/notion-sync")
def notion_sync_bridge(request: NotionSyncRequest):
    return push_to_notion(request.page_id, request.content)

# --- ✅ Active: Notion fetch endpoint (pure bridge) ---

@app.get("/bridge/notion-fetch")
def notion_fetch_bridge(page_id: str):
    return fetch_blocks_from_notion(page_id)

# --- ✅ Custom OpenAPI schema with servers field ---
def custom_openapi():
    openapi_schema = get_openapi(
        title="GPT Beyond Neural Core API",
        version="0.1.0",
        description="Bridge API for Notion sync and fetch.",
        routes=app.routes,
    )
    openapi_schema["openapi"] = "3.0.3"  # 👈 Force OpenAPI 3.0.3
    openapi_schema["servers"] = [
        {"url": "https://neural-core.onrender.com"}
    ]
    return openapi_schema

# Override the default OpenAPI generator
app.openapi = custom_openapi
