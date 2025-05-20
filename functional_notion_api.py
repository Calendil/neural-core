import requests
from os import getenv

NOTION_API_VERSION = "2022-06-28"
NOTION_API_KEY = getenv("NOTION_API_KEY")

ROOT_PAGE_ID = "1f855c99-70ec-80ca-bf5f-e44f51a2f511"

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_API_VERSION,
}

def notion_sync(**body):
    page_id = body.get("page_id")
    if page_id == "root":
        page_id = ROOT_PAGE_ID
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
    if page_id == "root":
        page_id = ROOT_PAGE_ID
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
    if page_id == "root":
        page_id = ROOT_PAGE_ID
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
    if page_id == "root":
        page_id = ROOT_PAGE_ID
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
    if root_page_id == "root":
        root_page_id = ROOT_PAGE_ID
    if not root_page_id:
        return {"error": "page_id is required."}

    blocks = []
    next_cursor = None

    while True:
        url = f"https://api.notion.com/v1/blocks/{root_page_id}/children"
        query_params = {}
        if next_cursor:
            query_params["start_cursor"] = next_cursor

        response = requests.get(url, headers=HEADERS, params=query_params)
        if response.status_code != 200:
            return {"error": response.text, "status_code": response.status_code}

        data = response.json()
        blocks.extend(data.get("results", []))
        next_cursor = data.get("next_cursor")

        if not next_cursor:
            break

    return {
        "total_blocks": len(blocks),
        "blocks": blocks
    }

def notion_get_page_metadata(**params):
    page_id = params.get("page_id")
    if page_id == "root":
        page_id = ROOT_PAGE_ID
    if not page_id:
        return {"error": "page_id is required."}

    url = f"https://api.notion.com/v1/pages/{page_id}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return {"error": response.text, "status_code": response.status_code}

    return response.json()

def notion_recursive_list_pages(page_id=None, visited=None):
    if visited is None:
        visited = set()

    if page_id is None or page_id == "root":
        page_id = ROOT_PAGE_ID

    if page_id in visited:
        return []

    visited.add(page_id)

    url_blocks = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response_blocks = requests.get(url_blocks, headers=HEADERS)
    if response_blocks.status_code != 200:
        return {"error": response_blocks.text, "status_code": response_blocks.status_code}

    blocks = response_blocks.json().get("results", [])
    pages = []

    for block in blocks:
        if block.get("type") == "child_page":
            child_id = block.get("id")
            # Fetch metadata of the child page
            url_page = f"https://api.notion.com/v1/pages/{child_id}"
            response_page = requests.get(url_page, headers=HEADERS)
            if response_page.status_code == 200:
                page_data = response_page.json()
                pages.append(page_data)
                # Recursively get pages under this child page
                pages.extend(notion_recursive_list_pages(child_id, visited))
            else:
                pages.append({"error": f"Failed to fetch metadata for page {child_id}"})

    return pages

def handle_response(response):
    if response.status_code not in [200, 201]:
        return {"error": response.text, "status_code": response.status_code}
    return {"status": "success", "detail": response.json()}
