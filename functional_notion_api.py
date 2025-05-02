import requests
from os import getenv

NOTION_API_VERSION = "2022-06-28"
NOTION_API_KEY = getenv("NOTION_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_API_VERSION,
}

def notion_sync(**body):
    page_id = body.get("page_id")
    content = body.get("content")
    if not page_id or not content:
        return {"error": "page_id and content are required."}
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
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
                                "content": content
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
    page_id = params.get("page_id")
    if not page_id:
        return {"error": "page_id is required."}
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.get(url, headers=HEADERS)
    return handle_response(response)

def notion_create(**body):
    parent_id = body.get("parent_id")
    title = body.get("title")
    if not parent_id or not title:
        return {"error": "parent_id and title are required."}
    url = "https://api.notion.com/v1/pages"
    data = {
        "parent": {
            "type": "page_id",
            "page_id": parent_id
        },
        "properties": {
            "title": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        }
    }
    response = requests.post(url, headers=HEADERS, json=data)
    return handle_response(response)

def notion_database_create(**body):
    parent_id = body.get("parent_id")
    title = body.get("title")
    properties = body.get("properties")
    if not parent_id or not title:
        return {"error": "parent_id and title are required."}
    if not properties:
        properties = {
            "Name": {
                "title": {}
            }
        }
    url = "https://api.notion.com/v1/databases"
    data = {
        "parent": {
            "type": "page_id",
            "page_id": parent_id
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": title
                }
            }
        ],
        "properties": properties
    }
    response = requests.post(url, headers=HEADERS, json=data)
    return handle_response(response)

def notion_database_query(**params):
    database_id = params.get("database_id")
    if not database_id:
        return {"error": "database_id is required."}
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    response = requests.post(url, headers=HEADERS)
    return handle_response(response)

def notion_database_update(**body):
    page_id = body.get("page_id")
    properties = body.get("properties")
    if not page_id or not properties:
        return {"error": "page_id and properties are required."}
    url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {
        "properties": properties
    }
    response = requests.patch(url, headers=HEADERS, json=data)
    return handle_response(response)

def notion_database_delete(**body):
    page_id = body.get("page_id")
    if not page_id:
        return {"error": "page_id is required."}
    url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {
        "archived": True
    }
    response = requests.patch(url, headers=HEADERS, json=data)
    return handle_response(response)

def handle_response(response):
    if response.status_code not in [200, 201]:
        return {"error": response.text, "status_code": response.status_code}
    return {"status": "success", "detail": response.json()}
