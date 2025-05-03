import requests
from os import getenv
from pydantic import BaseModel, ValidationError

NOTION_API_VERSION = "2022-06-28"
NOTION_API_KEY = getenv("NOTION_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_API_VERSION,
}

# ------------------- Pydantic Models -------------------

class NotionSyncRequest(BaseModel):
    page_id: str
    content: str

class NotionFetchRequest(BaseModel):
    page_id: str

class NotionCreateRequest(BaseModel):
    parent_id: str
    title: str

class NotionDatabaseCreateRequest(BaseModel):
    parent_id: str
    title: str
    properties: dict

class NotionDatabaseQueryRequest(BaseModel):
    database_id: str

class NotionDatabaseUpdateRequest(BaseModel):
    page_id: str
    properties: dict

class NotionDatabaseDeleteRequest(BaseModel):
    page_id: str

# ------------------- Notion Functions -------------------

def notion_sync(**body):
    expected_action = "notion_sync"
    if body.get("action_id") != expected_action:
        return {"error": f"Action mismatch: expected '{expected_action}', got '{body.get('action_id')}'"}

    try:
        validated = NotionSyncRequest(**body)
    except ValidationError as e:
        return {"error": e.errors()}

    url = f"https://api.notion.com/v1/blocks/{validated.page_id}/children"
    data = {
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": validated.content
                            }
                        }
                    ]
                }
            }
        ]
    }
    response = requests.patch(url, headers=HEADERS, json=data)
    return handle_response(response)

def notion_fetch(**params):
    expected_action = "notion_fetch"
    if params.get("action_id") != expected_action:
        return {"error": f"Action mismatch: expected '{expected_action}', got '{params.get('action_id')}'"}

    try:
        validated = NotionFetchRequest(**params)
    except ValidationError as e:
        return {"error": e.errors()}

    url = f"https://api.notion.com/v1/blocks/{validated.page_id}/children"
    response = requests.get(url, headers=HEADERS)
    return handle_response(response)

def notion_create(**body):
    expected_action = "notion_create"
    if body.get("action_id") != expected_action:
        return {"error": f"Action mismatch: expected '{expected_action}', got '{body.get('action_id')}'"}

    try:
        validated = NotionCreateRequest(**body)
    except ValidationError as e:
        return {"error": e.errors()}

    url = "https://api.notion.com/v1/pages"
    data = {
        "parent": {
            "type": "page_id",
            "page_id": validated.parent_id
        },
        "properties": {
            "title": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": validated.title
                        }
                    }
                ]
            }
        }
    }
    response = requests.post(url, headers=HEADERS, json=data)
    return handle_response(response)

def notion_database_create(**body):
    expected_action = "notion_database_create"
    if body.get("action_id") != expected_action:
        return {"error": f"Action mismatch: expected '{expected_action}', got '{body.get('action_id')}'"}

    try:
        validated = NotionDatabaseCreateRequest(**body)
    except ValidationError as e:
        return {"error": e.errors()}

    url = "https://api.notion.com/v1/databases"
    data = {
        "parent": {
            "type": "page_id",
            "page_id": validated.parent_id
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": validated.title
                }
            }
        ],
        "properties": validated.properties or {"Name": {"title": {}}}
    }
    response = requests.post(url, headers=HEADERS, json=data)
    return handle_response(response)

def notion_database_query(**params):
    expected_action = "notion_database_query"
    if params.get("action_id") != expected_action:
        return {"error": f"Action mismatch: expected '{expected_action}', got '{params.get('action_id')}'"}

    try:
        validated = NotionDatabaseQueryRequest(**params)
    except ValidationError as e:
        return {"error": e.errors()}

    url = f"https://api.notion.com/v1/databases/{validated.database_id}/query"
    response = requests.post(url, headers=HEADERS)
    return handle_response(response)

def notion_database_update(**body):
    expected_action = "notion_database_update"
    if body.get("action_id") != expected_action:
        return {"error": f"Action mismatch: expected '{expected_action}', got '{body.get('action_id')}'"}

    try:
        validated = NotionDatabaseUpdateRequest(**body)
    except ValidationError as e:
        return {"error": e.errors()}

    url = f"https://api.notion.com/v1/pages/{validated.page_id}"
    data = {
        "properties": validated.properties
    }
    response = requests.patch(url, headers=HEADERS, json=data)
    return handle_response(response)

def notion_database_delete(**body):
    expected_action = "notion_database_delete"
    if body.get("action_id") != expected_action:
        return {"error": f"Action mismatch: expected '{expected_action}', got '{body.get('action_id')}'"}

    try:
        validated = NotionDatabaseDeleteRequest(**body)
    except ValidationError as e:
        return {"error": e.errors()}

    url = f"https://api.notion.com/v1/pages/{validated.page_id}"
    data = {
        "archived": True
    }
    response = requests.patch(url, headers=HEADERS, json=data)
    return handle_response(response)

# ------------------- Response Handler -------------------

def handle_response(response):
    if response.status_code not in [200, 201]:
        return {"error": response.text, "status_code": response.status_code}
    return {"status": "success", "detail": response.json()}
