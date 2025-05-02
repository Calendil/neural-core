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

class NotionDatabaseCreateRequest(BaseModel):
    parent_id: str
    title: str
    properties: dict

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

# Leave the rest of your existing functions unchanged for now.
# Repeat similar structure as needed in other functions if desired.

def handle_response(response):
    if response.status_code not in [200, 201]:
        return {"error": response.text, "status_code": response.status_code}
    return {"status": "success", "detail": response.json()}
