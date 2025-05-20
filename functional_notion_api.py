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

MAX_RECURSION_DEPTH = 5

def notion_recursive_list_pages(page_id=None, visited=None, depth=0):
    if visited is None:
        visited = set()

    if page_id is None or page_id == "root":
        page_id = ROOT_PAGE_ID

    if depth > MAX_RECURSION_DEPTH:
        return [{"error": "Max recursion depth reached"}]

    if page_id in visited:
        return []

    visited.add(page_id)

    url_blocks = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response_blocks = requests.get(url_blocks, headers=HEADERS)
    if response_blocks.status_code != 200:
        return [{"error": response_blocks.text, "status_code": response_blocks.status_code}]

    blocks = response_blocks.json().get("results", [])
    pages = []

    for block in blocks:
        if block.get("type") == "child_page":
            child_id = block.get("id")
            url_page = f"https://api.notion.com/v1/pages/{child_id}"
            response_page = requests.get(url_page, headers=HEADERS)
            if response_page.status_code == 200:
                page_data = response_page.json()
                pages.append(page_data)
                pages.extend(notion_recursive_list_pages(child_id, visited, depth + 1))
            else:
                pages.append({"error": f"Failed to fetch metadata for page {child_id}"})

    return pages

# Include all other existing functions below unchanged...

def notion_sync(**body):
    # (existing code unchanged)
    ...

def notion_fetch(**params):
    # (existing code unchanged)
    ...

def notion_create(**body):
    # (existing code unchanged)
    ...

def notion_update(**body):
    # (existing code unchanged)
    ...

def notion_delete(**body):
    # (existing code unchanged)
    ...

def notion_list_child_pages(**params):
    # (existing code unchanged)
    ...

def notion_get_page_metadata(**params):
    # (existing code unchanged)
    ...

def handle_response(response):
    if response.status_code not in [200, 201]:
        return {"error": response.text, "status_code": response.status_code}
    return {"status": "success", "detail": response.json()}
