import requests
from os import getenv
import re

NOTION_API_VERSION = "2022-06-28"
NOTION_API_KEY = getenv("NOTION_API_KEY")

ROOT_PAGE_ID = "1f855c99-70ec-80ca-bf5f-e44f51a2f511"

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_API_VERSION,
}

def rich_text_block(content):
    return [{"type": "text", "text": {"content": content}}]

def parse_markdown_to_notion_blocks(text):
    lines = text.splitlines()
    blocks = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i].rstrip()

        if re.match(r"^# (.+)", line):
            content = re.match(r"^# (.+)", line).group(1)
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": rich_text_block(content)
                }
            })
            i += 1
            continue

        if re.match(r"^## (.+)", line):
            content = re.match(r"^## (.+)", line).group(1)
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": rich_text_block(content)
                }
            })
            i += 1
            continue

        if re.match(r"^### (.+)", line):
            content = re.match(r"^### (.+)", line).group(1)
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": rich_text_block(content)
                }
            })
            i += 1
            continue

        if re.match(r"^\d+\. (.+)", line):
            items = []
            while i < n and re.match(r"^\d+\. (.+)", lines[i].rstrip()):
                content = re.match(r"^\d+\. (.+)", lines[i].rstrip()).group(1)
                items.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": rich_text_block(content)
                    }
                })
                i += 1
            blocks.extend(items)
            continue

        if re.match(r"^[-*] (.+)", line):
            items = []
            while i < n and re.match(r"^[-*] (.+)", lines[i].rstrip()):
                content = re.match(r"^[-*] (.+)", lines[i].rstrip()).group(1)
                items.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": rich_text_block(content)
                    }
                })
                i += 1
            blocks.extend(items)
            continue

        if line.strip():
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": rich_text_block(line)
                }
            })

        i += 1

    return blocks

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

    try:
        response = requests.post(url, headers=HEADERS, json=data)
        return handle_response(response)
    except Exception as e:
        return {"error": f"Exception occurred during Notion page creation: {str(e)}"}

def notion_append_blocks(**body):
    page_id = body.get("page_id")
    if page_id == "root":
        page_id = ROOT_PAGE_ID
    content = body.get("content")
    if not page_id or not content:
        return {"error": "page_id and content are required."}

    blocks = parse_markdown_to_notion_blocks(content)

    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    data = {
        "children": blocks
    }

    try:
        response = requests.patch(url, headers=HEADERS, json=data)
        return handle_response(response)
    except Exception as e:
        return {"error": f"Exception occurred while appending blocks: {str(e)}"}

def notion_fetch(**params):
    page_id = params.get("page_id")
    if page_id == "root":
        page_id = ROOT_PAGE_ID
    if not page_id:
        return {"error": "page_id is required."}

    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    try:
        response = requests.get(url, headers=HEADERS)
        return handle_response(response)
    except Exception as e:
        return {"error": f"Exception during fetch: {str(e)}"}

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

    try:
        response = requests.patch(url, headers=HEADERS, json=data)
        return handle_response(response)
    except Exception as e:
        return {"error": f"Exception during update: {str(e)}"}

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

    try:
        response = requests.patch(url, headers=HEADERS, json=data)
        return handle_response(response)
    except Exception as e:
        return {"error": f"Exception during delete: {str(e)}"}

def handle_response(response):
    if response.status_code not in [200, 201]:
        return {"error": response.text, "status_code": response.status_code}
    return {"status": "success", "detail": response.json()}
