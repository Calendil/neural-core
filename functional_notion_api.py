import requests
from os import getenv

NOTION_API_VERSION = "2022-06-28"
NOTION_API_KEY = getenv("NOTION_API_KEY")

ROOT_PAGE_ID = "1f855c9970ec80cabf5fe44f51a2f511"

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
    if parent_id == "root":
        parent_id = ROOT_PAGE_ID
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

def notion_update(**body):
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

def notion_delete(**body):
    page_id = body.get("page_id")
    if not page_id:
        return {"error": "page_id is required."}

    url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {
        "archived": True
    }
    response = requests.patch(url, headers=HEADERS, json=data)
    return handle_response(response)

def notion_list_child_pages(**params):
    root_page_id = params.get("page_id")
    if not root_page_id:
        return {"error": "page_id is required."}

    url = f"https://api.notion.com/v1/blocks/{root_page_id}/children"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return {"error": response.text, "status_code": response.status_code}

    blocks = response.json().get("results", [])
    pages = []
    for block in blocks:
        if block.get("type") == "child_page":
            pages.append({
                "id": block.get("id"),
                "title": block.get("child_page", {}).get("title")
            })

    return {"child_pages": pages}

def handle_response(response):
    if response.status_code not in [200, 201]:
        return {"error": response.text, "status_code": response.status_code}
    return {"status": "success", "detail": response.json()}
