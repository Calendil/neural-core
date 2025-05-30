from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.utils import get_openapi

app = FastAPI(openapi_version="3.1.0")

@app.get("/")
def read_root():
    return {"message": "Bridge API is live."}

@app.api_route("/bridge/notion/{action}", methods=["GET", "POST"])
async def notion_dynamic_bridge(action: str, request: Request):
    from functional_notion_crud import __dict__ as notion_funcs

    # Smart prefix logic
    SMART_PREFIX = "notion_crud_"
    if action.startswith(SMART_PREFIX):
        stripped_action = action[len(SMART_PREFIX):]
    else:
        stripped_action = action

    func = notion_funcs.get(stripped_action)
    if not callable(func):
        raise HTTPException(
            status_code=400,
            detail=f"Handler '{stripped_action}' is not callable or not found."
        )

    if request.method == "POST":
        try:
            body = await request.json()
        except Exception:
            body = {}
        return await maybe_await(func, **body)

    elif request.method == "GET":
        params = dict(request.query_params)
        return await maybe_await(func, **params)

    raise HTTPException(status_code=405, detail="Method not allowed.")

async def maybe_await(func, *args, **kwargs):
    result = func(*args, **kwargs)
    if hasattr(result, "__await__"):
        return await result
    return result

def custom_openapi():
    openapi_schema = get_openapi(
        title="GPT Beyond Neural Core API",
        version="1.0.0",
        description="Bridge API for Notion page and block creation only.",
        routes=app.routes,
    )
    openapi_schema["servers"] = [
        {"url": "https://neural-core.onrender.com"}
    ]
    return openapi_schema

app.openapi = custom_openapi
