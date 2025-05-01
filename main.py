from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import os
from functional_notion_api import (
    push_to_notion,
    fetch_blocks_from_notion,
    create_page_in_notion  # Make sure this exists if you plan to create pages
)
from fastapi.openapi.utils import get_openapi

# Initialize the FastAPI app
app = FastAPI(openapi_version="3.1.0")

@app.get("/")
def read_root():
    return {"message": "Bridge API is live."}

@app.get("/list-files")
def list_files():
    files = os.listdir(".")
    return {"files": files}

# --- ✅ Dynamic Notion bridge route ---
@app.api_route("/bridge/notion/{action}", methods=["GET", "POST"])
async def notion_dynamic_bridge(action: str, request: Request):
    if action == "sync":
        body = await request.json()
        page_id = body.get("page_id")
        content = body.get("content")
        if not page_id or not content:
            raise HTTPException(status_code=400, detail="page_id and content are required.")
        return push_to_notion(page_id, content)

    elif action == "fetch":
        page_id = request.query_params.get("page_id")
        if not page_id:
            raise HTTPException(status_code=400, detail="page_id is required.")
        return fetch_blocks_from_notion(page_id)

    elif action == "create":
        body = await request.json()
        parent_id = body.get("parent_id")
        title = body.get("title")
        if not parent_id or not title:
            raise HTTPException(status_code=400, detail="parent_id and title are required.")
        return create_page_in_notion(parent_id, title)

    else:
        raise HTTPException(status_code=404, detail=f"Unsupported action: {action}")

# --- ✅ Custom OpenAPI schema with servers field ---
def custom_openapi():
    openapi_schema = get_openapi(
        title="GPT Beyond Neural Core API",
        version="0.2.0",
        description="Dynamic Bridge API for Notion integrations.",
        routes=app.routes,
    )
    openapi_schema["servers"] = [
        {"url": "https://neural-core.onrender.com"}
    ]
    return openapi_schema

app.openapi = custom_openapi
