# functional_notion_api.py

import requests
from os import getenv

NOTION_API_VERSION = "2022-06-28"
NOTION_API_KEY = getenv("NOTION_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_API_VERSION,
}

# --- Existing functions ---

def notion_sync(page_id: str, content: str):
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


def notion_fetch(page_id: str):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.get(url, headers=HEADERS)
    return handle_response(response)


def notion_create(parent_id: str, title: str):
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

# --- New database CRUD functions ---

def notion_database_create(parent_id: str, title: str, properties: dict):
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


def notion_database_query(database_id: str):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    response = requests.post(url, headers=HEADERS)
    return handle_response(response)


def notion_database_update(page_id: str, properties: dict):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {
        "properties": properties
    }
    response = requests.patch(url, headers=HEADERS, json=data)
    return handle_response(response)


def notion_database_delete(page_id: str):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {
        "archived": True
    }
    response = requests.patch(url, headers=HEADERS, json=data)
    return handle_response(response)

# --- Helper ---

def handle_response(response):
    if response.status_code not in [200, 201]:
        return {"error": response.text, "status_code": response.status_code}
    return {"status": "success", "detail": response.json()}
